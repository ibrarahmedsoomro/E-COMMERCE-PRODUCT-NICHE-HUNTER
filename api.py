"""FastAPI Backend Server for Product Hunter 3D Frontend."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import ProductHunterPipeline
from models.schemas import ProductInput, FinalEvaluationDossier, DecisionVerdictEnum
from core.database import SessionLocal
from models.db_models import ProductRecord, EvaluationRecord

app = FastAPI(title="Product Hunter 3D Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


pipeline = ProductHunterPipeline(use_mock_llm=True)
PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    return FileResponse(
        str(index_file),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/report")
def serve_report():
    report_file = FRONTEND_DIR / "report.html"
    return FileResponse(
        str(report_file),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


class EvaluateRequest(BaseModel):
    title: str
    category: str = "office_products"
    retail_price_usd: float
    shipping_weight_lbs: float = 1.0
    longest_side_inches: float = 12.0
    fragility_tier: int = 1
    monthly_search_volume: int = 10000
    monthly_revenue_usd: float = 25000.0
    market_cagr_pct: float = 8.0
    dominant_brand_share_pct: float = 25.0
    top_3_brand_share_pct: float = 50.0
    competitor_avg_rating: float = 4.0
    competitor_avg_reviews: int = 500
    supplier_cogs_usd: Optional[float] = None
    supplier_shipping_usd: Optional[float] = None


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Product Hunter 3D Engine"}


@app.post("/api/evaluate", response_model=FinalEvaluationDossier)
def evaluate_product(req: EvaluateRequest):
    try:
        product = ProductInput(
            title=req.title,
            category=req.category,
            retail_price_usd=req.retail_price_usd,
            shipping_weight_lbs=req.shipping_weight_lbs,
            longest_side_inches=req.longest_side_inches,
            fragility_tier=req.fragility_tier,
            monthly_search_volume=req.monthly_search_volume,
            monthly_revenue_usd=req.monthly_revenue_usd,
            market_cagr_pct=req.market_cagr_pct,
            dominant_brand_share_pct=req.dominant_brand_share_pct,
            top_3_brand_share_pct=req.top_3_brand_share_pct,
            competitor_avg_rating=req.competitor_avg_rating,
            competitor_avg_reviews=req.competitor_avg_reviews,
            supplier_cogs_usd=req.supplier_cogs_usd,
            supplier_shipping_usd=req.supplier_shipping_usd,
            data_sources=["marketplace_adapter", "google_trends", "reddit_discussions"]
        )
        dossier = pipeline.evaluate_product(product)
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AutoHuntRequest(BaseModel):
    keyword: str


@app.post("/api/auto-hunt", response_model=FinalEvaluationDossier)
def auto_hunt_keyword(req: AutoHuntRequest):
    try:
        from engine.autonomous_hunter import autonomous_hunter
        dossier = autonomous_hunter.hunt(req.keyword)
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending-niches")
def get_trending_niches(
    category: str = "all",
    refresh: bool = False,
    min_margin: float = 25.0,
    sort_by: str = "profit"
):
    from engine.live_niche_discovery import live_discovery_service
    niches = live_discovery_service.discover(
        category=category,
        refresh=refresh,
        min_margin=min_margin,
        sort_by=sort_by
    )
    categories = live_discovery_service.get_categories()
    return {"niches": niches, "categories": categories, "count": len(niches)}


@app.get("/api/categories")
def get_categories():
    from engine.live_niche_discovery import live_discovery_service
    return {"categories": live_discovery_service.get_categories()}


@app.get("/api/history")
def get_history(limit: int = 10):
    session = SessionLocal()
    try:
        evals = session.query(EvaluationRecord).order_by(EvaluationRecord.created_at.desc()).limit(limit).all()
        results = []
        for ev in evals:
            results.append({
                "id": ev.id,
                "product_id": ev.product_id,
                "decision": ev.decision,
                "composite_score": ev.composite_score,
                "confidence_score": ev.confidence_score,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "executive_summary": ev.executive_summary
            })
        return results
    finally:
        session.close()


# Mount static frontend
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
