"""
Model location config. Load from .env in project root.
"""
import os
from pathlib import Path

# Load .env from project root (parent of app/)
_root = Path(__file__).resolve().parent
_env_file = _root / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

# Model root: directory containing base.pt, large-v3.pt, etc.
# Default: models/ at project root
WHISPER_MODEL_ROOT = os.environ.get("WHISPER_MODEL_ROOT") or str(_root / "models")

# Per-model override: full path to .pt file (overrides MODEL_ROOT for that model)
WHISPER_MODEL_BASE = os.environ.get("WHISPER_MODEL_BASE")
WHISPER_MODEL_LARGE_V3 = os.environ.get("WHISPER_MODEL_LARGE_V3")

# Server port (default: 9876)
PORT = int(os.environ.get("PORT", "9876"))
