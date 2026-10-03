"""Streamlit Visual Dashboard for E-Commerce Product & Niche Hunter Engine."""

import streamlit as st
import pandas as pd
from pipeline import ProductHunterPipeline
from models.schemas import ProductInput, DecisionVerdictEnum
from core.database import SessionLocal
from models.db_models import ProductRecord, EvaluationRecord

st.set_page_config(
    page_title="E-Commerce Product & Niche Hunter",
    page_icon="🏹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 0.75rem;
        border: 1px solid #334155;
        color: white;
    }
    .badge-launch {
        background-color: #16a34a;
        color: white;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-weight: bold;
    }
    .badge-watchlist {
        background-color: #d97706;
        color: white;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-weight: bold;
    }
    .badge-reject {
        background-color: #dc2626;
        color: white;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏹 E-Commerce Product & Niche Hunter Engine")
st.caption("Deterministic Unit Economics | Hard Gate Filters | Multi-Agent Moat & Risk Reasoning")

# Sidebar: Evaluation Controls
st.sidebar.header("🎯 Product Input Parameters")

presets = {
    "✨ Golden Winner: Ergonomic Bamboo Desk Organizer": {
        "title": "Ergonomic Bamboo Desk Organizer",
        "category": "office_products",
        "price": 39.99,
        "weight": 1.4,
        "length": 12.0,
        "fragility": 1,
        "search_vol": 14000,
        "revenue": 32000.0,
        "cagr": 9.2,
        "dominant_share": 24.0,
        "top3_share": 48.0,
        "comp_rating": 4.0,
        "comp_reviews": 450,
        "cogs": 6.00,
        "ship": 1.80
    },
    "🛑 Fragility Risk: Geometric Glass Terrarium": {
        "title": "Geometric Hanging Glass Terrarium",
        "category": "home_and_kitchen",
        "price": 28.50,
        "weight": 2.1,
        "length": 11.0,
        "fragility": 3,
        "search_vol": 8000,
        "revenue": 15000.0,
        "cagr": 4.0,
        "dominant_share": 30.0,
        "top3_share": 55.0,
        "comp_rating": 3.9,
        "comp_reviews": 600,
        "cogs": None,
        "ship": None
    },
    "⚠️ Low Price Trap: Standard Tri-Spinner": {
        "title": "Standard Tri-Spinner Toy",
        "category": "toys_and_games",
        "price": 8.99,
        "weight": 0.3,
        "length": 4.0,
        "fragility": 1,
        "search_vol": 5000,
        "revenue": 4000.0,
        "cagr": -22.0,
        "dominant_share": 45.0,
        "top3_share": 88.0,
        "comp_rating": 4.6,
        "comp_reviews": 4200,
        "cogs": None,
        "ship": None
    },
    "Custom Product Entry": None
}

selected_preset = st.sidebar.selectbox("Load Preset Benchmark or Custom", list(presets.keys()))
preset_data = presets[selected_preset]

if preset_data:
    title = st.sidebar.text_input("Product Title", preset_data["title"])
    category = st.sidebar.selectbox("Category", [
        "office_products", "home_and_kitchen", "beauty_and_personal_care",
        "sports_and_outdoors", "electronics_accessories", "pet_supplies",
        "toys_and_games", "tools_and_home_improvement"
    ], index=["office_products", "home_and_kitchen", "beauty_and_personal_care", "sports_and_outdoors", "electronics_accessories", "pet_supplies", "toys_and_games", "tools_and_home_improvement"].index(preset_data["category"]))
    price = st.sidebar.number_input("Retail Price ($)", value=float(preset_data["price"]), step=1.0)
    weight = st.sidebar.number_input("Weight (lbs)", value=float(preset_data["weight"]), step=0.1)
    length = st.sidebar.number_input("Longest Side (inches)", value=float(preset_data["length"]), step=0.5)
    fragility = st.sidebar.slider("Fragility Tier (1=Low, 3=Glass/Hazmat)", 1, 3, preset_data["fragility"])
    search_vol = st.sidebar.number_input("Monthly Search Volume", value=int(preset_data["search_vol"]), step=500)
    revenue = st.sidebar.number_input("Monthly Niche Revenue ($)", value=float(preset_data["revenue"]), step=1000.0)
    cagr = st.sidebar.number_input("Market CAGR (%)", value=float(preset_data["cagr"]), step=0.5)
    dominant_share = st.sidebar.slider("Dominant Brand Share (%)", 0.0, 100.0, float(preset_data["dominant_share"]))
    top3_share = st.sidebar.slider("Top 3 Brands Share (%)", 0.0, 100.0, float(preset_data["top3_share"]))
    comp_rating = st.sidebar.slider("Competitor Avg Rating", 1.0, 5.0, float(preset_data["comp_rating"]), step=0.1)
    comp_reviews = st.sidebar.number_input("Competitor Avg Reviews", value=int(preset_data["comp_reviews"]), step=50)
    cogs_override = st.sidebar.number_input("Supplier Quote COGS ($) [0 = use benchmark]", value=float(preset_data["cogs"] or 0.0), step=0.5)
    ship_override = st.sidebar.number_input("Inbound Freight Quote ($) [0 = use benchmark]", value=float(preset_data["ship"] or 0.0), step=0.5)
else:
    title = st.sidebar.text_input("Product Title", "Stainless Steel French Press")
    category = st.sidebar.selectbox("Category", [
        "home_and_kitchen", "office_products", "beauty_and_personal_care",
        "sports_and_outdoors", "electronics_accessories", "pet_supplies",
        "toys_and_games", "tools_and_home_improvement"
    ])
    price = st.sidebar.number_input("Retail Price ($)", value=34.99, step=1.0)
    weight = st.sidebar.number_input("Weight (lbs)", value=1.5, step=0.1)
    length = st.sidebar.number_input("Longest Side (inches)", value=9.0, step=0.5)
    fragility = st.sidebar.slider("Fragility Tier (1=Low, 3=Glass/Hazmat)", 1, 3, 1)
    search_vol = st.sidebar.number_input("Monthly Search Volume", value=12000, step=500)
    revenue = st.sidebar.number_input("Monthly Niche Revenue ($)", value=25000.0, step=1000.0)
    cagr = st.sidebar.number_input("Market CAGR (%)", value=7.5, step=0.5)
    dominant_share = st.sidebar.slider("Dominant Brand Share (%)", 0.0, 100.0, 25.0)
    top3_share = st.sidebar.slider("Top 3 Brands Share (%)", 0.0, 100.0, 50.0)
    comp_rating = st.sidebar.slider("Competitor Avg Rating", 1.0, 5.0, 4.1, step=0.1)
    comp_reviews = st.sidebar.number_input("Competitor Avg Reviews", value=650, step=50)
    cogs_override = st.sidebar.number_input("Supplier Quote COGS ($) [0 = use benchmark]", value=0.0, step=0.5)
    ship_override = st.sidebar.number_input("Inbound Freight Quote ($) [0 = use benchmark]", value=0.0, step=0.5)

run_eval = st.sidebar.button("🚀 Run Full Product Evaluation", use_container_width=True, type="primary")

# Execution & Display
if run_eval or "latest_dossier" in st.session_state:
    if run_eval:
        pipeline = ProductHunterPipeline(use_mock_llm=True)
        prod = ProductInput(
            title=title,
            category=category,
            retail_price_usd=price,
            shipping_weight_lbs=weight,
            longest_side_inches=length,
            fragility_tier=fragility,
            monthly_search_volume=search_vol,
            monthly_revenue_usd=revenue,
            market_cagr_pct=cagr,
            dominant_brand_share_pct=dominant_share,
            top_3_brand_share_pct=top3_share,
            competitor_avg_rating=comp_rating,
            competitor_avg_reviews=comp_reviews,
            supplier_cogs_usd=cogs_override if cogs_override > 0 else None,
            supplier_shipping_usd=ship_override if ship_override > 0 else None,
            data_sources=["marketplace_adapter", "google_trends", "reddit_nlp"]
        )
        with st.spinner("Executing Deterministic Math & Multi-Agent Reasoning Pipeline..."):
            dossier = pipeline.evaluate_product(prod)
            st.session_state["latest_dossier"] = dossier
    else:
        dossier = st.session_state["latest_dossier"]

    # Top KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if dossier.decision == DecisionVerdictEnum.LAUNCH:
            st.metric("Final Verdict", "🟢 LAUNCH")
        elif dossier.decision == DecisionVerdictEnum.WATCHLIST:
            st.metric("Final Verdict", "🟡 WATCHLIST")
        else:
            st.metric("Final Verdict", "🔴 REJECT")

    with col2:
        st.metric("Composite Score", f"{dossier.composite_score} / 100")

    with col3:
        st.metric("Net Profit Margin", f"{dossier.unit_economics.net_margin_pct}%", f"${dossier.unit_economics.net_profit_usd:.2f} / unit")

    with col4:
        st.metric("Return on Investment (ROI)", f"{dossier.unit_economics.roi_pct}%")

    st.markdown("---")

    # Layout: Left column (Unit Economics & Math), Right column (Agent Reasoning)
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("💰 Unit Economics & Fee Breakdown")
        econ = dossier.unit_economics
        
        econ_df = pd.DataFrame({
            "Cost Element": [
                "Retail Target Price",
                "Landed COGS (Inventory)",
                "Inbound Freight",
                "Amazon Referral Fee (15%)",
                "Amazon FBA Fulfillment Fee",
                "Target PPC / Ad CAC",
                "Returns Loss Reserve",
                "Total Costs",
                "Net Profit / Unit"
            ],
            "Amount ($)": [
                f"${econ.retail_price_usd:.2f}",
                f"${econ.cogs_usd:.2f}",
                f"${econ.shipping_to_warehouse_usd:.2f}",
                f"${econ.amazon_referral_fee_usd:.2f}",
                f"${econ.amazon_fba_fee_usd:.2f}",
                f"${econ.estimated_ad_spend_usd:.2f}",
                f"${econ.estimated_returns_loss_usd:.2f}",
                f"${econ.total_costs_usd:.2f}",
                f"${econ.net_profit_usd:.2f}"
            ]
        })
        st.table(econ_df)

        st.subheader("🛡️ Hard Gate Filter Audit")
        gate_records = []
        for g in dossier.gate_report.details:
            status = "✅ PASS" if g.passed else "❌ FAIL"
            gate_records.append({
                "Gate Name": g.gate_name,
                "Status": status,
                "Actual": str(g.actual_value),
                "Threshold": str(g.threshold)
            })
        st.dataframe(pd.DataFrame(gate_records), use_container_width=True, hide_index=True)

    with right_col:
        st.subheader("📊 6-Dimensional Score Breakdown")
        scores_df = pd.DataFrame({
            "Dimension": list(dossier.dimension_scores.keys()),
            "Score (0-100)": list(dossier.dimension_scores.values())
        })
        st.bar_chart(scores_df.set_index("Dimension"), use_container_width=True)

        st.subheader("🧠 Multi-Agent Qualitative Insights")
        
        if dossier.pain_point_report:
            with st.expander(f"⚠️ A1: Customer Pain-Points (Intensity: {dossier.pain_point_report.pain_point_intensity}/10)", expanded=True):
                for p in dossier.pain_point_report.top_pain_points:
                    st.write(f"- 🔴 **{p}**")
                st.caption("Unmet Needs: " + ", ".join(dossier.pain_point_report.unmet_customer_needs))

        if dossier.differentiation_report:
            with st.expander(f"💡 A2: Moat & Upgrades (Moat Score: {dossier.differentiation_report.moat_strength}/10)", expanded=True):
                for u in dossier.differentiation_report.proposed_upgrades:
                    st.write(f"- 🟢 {u}")
                st.info(f"**Defensibility:** {dossier.differentiation_report.defensibility_notes}")

        if dossier.critic_report:
            with st.expander(f"🛑 A3: Critic Risk Audit (Severity: {dossier.critic_report.severity_level.value})", expanded=True):
                for f in dossier.critic_report.failure_modes:
                    st.write(f"- ⚠️ {f}")
                if dossier.critic_report.critical_flaw_summary:
                    st.error(dossier.critic_report.critical_flaw_summary)

        st.success(f"**Executive Summary:** {dossier.executive_summary}")
else:
    st.info("👈 Select a preset product or customize the parameters on the sidebar, then click **'Run Full Product Evaluation'**.")
