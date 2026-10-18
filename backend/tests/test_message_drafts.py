from types import SimpleNamespace

from app.api.routes.message_drafts import generate_content


def test_generated_linkedin_draft_uses_reviewed_context() -> None:
    user = SimpleNamespace(
        email="student@example.com",
        profile=SimpleNamespace(school="State University", major="Computer Science"),
    )
    contact = SimpleNamespace(
        name="Taylor Recruiter",
        company_name="Acme Labs",
        relationship_reason="University alumni",
    )
    opportunity = SimpleNamespace(title="Software Engineer Intern", company_name="Acme Labs")

    subject, body = generate_content("linkedin", user, contact, opportunity)

    assert subject is None
    assert "Taylor Recruiter" in body
    assert "State University" in body
    assert "Software Engineer Intern" in body
    assert "university alumni" in body.lower()
    assert "review" not in body.lower()
