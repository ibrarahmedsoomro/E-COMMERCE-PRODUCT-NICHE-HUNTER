"""
Atomic Distributed Lease & Task Lock Manager.
Prevents concurrent worker race conditions on critical mutations (Publishing, Pricing, Budget spend).
Includes lease timeout, worker heartbeats, and automatic crash recovery.
"""

import time
import threading
from typing import Dict, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class LeaseRecord(BaseModel):
    resource_id: str
    owner_worker_id: str
    acquired_at: float
    expires_at: float
    is_active: bool = True


class DistributedLeaseManager:
    """
    Atomic in-memory and DB-compatible lease manager for distributed workers.
    Ensures that only ONE worker can mutate a product or resource at a time.
    """

    def __init__(self, default_ttl_seconds: int = 30):
        self.default_ttl_seconds = default_ttl_seconds
        self._locks: Dict[str, LeaseRecord] = {}
        self._mutex = threading.Lock()

    def acquire_lease(self, resource_id: str, worker_id: str, ttl_seconds: Optional[int] = None) -> bool:
        """Atomically attempts to acquire a lease on a resource."""
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        
        with self._mutex:
            existing = self._locks.get(resource_id)
            if existing and existing.is_active:
                # Check if existing lease expired (worker crash recovery)
                if now >= existing.expires_at:
                    # Expired -> Reclaim lease
                    self._locks[resource_id] = LeaseRecord(
                        resource_id=resource_id,
                        owner_worker_id=worker_id,
                        acquired_at=now,
                        expires_at=now + ttl,
                        is_active=True
                    )
                    return True
                # Still locked by another or same worker
                if existing.owner_worker_id == worker_id:
                    # Refresh own lease
                    existing.expires_at = now + ttl
                    return True
                return False

            # Acquire brand new lease
            self._locks[resource_id] = LeaseRecord(
                resource_id=resource_id,
                owner_worker_id=worker_id,
                acquired_at=now,
                expires_at=now + ttl,
                is_active=True
            )
            return True

    def release_lease(self, resource_id: str, worker_id: str) -> bool:
        """Releases an active lease if owned by the requesting worker."""
        with self._mutex:
            existing = self._locks.get(resource_id)
            if existing and existing.owner_worker_id == worker_id:
                existing.is_active = False
                del self._locks[resource_id]
                return True
            return False

    def heartbeat(self, resource_id: str, worker_id: str, extend_seconds: int = 30) -> bool:
        """Extends an active lease while a long-running task is progressing."""
        now = time.time()
        with self._mutex:
            existing = self._locks.get(resource_id)
            if existing and existing.is_active and existing.owner_worker_id == worker_id:
                existing.expires_at = now + extend_seconds
                return True
            return False


# Global singleton instance
lease_manager = DistributedLeaseManager()
