"""SQLAlchemy ORM models for portable SQLite and PostgreSQL persistence."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)



class ProductRecord(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    retail_price_usd = Column(Float, nullable=False)
    shipping_weight_lbs = Column(Float, nullable=False)
    monthly_search_volume = Column(Integer, default=0)
    monthly_revenue_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    # Raw Payload Snapshot
    raw_input = Column(JSON, nullable=True)


class EvaluationRecord(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), nullable=False, index=True)
    decision = Column(String(20), nullable=False, index=True)  # LAUNCH, WATCHLIST, REJECT
    composite_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)

    # Detailed Sub-Scores & Reports (JSON format)
    dimension_scores = Column(JSON, nullable=True)
    unit_economics = Column(JSON, nullable=True)
    gate_report = Column(JSON, nullable=True)
    pain_point_report = Column(JSON, nullable=True)
    differentiation_report = Column(JSON, nullable=True)
    critic_report = Column(JSON, nullable=True)
    
    executive_summary = Column(Text, nullable=True)
    risk_warnings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)
