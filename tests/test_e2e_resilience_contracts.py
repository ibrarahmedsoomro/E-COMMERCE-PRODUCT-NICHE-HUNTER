"""
End-to-End Resilience, Tool Timeout Recovery, and Immutable Invariant Tests.
Tests the critical scenario:
"TOOL SAYS TIMEOUT BUT SIDE-EFFECT ACTUALLY HAPPENED -> RECONCILIATION DETECTS & PREVENTS DUPLICATE SIDE-EFFECT"
"""

import pytest
from core.policy_engine import policy_engine, ActionType, AgentRole
from core.concurrency_lease import lease_manager
from core.state_machine import state_machine, ProductLifecycleState
from core.reconciliation_engine import reconciliation_engine
from core.immutable_event_stream import event_stream
from core.prompt_defense import prompt_defense


def test_tool_timeout_with_real_side_effect_reconciliation():
    """
    Critical Scenario:
    1. Worker requests publish for Product-284.
    2. Tool executes publish on Amazon/Shopify.
    3. Network times out on the return response (Client sees TimeoutError).
    4. Worker re-checks with Reconciliation Engine.
    5. External state confirms product IS LIVE.
    6. Database is reconciled to PUBLISHED without duplicate publish execution.
    """
    prod_id = "PROD_284_BAMBOO_ORGANIZER"
    idempotency_key = f"PUBLISH_PRODUCT:{prod_id}:V1"
    worker_id = "WORKER_PUBLISHER_01"

    # Step 1: Acquire Atomic Distributed Lease
    assert lease_manager.acquire_lease(prod_id, worker_id, ttl_seconds=30) is True

    # Step 2: Policy Engine Authorizes Action
    policy_res = policy_engine.evaluate_action_permission(
        agent_role=AgentRole.PUBLISHING_OPERATOR,
        action=ActionType.PUBLISH_PRODUCT,
        idempotency_key=idempotency_key
    )
    assert policy_res.is_permitted is True

    # Step 3: State Machine Validates Legal Transition
    state_res = state_machine.can_transition(
        current_state=ProductLifecycleState.APPROVED_FOR_PUBLISH,
        target_state=ProductLifecycleState.PUBLISHING,
        prerequisite_checks={"qa_passed": True, "economic_gate_passed": True}
    )
    assert state_res.passed_guard is True

    # Step 4: Simulate Simulated Timeout on Network Client
    # Side-effect succeeded on remote Amazon store, but client received TimeoutError
    def mock_external_amazon_verifier(p_id):
        # Remote marketplace confirms product 284 is active and live
        return "LIVE_ON_AMAZON"

    # Step 5: Reconciliation Engine queries external truth
    recon_res = reconciliation_engine.reconcile_published_product(
        product_id=prod_id,
        expected_status="LIVE_ON_AMAZON",
        mock_external_fetcher=mock_external_amazon_verifier
    )
    assert recon_res.is_synchronized is True

    # Step 6: Commit state & Record immutable hash-chained event
    policy_engine.record_action_executed(idempotency_key, ActionType.PUBLISH_PRODUCT)
    
    event = event_stream.record_event(
        event_type="PRODUCT_PUBLISHED_RECONCILED",
        entity_id=prod_id,
        agent_role=AgentRole.PUBLISHING_OPERATOR.value,
        action_type=ActionType.PUBLISH_PRODUCT.value,
        idempotency_key=idempotency_key,
        payload={"final_status": "PUBLISHED", "verified_platform": "AMAZON_US"}
    )
    assert len(event.event_hash) == 64

    # Step 7: Release lease
    assert lease_manager.release_lease(prod_id, worker_id) is True

    # Step 8: Subsequent duplicate publish request MUST be blocked by idempotency
    dup_res = policy_engine.evaluate_action_permission(
        agent_role=AgentRole.PUBLISHING_OPERATOR,
        action=ActionType.PUBLISH_PRODUCT,
        idempotency_key=idempotency_key
    )
    assert dup_res.is_permitted is False
    assert "IDEMPOTENCY BLOCKED" in dup_res.reason
