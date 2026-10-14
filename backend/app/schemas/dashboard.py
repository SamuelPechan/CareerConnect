from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_saved_opportunities: int
    total_applications: int
    applications_by_status: dict[str, int]
    total_interviews: int
    total_offers: int
