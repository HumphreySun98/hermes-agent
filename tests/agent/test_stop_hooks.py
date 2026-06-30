"""Unit tests for the round-end stop bound (agent/stop_hooks.py).

The `pre_stop` directive aggregation lives in `hermes_cli.plugins`
(`get_pre_stop_continue_message`) and is tested in `tests/hermes_cli/test_plugins.py`,
alongside its sibling `get_pre_tool_call_block_message`.
"""

from __future__ import annotations

from agent import stop_hooks


class TestMaxStopNudges:
    def test_default_when_unset(self):
        assert stop_hooks.max_stop_nudges({}) == stop_hooks.DEFAULT_MAX_STOP_NUDGES
        assert stop_hooks.max_stop_nudges({"agent": {}}) == stop_hooks.DEFAULT_MAX_STOP_NUDGES

    def test_reads_config(self):
        assert stop_hooks.max_stop_nudges({"agent": {"max_stop_nudges": 5}}) == 5

    def test_clamps_and_coerces(self):
        assert stop_hooks.max_stop_nudges({"agent": {"max_stop_nudges": -1}}) == 0
        assert stop_hooks.max_stop_nudges({"agent": {"max_stop_nudges": "2"}}) == 2

    def test_bad_value_falls_back_to_default(self):
        assert stop_hooks.max_stop_nudges({"agent": {"max_stop_nudges": "nope"}}) == stop_hooks.DEFAULT_MAX_STOP_NUDGES
