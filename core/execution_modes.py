"""
Execution Mode Tiering & Autonomous Rollout Controls.
Tiers: SHADOW -> DRY_RUN -> CONTROLLED_LIVE -> FULL_AUTONOMOUS
"""

from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel


class ExecutionMode(str, Enum):
    SHADOW = "SHADOW"                      # Runs decisions & evaluations; ZERO external tool execution
    DRY_RUN = "DRY_RUN"                    # Simulates tool responses and validates payloads; no real mutation
    CONTROLLED_LIVE = "CONTROLLED_LIVE"    # Real execution with strict low-spending & quota boundaries
    FULL_AUTONOMOUS = "FULL_AUTONOMOUS"    # Full policy-bound autonomous operation


class ExecutionModeConfig(BaseModel):
    current_mode: ExecutionMode = ExecutionMode.CONTROLLED_LIVE
    allow_real_publishing: bool = False
    allow_real_spending: bool = False
    max_test_spend_usd: float = 25.0


# Global config instance
execution_mode_config = ExecutionModeConfig()
