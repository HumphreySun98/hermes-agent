"""Round-end stop hooks — a general "before the agent finishes" gate.

Just before the agent loop accepts a final answer it fires the ``pre_stop``
hook. A callback (Python plugin or shell hook) may return a directive asking the
agent to keep going — run a check, tidy the diff, run a skill — instead of
stopping::

    {"action": "continue", "message": "<follow-up instruction for the model>"}

The Claude-Code Stop-hook shape (``{"decision": "block", "reason": ...}``, where
"block" means *block the stop*) is accepted too. Anything else lets the turn
finish.

This module is policy-only: it never runs anything itself, it just turns a
hook's directive into a bounded synthetic follow-up — the same mechanism the
verify-on-stop guard uses, which is now simply one built-in reason to continue
rather than the only one. The loop is bounded by ``agent.max_stop_nudges`` so a
hook that always says "continue" can't trap the agent.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

DEFAULT_MAX_STOP_NUDGES = 3

# Verbs that mean "don't stop yet". ``continue`` is the canonical Hermes action;
# ``block`` mirrors Claude-Code Stop hooks, where blocking the stop == keep going.
_CONTINUE_ACTIONS = frozenset({"continue", "block"})


def resolve_pre_stop_directive(results: Iterable[Any]) -> Optional[str]:
    """First continue directive's message from a list of hook returns, or None.

    Accepts the canonical ``{"action": "continue", "message": ...}`` and the
    Claude-Code ``{"decision": "block", "reason": ...}`` shape. A directive with
    no message is ignored — there's nothing to tell the model, so let it stop.
    """
    for ret in results:
        if not isinstance(ret, dict):
            continue
        action = str(ret.get("action") or ret.get("decision") or "").strip().lower()
        if action not in _CONTINUE_ACTIONS:
            continue
        message = ret.get("message") or ret.get("reason")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return None


def max_stop_nudges(config: Optional[dict[str, Any]] = None) -> int:
    """Bound on consecutive ``pre_stop`` continue directives per turn (>= 0)."""
    if config is None:
        try:
            from hermes_cli.config import load_config

            config = load_config()
        except Exception:
            config = {}
    agent_cfg = (config or {}).get("agent") if isinstance(config, dict) else None
    raw = agent_cfg.get("max_stop_nudges") if isinstance(agent_cfg, dict) else None
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return DEFAULT_MAX_STOP_NUDGES


def run_pre_stop_hooks(**ctx: Any) -> Optional[str]:
    """Fire ``pre_stop`` hooks and return the first continue message, or None."""
    try:
        from hermes_cli.plugins import invoke_hook

        return resolve_pre_stop_directive(invoke_hook("pre_stop", **ctx))
    except Exception:
        return None


__all__ = [
    "DEFAULT_MAX_STOP_NUDGES",
    "max_stop_nudges",
    "resolve_pre_stop_directive",
    "run_pre_stop_hooks",
]
