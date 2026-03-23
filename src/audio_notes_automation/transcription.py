from __future__ import annotations

import os
from pathlib import Path

from faster_whisper import WhisperModel

from .models import TranscriptSegment
from .utils import clean_text


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
    beam_size: int,
    vad_filter: bool,
) -> tuple[list[TranscriptSegment], str, float, float]:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )

    items: list[TranscriptSegment] = []
    for index, segment in enumerate(segments):
        text = clean_text(segment.text)
        if not text:
            continue
        items.append(
            TranscriptSegment(
                id=index,
                start=float(segment.start),
                end=float(segment.end),
                text=text,
            )
        )

    return items, info.language, float(info.language_probability), float(info.duration)
