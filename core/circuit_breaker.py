"""
Autonomous Circuit Breaker & Anomaly Detection Layer.
Monitors operational anomalies, error rates, mass API failures, price spikes, and halts subsystems safely.
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CircuitStatus(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    HALF_OPEN = "HALF_OPEN"# Recovering/testing trickle traffic
    OPEN = "OPEN"          # Tripped / Paused subsystem


class SubsystemEnum(str, Enum):
    MARKET_SCRAPING = "MARKET_SCRAPING"
    PUBLISHING_ENGINE = "PUBLISHING_ENGINE"
    AD_SPEND_ENGINE = "AD_SPEND_ENGINE"
    PRICING_ENGINE = "PRICING_ENGINE"
    GLOBAL_SYSTEM = "GLOBAL_SYSTEM"


class CircuitBreakerTrip(BaseModel):
    subsystem: SubsystemEnum
    status: CircuitStatus
    trip_reason: str
    failure_count: int
    tripped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state_preserved: bool = True


class CircuitBreaker:
    """
    Subsystem-level Circuit Breaker.
    Protects the business against catastrophic runs, API outage cascade, runaway spending, or corrupted data.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout_seconds: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        self.subsystem_status: Dict[SubsystemEnum, CircuitStatus] = {
            s: CircuitStatus.CLOSED for s in SubsystemEnum
        }
        self.failure_counters: Dict[SubsystemEnum, int] = {
            s: 0 for s in SubsystemEnum
        }
        self.trip_history: List[CircuitBreakerTrip] = []
        self.is_global_kill_switch_active: bool = False

    def check_subsystem_available(self, subsystem: SubsystemEnum) -> bool:
        """Checks if a subsystem is allowed to execute work."""
        if self.is_global_kill_switch_active:
            return False
        return self.subsystem_status.get(subsystem, CircuitStatus.CLOSED) != CircuitStatus.OPEN

    def record_success(self, subsystem: SubsystemEnum) -> None:
        """Resets failure counter on successful execution."""
        self.failure_counters[subsystem] = 0
        if self.subsystem_status[subsystem] == CircuitStatus.HALF_OPEN:
            self.subsystem_status[subsystem] = CircuitStatus.CLOSED

    def record_failure(self, subsystem: SubsystemEnum, error_msg: str) -> Optional[CircuitBreakerTrip]:
        """Records an error and trips circuit breaker if threshold is exceeded."""
        self.failure_counters[subsystem] = self.failure_counters.get(subsystem, 0) + 1
        count = self.failure_counters[subsystem]

        if count >= self.failure_threshold and self.subsystem_status[subsystem] != CircuitStatus.OPEN:
            self.subsystem_status[subsystem] = CircuitStatus.OPEN
            trip = CircuitBreakerTrip(
                subsystem=subsystem,
                status=CircuitStatus.OPEN,
                trip_reason=f"Circuit Tripped: {count} consecutive failures. Latest: {error_msg}",
                failure_count=count,
                state_preserved=True
            )
            self.trip_history.append(trip)
            return trip
        return None

    def trigger_kill_switch(self, reason: str = "Manual Emergency Kill Switch Triggered") -> None:
        """Stops all autonomous side-effects immediately while preserving state."""
        self.is_global_kill_switch_active = True
        for s in SubsystemEnum:
            self.subsystem_status[s] = CircuitStatus.OPEN
        self.trip_history.append(CircuitBreakerTrip(
            subsystem=SubsystemEnum.GLOBAL_SYSTEM,
            status=CircuitStatus.OPEN,
            trip_reason=reason,
            failure_count=999,
            state_preserved=True
        ))

    def reset_subsystem(self, subsystem: SubsystemEnum) -> None:
        """Manually or programmatically resets a paused subsystem."""
        self.subsystem_status[subsystem] = CircuitStatus.CLOSED
        self.failure_counters[subsystem] = 0


# Global singleton instance
circuit_breaker = CircuitBreaker()
