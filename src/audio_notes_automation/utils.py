from __future__ import annotations

import json
import shutil
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def clean_text(text: str) -> str:
    return " ".join(text.split())


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def prepare_audio_input(audio_path: Path, work_dir: Path) -> Path:
    if str(audio_path).isascii():
        return audio_path

    safe_dir = ensure_output_dir(work_dir / "_work")
    safe_path = safe_dir / f"input_audio{audio_path.suffix.lower()}"
    shutil.copy2(audio_path, safe_path)
    return safe_path


def write_text(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
