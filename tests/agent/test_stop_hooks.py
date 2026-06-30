"""Unit tests for the round-end `pre_stop` hook policy (agent/stop_hooks.py)."""

from __future__ import annotations

from agent import stop_hooks


class TestResolvePreStopDirective:
    def test_canonical_continue_wins(self):
        results = [{"action": "continue", "message": "run /clean"}]
        assert stop_hooks.resolve_pre_stop_directive(results) == "run /clean"

    def test_claude_block_means_continue(self):
        # Claude-Code Stop hooks: "block" the stop == keep going; reason is the msg.
        results = [{"decision": "block", "reason": "run the formatter"}]
        assert stop_hooks.resolve_pre_stop_directive(results) == "run the formatter"

    def test_first_actionable_directive_wins(self):
        results = [
            {"action": "continue"},                       # no message → skipped
            None,                                         # non-dict → skipped
            {"action": "continue", "message": "second"},
            {"action": "continue", "message": "third"},
        ]
        assert stop_hooks.resolve_pre_stop_directive(results) == "second"

    def test_message_is_trimmed(self):
        results = [{"action": "continue", "message": "  tidy up  "}]
        assert stop_hooks.resolve_pre_stop_directive(results) == "tidy up"

    def test_no_directive_returns_none(self):
        assert stop_hooks.resolve_pre_stop_directive([]) is None
        assert stop_hooks.resolve_pre_stop_directive([{"action": "allow"}]) is None
        assert stop_hooks.resolve_pre_stop_directive([{"context": "noise"}]) is None
        # A continue with a blank/non-string message is a no-op.
        assert stop_hooks.resolve_pre_stop_directive([{"action": "continue", "message": "   "}]) is None
        assert stop_hooks.resolve_pre_stop_directive([{"action": "continue", "message": 42}]) is None


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
