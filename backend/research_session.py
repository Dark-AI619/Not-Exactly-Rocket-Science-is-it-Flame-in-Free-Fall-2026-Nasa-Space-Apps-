# Co-authored with ChatGPT
"""Pure per-session request control shared by the Assistant and Solution Lab."""
from __future__ import annotations

from .grounded import GroundedResult, grounded_from_packet
from .groq_adapter import GroqAdapter


def research_turn(packet: dict, adapter: GroqAdapter, used: int,
                  *, history: tuple[str, ...] = ()) -> tuple[GroundedResult, int]:
    if not adapter.settings.configured or not packet["supported"]:
        return grounded_from_packet(packet, adapter, history=history), used
    if used >= adapter.settings.session_request_limit:
        return GroundedResult("evidence_only", "session_limit", (), (), packet, None), used
    return grounded_from_packet(packet, adapter, history=history), used + 1
