import json

import pytest

from app.core.config import Settings
from app.db.models import JobOpportunity
from app.services import job_import
from app.services.recommendations import find_recommendations


class FakeResponse:
    status_code = 200
    headers = {"content-type": "text/html; charset=utf-8"}
    content = b"<html>"
    text = """
    <html><head>
      <title>Fallback title</title>
      <script type="application/ld+json">
      {"@type":"JobPosting","title":"Backend Intern","hiringOrganization":{"name":"Example Labs"},"jobLocation":{"address":{"addressLocality":"Seattle","addressRegion":"WA"}},"description":"Build APIs."}
      </script>
    </head></html>
    """

    def json(self):
        return {
            "output_text": json.dumps(
                {
                    "recommendations": [
                        {
                            "name": "Alex Example",
                            "job_title": "Engineering Manager",
                            "company_name": "Example Labs",
                            "profile_url": "https://www.linkedin.com/in/alex-example",
                            "source_url": "https://example.com/team/alex-example",
                            "source_title": "Example Labs team",
                            "connection_reason": "Works on the team hiring for this role.",
                            "evidence": "The public team page lists Alex as an Engineering Manager.",
                            "confidence": "high",
                        }
                    ]
                }
            )
        }


class FakeHttpClient:
    def __init__(self, **kwargs):  # noqa: ANN003
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args):  # noqa: ANN002, ANN003
        return None

    def get(self, url):  # noqa: ANN001
        return FakeResponse()

    def post(self, url, headers, json):  # noqa: ANN001, A002
        return FakeResponse()


def test_job_import_extracts_public_json_ld(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(job_import, "_public_host", lambda hostname: True)
    monkeypatch.setattr(job_import.httpx, "Client", FakeHttpClient)

    imported = job_import.import_job_from_url("https://jobs.example.com/backend-intern")

    assert imported.title == "Backend Intern"
    assert imported.company_name == "Example Labs"
    assert imported.location == "Seattle, WA"
    assert imported.description == "Build APIs."


def test_job_import_rejects_local_urls() -> None:
    with pytest.raises(ValueError, match="Private or local"):
        job_import.validate_public_url("http://127.0.0.1/job")


def test_recommendation_service_parses_structured_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.recommendations.httpx.Client", FakeHttpClient)
    opportunity = JobOpportunity(title="Backend Intern", company_name="Example Labs", description="Build APIs.")
    settings = Settings(openai_api_key="test-key", openai_model="test-model")

    recommendations = find_recommendations(opportunity, None, settings)

    assert recommendations[0]["name"] == "Alex Example"
    assert recommendations[0]["source_url"] == "https://example.com/team/alex-example"
