from datetime import datetime
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from services.lead_service import (
    analyze_lead_for_lead,
    create_lead,
    get_lead,
    get_leads,
    update_status,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="ITоднушка LeadFlow",
    description="Система обработки клиентских заявок",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class LeadCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    company: str | None = Field(
        default=None,
        max_length=200,
    )

    contact: str = Field(
        min_length=3,
        max_length=200,
    )

    message: str = Field(
        min_length=10,
        max_length=5000,
    )

    budget: str | None = Field(
        default=None,
        max_length=100,
    )


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    name: str
    company: str | None
    contact: str
    message: str
    budget: str | None
    status: LeadStatus
    ai_status: str
    ai_category: str | None
    ai_priority: str | None
    ai_features: str | None
    ai_estimate: str | None


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "project": "ITоднушка LeadFlow",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post(
    "/leads",
    response_model=LeadResponse,
)
def create_lead_endpoint(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
):
    return create_lead(
        db=db,
        name=lead_data.name,
        company=lead_data.company,
        contact=lead_data.contact,
        message=lead_data.message,
        budget=lead_data.budget,
    )


@app.get(
    "/leads",
    response_model=list[LeadResponse],
)
def get_leads_endpoint(
    db: Session = Depends(get_db),
):
    return get_leads(db)


@app.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
)
def get_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = get_lead(db, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    return lead

@app.post(
    "/leads/{lead_id}/analyze",
    response_model=LeadResponse,
)
def analyze_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
):
    lead = get_lead(db, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    analyze_lead_for_lead(
        db=db,
        lead=lead,
    )

    return lead
@app.patch(
    "/leads/{lead_id}/status",
    response_model=LeadResponse,
)
def update_lead_status(
    lead_id: int,
    status_data: LeadStatusUpdate,
    db: Session = Depends(get_db),
):
    lead = get_lead(db, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    return update_status(
        db=db,
        lead=lead,
        status=status_data.status,
    )