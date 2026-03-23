from __future__ import annotations

import os
from pathlib import Path

from .models import SpeakerTurn, TranscriptSegment


def diarize_audio(
    audio_path: Path,
    *,
    duration: float,
    diarize: bool,
    diarization_model: str,
    hf_token: str | None,
    hf_token_env: str,
    device: str,
    fallback_speaker: str,
) -> tuple[list[SpeakerTurn], str]:
    if not diarize:
        return [SpeakerTurn(start=0.0, end=duration, speaker=fallback_speaker)], "disabled-single-speaker"

    try:
        import torch
        from pyannote.audio import Pipeline
    except ImportError:
        return [SpeakerTurn(start=0.0, end=duration, speaker=fallback_speaker)], "missing-pyannote-fallback"

    token = hf_token or os.environ.get(hf_token_env) or os.environ.get("HF_TOKEN")
    if not token:
        return [SpeakerTurn(start=0.0, end=duration, speaker=fallback_speaker)], "missing-hf-token-fallback"

    pipeline = Pipeline.from_pretrained(diarization_model, use_auth_token=token)

    if hasattr(pipeline, "to"):
        target = "cpu"
        if device.startswith("cuda"):
            target = device
        pipeline.to(target)

    diarization = pipeline(str(audio_path))
    turns: list[SpeakerTurn] = []
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        turns.append(
            SpeakerTurn(
                start=float(segment.start),
                end=float(segment.end),
                speaker=str(speaker),
            )
        )

    if not turns:
        return [SpeakerTurn(start=0.0, end=duration, speaker=fallback_speaker)], "empty-diarization-fallback"

    return turns, f"pyannote:{diarization_model}"


def assign_speakers(
    transcript_segments: list[TranscriptSegment],
    speaker_turns: list[SpeakerTurn],
    *,
    fallback_speaker: str,
) -> list[TranscriptSegment]:
    ordered_turns = sorted(speaker_turns, key=lambda item: (item.start, item.end))
    if not ordered_turns:
        for segment in transcript_segments:
            segment.speaker = fallback_speaker
        return transcript_segments

    for segment in transcript_segments:
        best_speaker = fallback_speaker
        best_overlap = 0.0
        for turn in ordered_turns:
            if turn.end < segment.start:
                continue
            if turn.start > segment.end:
                break
            overlap = min(segment.end, turn.end) - max(segment.start, turn.start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn.speaker
        segment.speaker = best_speaker

    return transcript_segments

