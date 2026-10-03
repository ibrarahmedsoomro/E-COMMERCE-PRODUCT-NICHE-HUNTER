"""
18-Stage Production Product Lifecycle State Machine with Deterministic Guardrails.
Enforces that a product cannot silently advance without prerequisite validations.
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ProductLifecycleState(str, Enum):
    DISCOVERED = "DISCOVERED"
    RESEARCHING = "RESEARCHING"
    VALIDATING = "VALIDATING"
    ECONOMIC_REVIEW = "ECONOMIC_REVIEW"
    RISK_REVIEW = "RISK_REVIEW"
    SOURCING = "SOURCING"
    BRANDING = "BRANDING"
    CREATIVE_READY = "CREATIVE_READY"
    LISTING_READY = "LISTING_READY"
    QUALITY_CHECK = "QUALITY_CHECK"
    APPROVED_FOR_PUBLISH = "APPROVED_FOR_PUBLISH"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    PERFORMANCE_TEST = "PERFORMANCE_TEST"
    OPTIMIZING = "OPTIMIZING"
    WINNING = "WINNING"
    WEAK = "WEAK"
    PAUSED = "PAUSED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class StateTransitionRecord(BaseModel):
    product_id: str
    from_state: ProductLifecycleState
    to_state: ProductLifecycleState
    passed_guard: bool
    guard_reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductStateMachine:
    """
    Deterministic State Machine enforcing lawful transitions across the 18 lifecycle states.
    """

    # Legal forward/backward transition paths
    ALLOWED_TRANSITIONS: Dict[ProductLifecycleState, Set[ProductLifecycleState]] = {
        ProductLifecycleState.DISCOVERED: {ProductLifecycleState.RESEARCHING, ProductLifecycleState.REJECTED},
        ProductLifecycleState.RESEARCHING: {ProductLifecycleState.VALIDATING, ProductLifecycleState.REJECTED},
        ProductLifecycleState.VALIDATING: {ProductLifecycleState.ECONOMIC_REVIEW, ProductLifecycleState.REJECTED},
        ProductLifecycleState.ECONOMIC_REVIEW: {ProductLifecycleState.RISK_REVIEW, ProductLifecycleState.REJECTED},
        ProductLifecycleState.RISK_REVIEW: {ProductLifecycleState.SOURCING, ProductLifecycleState.REJECTED},
        ProductLifecycleState.SOURCING: {ProductLifecycleState.BRANDING, ProductLifecycleState.REJECTED},
        ProductLifecycleState.BRANDING: {ProductLifecycleState.CREATIVE_READY, ProductLifecycleState.REJECTED},
        ProductLifecycleState.CREATIVE_READY: {ProductLifecycleState.LISTING_READY, ProductLifecycleState.REJECTED},
        ProductLifecycleState.LISTING_READY: {ProductLifecycleState.QUALITY_CHECK, ProductLifecycleState.REJECTED},
        ProductLifecycleState.QUALITY_CHECK: {ProductLifecycleState.APPROVED_FOR_PUBLISH, ProductLifecycleState.REJECTED},
        ProductLifecycleState.APPROVED_FOR_PUBLISH: {ProductLifecycleState.PUBLISHING, ProductLifecycleState.PAUSED, ProductLifecycleState.REJECTED},
        ProductLifecycleState.PUBLISHING: {ProductLifecycleState.PUBLISHED, ProductLifecycleState.APPROVED_FOR_PUBLISH, ProductLifecycleState.PAUSED},
        ProductLifecycleState.PUBLISHED: {ProductLifecycleState.PERFORMANCE_TEST, ProductLifecycleState.PAUSED, ProductLifecycleState.RETIRED},
        ProductLifecycleState.PERFORMANCE_TEST: {ProductLifecycleState.OPTIMIZING, ProductLifecycleState.WINNING, ProductLifecycleState.WEAK, ProductLifecycleState.PAUSED},
        ProductLifecycleState.OPTIMIZING: {ProductLifecycleState.WINNING, ProductLifecycleState.WEAK, ProductLifecycleState.PAUSED, ProductLifecycleState.RETIRED},
        ProductLifecycleState.WINNING: {ProductLifecycleState.OPTIMIZING, ProductLifecycleState.PAUSED, ProductLifecycleState.RETIRED},
        ProductLifecycleState.WEAK: {ProductLifecycleState.OPTIMIZING, ProductLifecycleState.PAUSED, ProductLifecycleState.RETIRED},
        ProductLifecycleState.PAUSED: {ProductLifecycleState.APPROVED_FOR_PUBLISH, ProductLifecycleState.OPTIMIZING, ProductLifecycleState.RETIRED},
        ProductLifecycleState.RETIRED: set(),
        ProductLifecycleState.REJECTED: set()
    }

    def can_transition(
        self,
        current_state: ProductLifecycleState,
        target_state: ProductLifecycleState,
        prerequisite_checks: Optional[Dict[str, bool]] = None
    ) -> StateTransitionRecord:
        """Evaluates whether state transition is legally permissible."""
        allowed = self.ALLOWED_TRANSITIONS.get(current_state, set())
        
        if target_state not in allowed:
            return StateTransitionRecord(
                product_id="N/A",
                from_state=current_state,
                to_state=target_state,
                passed_guard=False,
                guard_reason=f"ILLEGAL TRANSITION: Cannot transition directly from {current_state.value} to {target_state.value}."
            )

        # Deterministic Guard Checks
        if prerequisite_checks:
            failed = [k for k, v in prerequisite_checks.items() if not v]
            if failed:
                return StateTransitionRecord(
                    product_id="N/A",
                    from_state=current_state,
                    to_state=target_state,
                    passed_guard=False,
                    guard_reason=f"GUARD FAILURE: Missing prerequisite checks: {', '.join(failed)}"
                )

        return StateTransitionRecord(
            product_id="N/A",
            from_state=current_state,
            to_state=target_state,
            passed_guard=True,
            guard_reason="TRANSITION APPROVED: All state guardrails satisfied."
        )


# Global singleton instance
state_machine = ProductStateMachine()
