# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: CC-BY-NC-4.0
"""The profiler hands agents a BOUNDED rolling window of recent cycles, not the
full accumulated history.

Originally profile() passed agents the full accumulated history, rebuilt as a
DataFrame from an unbounded list every cycle (O(N) per cycle, O(N^2) per
episode) — long full-workload rollouts grew from ~1.7s/step to >10s/step. The
fix bounds the window to the last K cycles: O(K) per cycle (flat), while still
letting a history-based in-sim agent (e.g. a Flexo-style controller) look back
several cycles. Latest-timestamp-only agents (Stdio/Spendy/Oblivious) are
unaffected because the newest cycle's rows are still last in the window.
"""
from types import SimpleNamespace

import pandas

from dse_sim.profiler.profiler import Profiler


class _RecordingAgent:
    """Duck-typed agent: records each DataFrame profile() passes to act()."""

    def __init__(self):
        self.received = []

    def act(self, history: pandas.DataFrame):
        self.received.append(history)
        return None


def _stub_collection():
    # Only the attributes Profiler.profile() touches.
    return SimpleNamespace(
        time=0.0,
        dse_config=SimpleNamespace(num_workers=3, half_ocus_per_worker=8),
        workers=[],
        steady=False,
        profilable_actors=[],
        register=lambda actor: None,
        unregsiter=lambda actor: None,
        log=lambda *a, **k: None,
    )


def test_window_is_bounded_to_last_k_cycles():
    agent = _RecordingAgent()
    profiler = Profiler(_stub_collection(), save_path="/dev/null",
                        agents=[agent], agent_history_cycles=3)

    times = [10.0, 20.0, 30.0, 40.0, 50.0]
    for t in times:
        profiler.profile(t)

    last = agent.received[-1]
    # Exactly the last 3 cycles are visible; the oldest two (10, 20) are dropped.
    assert sorted(last["time"].unique().tolist()) == [30.0, 40.0, 50.0]
    # The window never grows without bound: same size on every later cycle.
    assert agent.received[-2]["time"].nunique() == 3


def test_latest_timestamp_is_last_row_preserving_stdio_contract():
    # Stdio/Spendy read history["time"].iloc[-1]; it must be the newest cycle.
    agent = _RecordingAgent()
    profiler = Profiler(_stub_collection(), save_path="/dev/null",
                        agents=[agent], agent_history_cycles=12)

    for t in (10.0, 20.0, 30.0):
        profiler.profile(t)

    last = agent.received[-1]
    assert last["time"].iloc[-1] == 30.0


def test_default_window_matches_frame_stack_depth():
    agent = _RecordingAgent()
    profiler = Profiler(_stub_collection(), save_path="/dev/null", agents=[agent])

    for t in range(1, 16):  # 15 cycles
        profiler.profile(float(t))

    # Default keeps the last 12 cycles (frame-stack depth), not all 15.
    assert agent.received[-1]["time"].nunique() == 12
