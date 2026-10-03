# 🚀 E-Commerce Product & Niche Hunter Engine

An enterprise-grade, deterministic multi-agent system designed for automated e-commerce niche research, unit economics validation, hard-gated risk filtering, and AI-driven moat engineering.

---

## 🏛️ Core Architectural Principle

> **"Code = Math & Deterministic Gates, LLM = Deep Reasoning & Qualitative Analysis"**

- **Deterministic Hard Gates First**: Unit economics, weight, dimensions, fragility, and market monopoly are evaluated in code first. Products failing basic investment criteria are rejected immediately with zero LLM token waste.
- **Single Source of Truth**: All thresholds and weights are centralized in YAML configuration files (`config/`).
- **Portable Persistence**: Works out-of-the-box with local SQLite (`data/hunter.db`) for rapid development and seamlessly switches to PostgreSQL in production.
- **Dual Inference Engine**: Instant deterministic mock fallbacks for testing + live Google Gemini 2.5 Flash / Pro integration.

---

## 📂 Project Structure

```
├── config/                     # Single Source of Truth Configurations
│   ├── gates.yaml              # Deterministic Hard Gates thresholds
│   ├── scoring.yaml            # Composite scoring weights & thresholds
│   ├── normalization.yaml      # Piecewise linear / logarithmic curves (0-100)
│   └── cogs_benchmark.yaml     # Pre-gate category COGS benchmark ratios
├── core/                       # Foundation & Infrastructure
│   ├── config_loader.py        # Typed Pydantic config registry
│   └── database.py             # Portable SQLAlchemy connection factory
├── models/                     # Data Contracts & Schemas
│   ├── schemas.py              # Pydantic validation models
│   └── db_models.py            # SQLAlchemy database ORM models
├── engine/                     # Deterministic Math & Decision Logic
│   ├── profit_calculator.py    # FBA fees, referral fees, ad spend, net margin, ROI
│   ├── normalizer.py           # Mathematical 0-100 curve normalization
│   ├── gate_evaluator.py       # Hard gate filter evaluator
│   └── decision_engine.py      # Composite scoring, risk caps, verdict engine
├── adapters/                   # Data Providers & Scrapers
│   ├── base.py                 # Abstract adapter interfaces
│   ├── mock_adapter.py         # Deterministic mock provider
│   ├── keepa_adapter.py        # Keepa API marketplace ingestion
│   ├── reddit_review_adapter.py# Public forum & review text harvester (with cache)
│   └── trend_adapter.py        # Google Trends momentum extractor (with cache)
├── agents/                     # Multi-Agent Qualitative Reasoning
│   ├── base_agent.py           # Gemini SDK wrapper + Mock LLM fallback
│   ├── pain_point_agent.py     # A1: Customer pain-point & complaint hunter
│   ├── differentiation_agent.py# A2: Moat & industrial upgrade designer
│   └── critic_agent.py         # A3: Devil's advocate risk & legal auditor
├── tests/                      # 38 Automated Pytest Test Scenarios
│   ├── test_config.py          # Configuration consistency tests
│   ├── test_schemas.py         # Pydantic schema validation tests
│   ├── test_database.py        # Database CRUD & ORM tests
│   ├── test_profit_engine.py   # Unit economics & FBA calculation tests
│   ├── test_normalizer.py      # Normalization curves tests
│   ├── test_gates.py           # 15 Edge case & hard gate tests
│   ├── test_adapters.py        # Ingestion adapter tests
│   └── test_pipeline.py        # End-to-end evaluation & decision matrix tests
├── pipeline.py                 # Master evaluation orchestrator
├── main.py                     # CLI Entrypoint
└── requirements.txt            # Python dependencies
```

---

## ⚡ Quick Start

### 1. Run Automated Test Suite
```bash
pytest -v
```
*(All 38 test cases pass deterministically)*

### 2. Run CLI Evaluation
```bash
python main.py --title "Bamboo Desk Organizer" --price 38.99 --category "office_products"
```

---

## 🛡️ Decision Matrix & Risk Capping Rules

| Condition | Verdict |
| :--- | :--- |
| Any Hard Gate Fails (Margin < 30%, Weight > 4.5 lbs, Monopoly > 65%) | **🔴 REJECT** (Fast exit, 0 LLM cost) |
| Critic Agent flags `CRITICAL` risk (Choking hazard, patent violation) | **🔴 REJECT** (Auto-veto) |
| Critic Agent flags `HIGH` risk | **🟡 WATCHLIST** (Strict cap, cannot be LAUNCH) |
| Composite Score $\ge 70.0$ AND zero critical/high risks | **🟢 LAUNCH** |
| Composite Score $\ge 55.0$ | **🟡 WATCHLIST** |
| Composite Score $< 55.0$ | **🔴 REJECT** |
