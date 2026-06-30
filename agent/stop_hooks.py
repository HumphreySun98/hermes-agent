"""Round-end stop policy — the bound on the ``pre_stop`` hook loop.

``agent/conversation_loop.py`` fires the ``pre_stop`` hook (resolved by
:func:`hermes_cli.plugins.get_pre_stop_continue_message`) just before it accepts
a final answer; a hook may keep the agent going — run a check, tidy the diff,
run a skill — instead of stopping. This module holds the one piece of *agent*
policy around that: the per-turn bound, so a hook that always says "continue"
can never trap the loop. It sits next to its sibling ``agent/verification_stop.py``.
"""

from __future__ import annotations

from typing import Any, Optional

DEFAULT_MAX_STOP_NUDGES = 3


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


__all__ = ["DEFAULT_MAX_STOP_NUDGES", "max_stop_nudges"]
