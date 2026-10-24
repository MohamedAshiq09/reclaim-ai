from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Agentverse and ASI:One configurations
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY", "").strip()
ASI_ONE_API_KEY = os.getenv("ASI_ONE_API_KEY", "").strip()
ASI_ONE_BASE_URL = os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1").strip()
ASI_ONE_MODEL = os.getenv("ASI_ONE_MODEL", "asi1").strip()

# Search API
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "").strip()

# Email Dispatcher (Resend)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev").strip()

# Demo Mode Settings
DEMO_MODE = os.getenv("DEMO_MODE", "1").strip().lower() in ("1", "true", "yes")
DEMO_RECIPIENT_OVERRIDE = os.getenv("DEMO_RECIPIENT_OVERRIDE", "").strip()

# FET Payment Settings
FET_USE_TESTNET = os.getenv("FET_USE_TESTNET", "true").strip().lower() in ("1", "true", "yes")
FET_PAYMENT_AMOUNT = os.getenv("FET_PAYMENT_AMOUNT", "0.001").strip()

# Agent Seeds
CONCIERGE_SEED = os.getenv("CONCIERGE_SEED", "reclaimai_concierge_seed_phrase_hackathon_2026_festive").strip()
RESEARCHER_SEED = os.getenv("RESEARCHER_SEED", "reclaimai_researcher_seed_phrase_hackathon_2026_festive").strip()
DRAFTER_SEED = os.getenv("DRAFTER_SEED", "reclaimai_drafter_seed_phrase_hackathon_2026_festive").strip()
DISPATCHER_SEED = os.getenv("DISPATCHER_SEED", "reclaimai_dispatcher_seed_phrase_hackathon_2026_festive").strip()
WATCHER_SEED = os.getenv("WATCHER_SEED", "reclaimai_watcher_seed_phrase_hackathon_2026_festive").strip()

# Agent Addresses
CONCIERGE_ADDRESS = os.getenv("CONCIERGE_ADDRESS", "agent1q2a0f0a8zyw3229agt7saxtvenftxwe0gry6nv02dzd78rvye98tzty77e7").strip()
RESEARCHER_ADDRESS = os.getenv("RESEARCHER_ADDRESS", "agent1qgktn2gauj62w4uaynnapajvsexxjgxuq8ylj6ru2503p9hxt09h6tcgaum").strip()
DRAFTER_ADDRESS = os.getenv("DRAFTER_ADDRESS", "agent1q00z4x9d574zttujnjwkj7zz7u0elv4jw4exrrefvqegjnz0dntu5cj5js0").strip()
DISPATCHER_ADDRESS = os.getenv("DISPATCHER_ADDRESS", "agent1qg9evq8equ7kkt2nw8fkg2wgujr6sy69ucpeflyr28539rnx8v7ng2wuu8l").strip()
WATCHER_ADDRESS = os.getenv("WATCHER_ADDRESS", "agent1qgz54hf8dzdvqsuf3ja9vfvdl25d9umed0r6y6vhalwtl2s0vqkmw3l0a46").strip()

# Local SQLite DB
DATABASE_PATH = ROOT_DIR / "cases.db"
CORPUS_DIR = ROOT_DIR / "corpus"
