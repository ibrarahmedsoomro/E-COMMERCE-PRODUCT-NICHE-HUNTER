"""Tests for Database Operations and ORM Persistence."""

import pytest
from core.database import init_db, SessionLocal, engine, Base
from models.db_models import ProductRecord, EvaluationRecord


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_insert_and_retrieve_product_and_evaluation():
    session = SessionLocal()
    
    # 1. Insert product
    product = ProductRecord(
        title="Silicone Pastry Mat",
        category="home_and_kitchen",
        retail_price_usd=24.99,
        shipping_weight_lbs=0.8,
        monthly_search_volume=8500,
        monthly_revenue_usd=18000.0,
        raw_input={"tags": ["baking", "silicone", "kitchen"]}
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    assert product.id is not None
    assert len(product.id) == 36  # UUID length

    # 2. Insert evaluation
    eval_rec = EvaluationRecord(
        product_id=product.id,
        decision="LAUNCH",
        composite_score=82.5,
        confidence_score=90.0,
        dimension_scores={"profitability": 85.0, "demand_traction": 80.0},
        unit_economics={"net_margin_pct": 26.5},
        executive_summary="Solid margins and high demand with weak competitor durability."
    )
    session.add(eval_rec)
    session.commit()
    session.refresh(eval_rec)

    # 3. Query back
    retrieved = session.query(EvaluationRecord).filter_by(product_id=product.id).first()
    assert retrieved is not None
    assert retrieved.decision == "LAUNCH"
    assert retrieved.composite_score == 82.5
    assert retrieved.dimension_scores["profitability"] == 85.0

    session.close()
