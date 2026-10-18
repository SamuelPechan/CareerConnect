from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_saved_opportunities: int
    total_applications: int
    applications_by_status: dict[str, int]
    total_interviews: int
    total_offers: int
    total_contacts: int
    upcoming_follow_ups: int
    overdue_follow_ups: int
    total_interactions: int
    total_discovery_links: int
    reviewed_discovery_links: int
    applications_with_contacts: int
    applications_without_contacts: int
    interview_rate: float | None
    offer_rate: float | None
