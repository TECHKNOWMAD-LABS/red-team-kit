"""Performance tests — parallel execution, batch processing, async sessions."""

from __future__ import annotations

import asyncio
import time

import pytest

from redteamkit.agent import AgentRole
from redteamkit.council import AdversarialCouncil


class TestAsyncSession:
    """Tests for async parallel session execution."""

    @pytest.mark.asyncio
    async def test_arun_session_basic(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
        record = await council.arun_session("H-ASYNC-001", confidence=0.6)
        assert record.hypothesis_id == "H-ASYNC-001"
        assert len(record.critiques) == 2
        assert record.score is not None

    @pytest.mark.asyncio
    async def test_arun_session_with_semaphore(self):
        roles = [AgentRole.CONTRARIAN] * 20
        council = AdversarialCouncil(roles=roles)
        record = await council.arun_session("H-ASYNC-002", max_concurrency=5)
        assert len(record.critiques) == 20

    @pytest.mark.asyncio
    async def test_arun_session_validates_input(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        with pytest.raises(ValueError, match="hypothesis_id"):
            await council.arun_session("")

    @pytest.mark.asyncio
    async def test_arun_session_no_agents(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        council.agents.clear()
        with pytest.raises(ValueError, match="no agents"):
            await council.arun_session("H-001")


class TestBatchProcessing:
    """Tests for batch hypothesis processing."""

    def test_run_batch_basic(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
        results = council.run_batch(["H-B-001", "H-B-002", "H-B-003"])
        assert len(results) == 3
        for r in results:
            assert r.score is not None

    def test_run_batch_empty_raises(self):
        council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
        with pytest.raises(ValueError, match="non-empty"):
            council.run_batch([])

    def test_run_batch_performance(self):
        """Batch of 10 hypotheses should complete under 2 seconds."""
        council = AdversarialCouncil(
            roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER, AgentRole.DEVILS_ADVOCATE]
        )
        h_ids = [f"H-PERF-{i:03d}" for i in range(10)]
        start = time.monotonic()
        results = council.run_batch(h_ids, max_workers=4)
        elapsed = time.monotonic() - start
        assert len(results) == 10
        assert elapsed < 2.0, f"Batch took {elapsed:.2f}s — too slow"


class TestSequentialVsParallel:
    """Measure sequential vs async execution."""

    def test_sequential_baseline(self):
        council = AdversarialCouncil(roles=list(AgentRole))
        start = time.monotonic()
        for i in range(5):
            council.run_session(f"H-SEQ-{i}")
        sequential_time = time.monotonic() - start
        assert len(council.sessions) == 5
        # Just ensure it completes; these are CPU-bound so both are fast
        assert sequential_time < 2.0

    @pytest.mark.asyncio
    async def test_async_parallel(self):
        council = AdversarialCouncil(roles=list(AgentRole))
        start = time.monotonic()
        tasks = [council.arun_session(f"H-PAR-{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)
        parallel_time = time.monotonic() - start
        assert len(results) == 5
        assert parallel_time < 2.0
