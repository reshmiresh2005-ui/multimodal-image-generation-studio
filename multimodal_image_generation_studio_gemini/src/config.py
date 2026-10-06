import os
from dataclasses import dataclass
from pathlib import Path


IMAGE_SIZES = {
    "16:9 Landscape": "16:9",
    "1:1 Square": "1:1",
    "9:16 Portrait": "9:16",
}

IMAGE_FORMATS = {
    "JPEG": "image/jpeg",
}


@dataclass(frozen=True)
class Settings:
    api_key: str
    image_model: str
    demo_mode: bool
    max_retries: int
    base_backoff: float
    output_dir: Path
    history_file: Path


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def load_settings() -> Settings:
    output_dir = Path("data/generated")
    history_file = Path("data/history.json")

    output_dir.mkdir(parents=True, exist_ok=True)
    history_file.parent.mkdir(parents=True, exist_ok=True)

    return Settings(
        api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        image_model=os.getenv(
            "GEMINI_IMAGE_MODEL",
            "gemini-3.1-flash-image",
        ).strip(),
        demo_mode=_as_bool(
            os.getenv("DEMO_MODE", "false")
        ),
        max_retries=int(
            os.getenv("MAX_RETRIES", "4")
        ),
        base_backoff=float(
            os.getenv("BASE_BACKOFF", "1.0")
        ),
        output_dir=output_dir,
        history_file=history_file,
    )