import json
from datetime import datetime, timezone
from pathlib import Path


def save_image(
    image_bytes: bytes,
    output_dir: Path,
    extension: str = "png",
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    path = output_dir / f"generated_{timestamp}.{extension}"
    path.write_bytes(image_bytes)

    return path


def save_history(history_file: Path, record: dict) -> None:
    history_file.parent.mkdir(parents=True, exist_ok=True)

    history = []

    if history_file.exists():
        try:
            history = json.loads(
                history_file.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            history = []

    history.append(
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            **record,
        }
    )

    history_file.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
