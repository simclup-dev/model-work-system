"""Make `evals/runner.py` importable without turning `evals/` into a package."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
