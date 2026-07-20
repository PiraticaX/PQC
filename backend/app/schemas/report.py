from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from typing import Any


class ReportCreate(BaseModel):

    title: str
    description: str | None = None
    report_type: str = "security"


class ReportResponse(BaseModel):

    id: UUID
    title: str
    description: str | None = None
    report_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    report_type: str | None = None


class ReportSummary(BaseModel):
    id: UUID
    title: str
    report_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    items: list[ReportSummary]
    total: int