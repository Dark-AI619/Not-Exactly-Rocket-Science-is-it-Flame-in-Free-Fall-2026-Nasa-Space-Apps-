# Co-authored with ChatGPT
"""Read-only scientific research services, independent of Streamlit."""

from .store import ResearchStore, ResearchError, validate_database
from .sql_workspace import QueryRejected, RestrictedSQL
from .analysis import Comparison, build_comparison
from .retrieval import retrieve_evidence, route_question
from .groq_adapter import GroqAdapter, GroqSettings, GroqResult, load_groq_settings
from .grounded import GroundedResult, answer_question, grounded_from_packet
from .research_session import research_turn

__all__ = ["ResearchStore", "ResearchError", "validate_database", "QueryRejected", "RestrictedSQL", "Comparison", "build_comparison", "retrieve_evidence", "route_question", "GroqAdapter", "GroqSettings", "GroqResult", "load_groq_settings", "GroundedResult", "answer_question", "grounded_from_packet", "research_turn"]
