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
def get_trending_niches():
    niches = [
        {
            "rank": "01",
            "icon": "🧊",
            "keyword": "Ice Roller",
            "title": "Cryotherapy Silicone Facial Ice Roller",
            "category": "Beauty & Personal Care",
            "search_volume": 32000,
            "monthly_revenue": 65000,
            "cagr": 14.5,
            "competition": "Low",
            "net_margin": 39.7,
            "verdict": "LAUNCH"
        },
        {
            "rank": "02",
            "icon": "🍵",
            "keyword": "Matcha Whisk",
            "title": "Traditional Bamboo Matcha Whisk & Scoop Set",
            "category": "Home & Kitchen",
            "search_volume": 24000,
            "monthly_revenue": 52000,
            "cagr": 12.0,
            "competition": "Low",
            "net_margin": 39.7,
            "verdict": "LAUNCH"
        },
        {
            "rank": "03",
            "icon": "📱",
            "keyword": "MagSafe Stand",
            "title": "Foldable Aluminum MagSafe Desk Stand",
            "category": "Electronics & Accessories",
            "search_volume": 45000,
            "monthly_revenue": 98000,
            "cagr": 18.5,
            "competition": "Moderate",
            "net_margin": 34.8,
            "verdict": "LAUNCH"
        },
        {
            "rank": "04",
            "icon": "🏋️",
            "keyword": "Posture Corrector",
            "title": "Breathable Ergonomic Posture Corrector Brace",
            "category": "Sports & Outdoors",
            "search_volume": 38000,
            "monthly_revenue": 76000,
            "cagr": 10.2,
            "competition": "Moderate",
            "net_margin": 32.4,
            "verdict": "LAUNCH"
        },
        {
            "rank": "05",
            "icon": "📁",
            "keyword": "Bamboo Desk Organizer",
            "title": "Ergonomic Bamboo Desk Organizer",
            "category": "Office Products",
            "search_volume": 16000,
            "monthly_revenue": 34000,
            "cagr": 9.2,
            "competition": "Low",
            "net_margin": 30.1,
            "verdict": "LAUNCH"
        },
        {
            "rank": "06",
            "icon": "☕",
            "keyword": "French Press",
            "title": "Double-Wall Stainless French Press Brewer",
            "category": "Home & Kitchen",
            "search_volume": 28000,
            "monthly_revenue": 60000,
            "cagr": 7.8,
            "competition": "Moderate",
            "net_margin": 33.5,
            "verdict": "LAUNCH"
        },
        {
            "rank": "07",
            "icon": "🧘",
            "keyword": "Acupressure Mat",
            "title": "Acupressure Mat & Ergonomic Neck Pillow Set",
            "category": "Sports & Wellness",
            "search_volume": 21000,
            "monthly_revenue": 48000,
            "cagr": 15.2,
            "competition": "Low",
            "net_margin": 35.0,
            "verdict": "LAUNCH"
        },
        {
            "rank": "08",
            "icon": "💡",
            "keyword": "Sunrise Alarm Clock",
            "title": "Smart Sunrise Simulation Wake-Up Light",
            "category": "Smart Home Electronics",
            "search_volume": 50000,
            "monthly_revenue": 120000,
            "cagr": 22.0,
            "competition": "High",
            "net_margin": 28.0,
            "verdict": "WATCHLIST"
        }
    ]
    return {"niches": niches}


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
