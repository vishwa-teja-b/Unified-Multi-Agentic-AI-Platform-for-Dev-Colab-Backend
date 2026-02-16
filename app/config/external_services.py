"""
Centralized external service URLs.
All third-party and self-hosted service endpoints are defined here
so they can be managed from a single location.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Self-hosted services ────────────────────────────────────
PISTON_API_URL: str = os.getenv(
    "PISTON_API_URL", "http://localhost:2000/api/v2/execute"
)

# ── LLM / AI services ──────────────────────────────────────
OPENROUTER_BASE_URL: str = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)

# ── Observability ───────────────────────────────────────────
LANGSMITH_ENDPOINT: str = os.getenv(
    "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
)

# ── Social URL prefixes (used in profile response) ─────────
GITHUB_URL_PREFIX: str = "https://github.com/"
LINKEDIN_URL_PREFIX: str = "https://linkedin.com/in/"
