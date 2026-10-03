"""
Append-Only Immutable Event Stream with Full Policy & Engine Versioning.
Every business decision, tool execution, and state change produces an immutable cryptographic event record.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# System Component Versions
POLICY_VERSION = "POLICY-v1.4"
ECONOMICS_VERSION = "ECONOMICS-v2.1"
AMAZON_FEES_VERSION = "AMAZON-FEES-v3.0"
ORCHESTRATOR_VERSION = "ORCHESTRATOR-v2.0"


class ImmutableAuditEvent(BaseModel):
    event_id: str
    previous_event_hash: str
    event_type: str
    entity_id: str
    agent_role: str
    action_type: str
    idempotency_key: str
    policy_version: str = POLICY_VERSION
    economics_version: str = ECONOMICS_VERSION
    amazon_fees_version: str = AMAZON_FEES_VERSION
    orchestrator_version: str = ORCHESTRATOR_VERSION
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_hash: str = ""


class ImmutableEventStream:
    """
    Append-only in-memory and database-backed event stream.
    Hash-chained to guarantee tamper-evidence and full operational lineage.
    """

    def __init__(self):
        self._events: List[ImmutableAuditEvent] = []
        self._last_hash: str = "GENESIS_BLOCK_00000000"

    def record_event(
        self,
        event_type: str,
        entity_id: str,
        agent_role: str,
        action_type: str,
        idempotency_key: str,
        payload: Dict[str, Any]
    ) -> ImmutableAuditEvent:
        """Appends an immutable event into the hash chain."""
        event_seq = len(self._events) + 1
        event_id = f"EVENT_{event_seq:06d}"
        
        # Calculate cryptographic hash of content + previous hash
        raw_to_hash = f"{event_id}:{self._last_hash}:{event_type}:{entity_id}:{agent_role}:{action_type}:{idempotency_key}:{json.dumps(payload, sort_keys=True)}"
        current_hash = hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()

        event = ImmutableAuditEvent(
            event_id=event_id,
            previous_event_hash=self._last_hash,
            event_type=event_type,
            entity_id=entity_id,
            agent_role=agent_role,
            action_type=action_type,
            idempotency_key=idempotency_key,
            payload=payload,
            event_hash=current_hash
        )

        self._events.append(event)
        self._last_hash = current_hash
        return event

    def get_events_for_entity(self, entity_id: str) -> List[ImmutableAuditEvent]:
        """Retrieves complete timeline audit trail for a specific product or decision."""
        return [e for e in self._events if e.entity_id == entity_id]

    def verify_integrity(self) -> bool:
        """Verifies the cryptographic chain integrity of the entire event stream."""
        prev = "GENESIS_BLOCK_00000000"
        for e in self._events:
            if e.previous_event_hash != prev:
                return False
            raw = f"{e.event_id}:{prev}:{e.event_type}:{e.entity_id}:{e.agent_role}:{e.action_type}:{e.idempotency_key}:{json.dumps(e.payload, sort_keys=True)}"
            expected_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if e.event_hash != expected_hash:
                return False
            prev = e.event_hash
        return True


# Global singleton instance
event_stream = ImmutableEventStream()
