from pathlib import Path

from dotenv import load_dotenv


def load_project_env() -> None:
    """Load env vars from the project root, with .venv/.env as a fallback."""
    project_root = Path(__file__).resolve().parents[2]
    candidate_paths = [
        project_root / ".env",
        project_root / ".venv" / ".env",
    ]

    for candidate_path in candidate_paths:
        if candidate_path.exists():
            load_dotenv(candidate_path, override=False)
