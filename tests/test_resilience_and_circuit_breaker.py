"""
Comprehensive Resilience, Circuit Breaker, Idempotency, and Adversarial Guard Tests.
Tests failure recovery, permission isolation, circuit breaker tripping, and idempotency guarantees.
"""

import pytest
from core.policy_engine import policy_engine, ActionType, AgentRole
from core.circuit_breaker import circuit_breaker, SubsystemEnum, CircuitStatus
from core.state_machine import state_machine, ProductLifecycleState
from engine.profit_calculator import calculate_unit_economics
from models.schemas import ProductInput


def test_idempotency_prevents_duplicate_publish_action():
    """Test that retrying or executing the same action key is blocked to prevent duplication."""
    key = "PUBLISH_PRODUCT:PROD-ICE-ROLLER-001:V1"
    
    # First execution should pass
    res1 = policy_engine.evaluate_action_permission(
        agent_role=AgentRole.PUBLISHING_OPERATOR,
        action=ActionType.PUBLISH_PRODUCT,
        idempotency_key=key
    )
    assert res1.is_permitted is True
    policy_engine.record_action_executed(key, ActionType.PUBLISH_PRODUCT)

    # Second execution with same key MUST be blocked immediately
    res2 = policy_engine.evaluate_action_permission(
        agent_role=AgentRole.PUBLISHING_OPERATOR,
        action=ActionType.PUBLISH_PRODUCT,
        idempotency_key=key
    )
    assert res2.is_permitted is False
    assert "IDEMPOTENCY BLOCKED" in res2.reason


def test_permission_boundary_blocks_unauthorized_agent_actions():
    """Test that a Product / Research Agent CANNOT publish or spend ad budget."""
    key = "UNAUTHORIZED_ATTEMPT:PROD-002"
    
    # Pain Point Hunter attempting to publish -> DENIED
    res = policy_engine.evaluate_action_permission(
        agent_role=AgentRole.PAIN_POINT_HUNTER,
        action=ActionType.PUBLISH_PRODUCT,
        idempotency_key=key
    )
    assert res.is_permitted is False
    assert "POLICY DENIAL" in res.reason


def test_circuit_breaker_trips_on_consecutive_api_outages():
    """Test that repeated API or scraper failures trip the circuit breaker and isolate the subsystem."""
    cb = circuit_breaker
    cb.reset_subsystem(SubsystemEnum.MARKET_SCRAPING)
    
    assert cb.check_subsystem_available(SubsystemEnum.MARKET_SCRAPING) is True

    # Simulate 5 consecutive connection timeouts
    for i in range(5):
        trip = cb.record_failure(SubsystemEnum.MARKET_SCRAPING, "504 Gateway Timeout")

    # Subsystem MUST now be OPEN (tripped / paused)
    assert cb.check_subsystem_available(SubsystemEnum.MARKET_SCRAPING) is False
    assert cb.subsystem_status[SubsystemEnum.MARKET_SCRAPING] == CircuitStatus.OPEN

    # Reset
    cb.reset_subsystem(SubsystemEnum.MARKET_SCRAPING)
    assert cb.check_subsystem_available(SubsystemEnum.MARKET_SCRAPING) is True


def test_global_kill_switch_halts_all_subsystems():
    """Test that emergency global kill switch immediately halts all autonomous operations."""
    cb = circuit_breaker
    cb.trigger_kill_switch(reason="Emergency Admin Halt")
    
    assert cb.check_subsystem_available(SubsystemEnum.PUBLISHING_ENGINE) is False
    assert cb.check_subsystem_available(SubsystemEnum.AD_SPEND_ENGINE) is False
    assert cb.check_subsystem_available(SubsystemEnum.MARKET_SCRAPING) is False
    
    # Restore normal state for subsequent tests
    cb.is_global_kill_switch_active = False
    for s in SubsystemEnum:
        cb.reset_subsystem(s)


def test_state_machine_blocks_unlawful_lifecycle_jumps():
    """Test that a product cannot jump directly from DISCOVERED to PUBLISHED without gates."""
    sm = state_machine
    
    # Unlawful jump from DISCOVERED straight to PUBLISHED
    res = sm.can_transition(
        current_state=ProductLifecycleState.DISCOVERED,
        target_state=ProductLifecycleState.PUBLISHED
    )
    assert res.passed_guard is False
    assert "ILLEGAL TRANSITION" in res.guard_reason

    # Lawful step with failing prerequisite checks
    res_prereq = sm.can_transition(
        current_state=ProductLifecycleState.VALIDATING,
        target_state=ProductLifecycleState.ECONOMIC_REVIEW,
        prerequisite_checks={"demand_verified": True, "hard_gates_passed": False}
    )
    assert res_prereq.passed_guard is False
    assert "GUARD FAILURE" in res_prereq.guard_reason


def test_unit_economics_exact_reproducibility():
    """Verify exact formula guarantees across multiple runs without state drift."""
    prod = ProductInput(
        title="Test Private Label Product",
        category="beauty_and_personal_care",
        retail_price_usd=24.99,
        supplier_cogs_usd=4.00,
        supplier_shipping_usd=1.00,
        shipping_weight_lbs=0.8,
        longest_side_inches=8.0,
        target_ad_spend_pct=12.0048
    )
    econ = calculate_unit_economics(prod)
    assert econ.contribution_profit_usd == 9.38
    assert econ.contribution_margin_pct == 37.54
    assert econ.operating_profit_usd == 9.06
    assert econ.net_profit_usd == 7.70
    assert econ.scenario_analysis.worst_case_survival_status == "SURVIVES"
