import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

MAX_RESPONSE_BYTES = 2_000_000
MAX_REDIRECTS = 3
REQUEST_TIMEOUT_SECONDS = 8.0


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.json_ld: list[object] = []
        self._in_title = False
        self._in_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            key = attributes.get("property") or attributes.get("name")
            content = attributes.get("content")
            if key and content:
                self.meta[key.lower()] = content.strip()
        if tag.lower() == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        if tag.lower() == "script" and self._in_json_ld:
            self._in_json_ld = False
            raw = "".join(self._json_ld_parts).strip()
            if not raw:
                return
            try:
                self.json_ld.append(json.loads(raw))
            except json.JSONDecodeError:
                return

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._json_ld_parts.append(data)


@dataclass(frozen=True)
class ImportedJob:
    title: str
    company_name: str
    location: str | None
    description: str | None
    source_platform: str
    job_url: str


def _clean_text(value: object) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _public_host(hostname: str) -> bool:
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(hostname, None)}
    except socket.gaierror as exc:
        raise ValueError("The job URL host could not be resolved") from exc
    for address in addresses:
        parsed = ipaddress.ip_address(address)
        if parsed.is_private or parsed.is_loopback or parsed.is_link_local or parsed.is_multicast or parsed.is_unspecified:
            return False
    return True


def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public http:// or https:// job URL")
    if parsed.port and parsed.port not in {80, 443}:
        raise ValueError("The job URL must use a standard web port")
    if not _public_host(parsed.hostname):
        raise ValueError("Private or local job URLs are not allowed")
    return value


def _iter_json_nodes(value: object):
    if isinstance(value, list):
        for item in value:
            yield from _iter_json_nodes(item)
    elif isinstance(value, dict):
        yield value
        for item in value.get("@graph", []) if isinstance(value.get("@graph"), list) else []:
            yield from _iter_json_nodes(item)


def _job_posting(parser: _MetadataParser) -> dict[str, object]:
    for value in parser.json_ld:
        for node in _iter_json_nodes(value):
            node_type = node.get("@type")
            types = node_type if isinstance(node_type, list) else [node_type]
            if any(str(item).lower() == "jobposting" for item in types):
                return node
    return {}


def _organization_name(value: object) -> str:
    if isinstance(value, dict):
        return _clean_text(value.get("name"))
    return _clean_text(value)


def _location_name(value: object) -> str | None:
    locations = value if isinstance(value, list) else [value]
    names: list[str] = []
    for location in locations:
        if not isinstance(location, dict):
            continue
        address = location.get("address", location)
        if isinstance(address, dict):
            parts = [address.get("addressLocality"), address.get("addressRegion"), address.get("addressCountry")]
            names.append(", ".join(_clean_text(part) for part in parts if _clean_text(part)))
        else:
            names.append(_clean_text(address))
    result = "; ".join(name for name in names if name)
    return result or None


def _source_platform(hostname: str) -> str:
    host = hostname.lower()
    known = {
        "linkedin.com": "LinkedIn",
        "indeed.com": "Indeed",
        "greenhouse.io": "Greenhouse",
        "lever.co": "Lever",
        "myworkdayjobs.com": "Workday",
        "ashbyhq.com": "Ashby",
        "workable.com": "Workable",
        "smartrecruiters.com": "SmartRecruiters",
    }
    for domain, label in known.items():
        if host == domain or host.endswith(f".{domain}"):
            return label
    return hostname


def import_job_from_url(job_url: str) -> ImportedJob:
    current_url = validate_public_url(job_url)
    response: httpx.Response | None = None
    with httpx.Client(
        timeout=REQUEST_TIMEOUT_SECONDS,
        follow_redirects=False,
        trust_env=False,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "CareerConnect/1.0 (public job metadata importer)",
        },
    ) as client:
        for _ in range(MAX_REDIRECTS + 1):
            response = client.get(current_url)
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise ValueError("The job site returned an invalid redirect")
                current_url = validate_public_url(urljoin(current_url, location))
                continue
            break
    if response is None or response.status_code >= 400:
        raise ValueError("The job page could not be read. Try a public job posting URL.")
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("The job page is too large to import safely")
    content_type = response.headers.get("content-type", "").lower()
    if content_type and "html" not in content_type:
        raise ValueError("That URL does not appear to be a public HTML job posting")

    parser = _MetadataParser()
    parser.feed(response.text[:MAX_RESPONSE_BYTES])
    job = _job_posting(parser)
    title = _clean_text(job.get("title")) or parser.meta.get("og:title", "") or _clean_text("".join(parser.title_parts))
    company = _organization_name(job.get("hiringOrganization")) or parser.meta.get("author", "")
    description = _clean_text(job.get("description")) or parser.meta.get("og:description") or parser.meta.get("description")
    location = _location_name(job.get("jobLocation"))
    if not title or not company:
        raise ValueError("CareerConnect could not confidently identify the job title and company from that page")
    return ImportedJob(
        title=title[:250],
        company_name=company[:250],
        location=location[:250] if location else None,
        description=description[:20000] if description else None,
        source_platform=_source_platform(urlparse(current_url).hostname or "job site"),
        job_url=current_url,
    )
