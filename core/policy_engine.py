"""
Action-Level Permission, Policy Engine & Idempotency Guard.
Architectural Principle: LLM proposes action -> Policy Engine decides authority -> Tool executes -> Verifier confirms.
"""

from enum import Enum
from typing import Dict, Any, Optional, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    READ_MARKET_DATA = "READ_MARKET_DATA"
    READ_COMPETITOR_DATA = "READ_COMPETITOR_DATA"
    READ_SUPPLIER_DATA = "READ_SUPPLIER_DATA"
    CREATE_PRODUCT_DRAFT = "CREATE_PRODUCT_DRAFT"
    EDIT_PRODUCT = "EDIT_PRODUCT"
    PUBLISH_PRODUCT = "PUBLISH_PRODUCT"
    CHANGE_PRICE = "CHANGE_PRICE"
    CREATE_DISCOUNT = "CREATE_DISCOUNT"
    POST_SOCIAL = "POST_SOCIAL"
    CREATE_CAMPAIGN = "CREATE_CAMPAIGN"
    SPEND_AD_BUDGET = "SPEND_AD_BUDGET"
    UNPUBLISH_PRODUCT = "UNPUBLISH_PRODUCT"
    CHANGE_STORE_SETTINGS = "CHANGE_STORE_SETTINGS"


class AgentRole(str, Enum):
    MASTER_ORCHESTRATOR = "MASTER_ORCHESTRATOR"
    MARKET_INTELLIGENCE = "MARKET_INTELLIGENCE"
    PAIN_POINT_HUNTER = "PAIN_POINT_HUNTER"
    MOAT_ENGINEER = "MOAT_ENGINEER"
    DEVILS_CRITIC = "DEVILS_CRITIC"
    UNIT_ECONOMICS = "UNIT_ECONOMICS"
    LISTING_COPYWRITER = "LISTING_COPYWRITER"
    PUBLISHING_OPERATOR = "PUBLISHING_OPERATOR"


class ActionPolicyResult(BaseModel):
    is_permitted: bool
    action: ActionType
    agent_role: AgentRole
    reason: str
    idempotency_key: str
    requires_human_approval: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PolicyEngine:
    """
    Central Authority Policy Engine.
    Controls what actions each agent is permitted to execute, spending limits, and daily quotas.
    """

    # Role Permissions Matrix (Strict Least Privilege)
    ROLE_PERMISSIONS: Dict[AgentRole, Set[ActionType]] = {
        AgentRole.MARKET_INTELLIGENCE: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_COMPETITOR_DATA
        },
        AgentRole.PAIN_POINT_HUNTER: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_COMPETITOR_DATA
        },
        AgentRole.MOAT_ENGINEER: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_SUPPLIER_DATA,
            ActionType.CREATE_PRODUCT_DRAFT
        },
        AgentRole.DEVILS_CRITIC: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_COMPETITOR_DATA,
            ActionType.READ_SUPPLIER_DATA
        },
        AgentRole.UNIT_ECONOMICS: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_SUPPLIER_DATA
        },
        AgentRole.LISTING_COPYWRITER: {
            ActionType.CREATE_PRODUCT_DRAFT,
            ActionType.EDIT_PRODUCT
        },
        AgentRole.PUBLISHING_OPERATOR: {
            ActionType.PUBLISH_PRODUCT,
            ActionType.UNPUBLISH_PRODUCT
        },
        AgentRole.MASTER_ORCHESTRATOR: {
            ActionType.READ_MARKET_DATA,
            ActionType.READ_COMPETITOR_DATA,
            ActionType.READ_SUPPLIER_DATA,
            ActionType.CREATE_PRODUCT_DRAFT,
            ActionType.EDIT_PRODUCT,
            ActionType.PUBLISH_PRODUCT,
            ActionType.CHANGE_PRICE,
            ActionType.CREATE_DISCOUNT,
            ActionType.CREATE_CAMPAIGN,
            ActionType.SPEND_AD_BUDGET,
            ActionType.UNPUBLISH_PRODUCT
        }
    }

    def __init__(self):
        self.daily_published_count = 0
        self.max_daily_publish_limit = 10
        self.daily_ad_spend_usd = 0.0
        self.max_daily_ad_spend_limit = 250.0
        self.executed_idempotency_keys: Set[str] = set()

    def evaluate_action_permission(
        self,
        agent_role: AgentRole,
        action: ActionType,
        idempotency_key: str,
        spend_amount_usd: float = 0.0,
        price_change_pct: float = 0.0
    ) -> ActionPolicyResult:
        """Evaluates whether an requested action is authorized under current policy."""
        
        # 1. Idempotency Check: Prevent duplicate side-effects
        if idempotency_key in self.executed_idempotency_keys:
            return ActionPolicyResult(
                is_permitted=False,
                action=action,
                agent_role=agent_role,
                idempotency_key=idempotency_key,
                reason=f"IDEMPOTENCY BLOCKED: Action with key '{idempotency_key}' already executed."
            )

        # 2. Strict Role Capability Boundary
        allowed_actions = self.ROLE_PERMISSIONS.get(agent_role, set())
        if action not in allowed_actions:
            return ActionPolicyResult(
                is_permitted=False,
                action=action,
                agent_role=agent_role,
                idempotency_key=idempotency_key,
                reason=f"POLICY DENIAL: Agent role '{agent_role.value}' lacks permission for '{action.value}'."
            )

        # 3. Daily Publishing Quota Guard
        if action == ActionType.PUBLISH_PRODUCT:
            if self.daily_published_count >= self.max_daily_publish_limit:
                return ActionPolicyResult(
                    is_permitted=False,
                    action=action,
                    agent_role=agent_role,
                    idempotency_key=idempotency_key,
                    reason=f"QUOTA LIMIT: Daily publishing quota of {self.max_daily_publish_limit} reached."
                )

        # 4. Financial Spending Limit Guard
        if action == ActionType.SPEND_AD_BUDGET:
            if (self.daily_ad_spend_usd + spend_amount_usd) > self.max_daily_ad_spend_limit:
                return ActionPolicyResult(
                    is_permitted=False,
                    action=action,
                    agent_role=agent_role,
                    idempotency_key=idempotency_key,
                    requires_human_approval=True,
                    reason=f"BUDGET CAP: Spending ${spend_amount_usd} exceeds daily ceiling of ${self.max_daily_ad_spend_limit}."
                )

        # 5. Dangerous Price Mutation Guard (Max 30% single-day change without human approval)
        if action == ActionType.CHANGE_PRICE and abs(price_change_pct) > 30.0:
            return ActionPolicyResult(
                is_permitted=False,
                action=action,
                agent_role=agent_role,
                idempotency_key=idempotency_key,
                requires_human_approval=True,
                reason=f"PRICE SAFETY: Price change of {price_change_pct}% exceeds autonomous safety limit of ±30%."
            )

        return ActionPolicyResult(
            is_permitted=True,
            action=action,
            agent_role=agent_role,
            idempotency_key=idempotency_key,
            reason="AUTHORIZED: Action satisfies all policy constraints and permissions."
        )

    def record_action_executed(self, idempotency_key: str, action: ActionType, spend_amount_usd: float = 0.0) -> None:
        """Commits executed action into state to guarantee idempotency."""
        self.executed_idempotency_keys.add(idempotency_key)
        if action == ActionType.PUBLISH_PRODUCT:
            self.daily_published_count += 1
        elif action == ActionType.SPEND_AD_BUDGET:
            self.daily_ad_spend_usd += spend_amount_usd


# Global singleton instance
policy_engine = PolicyEngine()
