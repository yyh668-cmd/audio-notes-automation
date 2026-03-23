from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI

from .models import TranscriptSegment, TranscriptionInfo
from .utils import format_timestamp


def render_transcript_text(segments: list[TranscriptSegment]) -> str:
    lines = []
    for segment in segments:
        speaker = segment.speaker or "UNKNOWN"
        lines.append(f"[{segment.start:8.2f} - {segment.end:8.2f}] {speaker}: {segment.text}")
    return "\n".join(lines)


def render_speaker_transcript_markdown(segments: list[TranscriptSegment]) -> str:
    lines = ["# Speaker Transcript", ""]
    for segment in segments:
        speaker = segment.speaker or "UNKNOWN"
        lines.append(f"## {speaker} [{format_timestamp(segment.start)} - {format_timestamp(segment.end)}]")
        lines.append("")
        lines.append(segment.text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_extractive_notes(
    audio_path: Path,
    segments: list[TranscriptSegment],
    info: TranscriptionInfo,
    *,
    section_seconds: float = 90.0,
    max_segments_per_section: int = 8,
) -> str:
    sections: list[list[TranscriptSegment]] = []
    current: list[TranscriptSegment] = []
    section_anchor = 0.0

    for segment in segments:
        if not current:
            section_anchor = segment.start
        current.append(segment)
        if len(current) >= max_segments_per_section or segment.end - section_anchor >= section_seconds:
            sections.append(current)
            current = []

    if current:
        sections.append(current)

    speaker_names = sorted({segment.speaker or "UNKNOWN" for segment in segments})
    lines = [
        "# Organized Notes",
        "",
        f"- Source file: {audio_path.name}",
        f"- Duration: {format_timestamp(info.duration)}",
        f"- Detected language: {info.language}",
        f"- Speaker labels: {', '.join(speaker_names)}",
        f"- Notes backend: {info.notes_backend}",
        "",
    ]

    for index, section in enumerate(sections, start=1):
        start = format_timestamp(section[0].start)
        end = format_timestamp(section[-1].end)
        lines.append(f"## Section {index} [{start} - {end}]")
        lines.append("")
        lines.append(f"- Anchor line: {section[0].text}")
        for segment in section:
            speaker = segment.speaker or "UNKNOWN"
            lines.append(f"- {speaker}: {segment.text}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_openai_notes(
    audio_path: Path,
    segments: list[TranscriptSegment],
    info: TranscriptionInfo,
    *,
    model: str,
    api_key_env: str,
) -> str:
    api_key = os.environ.get(api_key_env) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(f"Missing {api_key_env} / OPENAI_API_KEY for OpenAI notes generation.")

    client = OpenAI(api_key=api_key)
    transcript = render_transcript_text(segments)
    instructions = (
        "Generate organized notes from the transcript. "
        "Use only the transcript content. "
        "Do not invent facts. "
        "Use markdown headings and bullet points. "
        "Preserve important terminology and speaker attribution where useful."
    )
    prompt = (
        f"Audio file: {audio_path.name}\n"
        f"Detected language: {info.language}\n"
        f"Duration: {format_timestamp(info.duration)}\n\n"
        "Transcript:\n"
        f"{transcript}"
    )
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
    )
    return response.output_text.strip() + "\n"


def generate_notes(
    audio_path: Path,
    segments: list[TranscriptSegment],
    info: TranscriptionInfo,
    *,
    backend: str,
    openai_model: str,
    openai_api_key_env: str,
) -> str:
    if backend == "openai":
        return render_openai_notes(
            audio_path,
            segments,
            info,
            model=openai_model,
            api_key_env=openai_api_key_env,
        )

    if backend == "auto":
        try:
            return render_openai_notes(
                audio_path,
                segments,
                info,
                model=openai_model,
                api_key_env=openai_api_key_env,
            )
        except Exception:
            return render_extractive_notes(audio_path, segments, info)

    return render_extractive_notes(audio_path, segments, info)

