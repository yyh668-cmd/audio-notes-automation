from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class TranscriptSegment:
    id: int
    start: float
    end: float
    text: str
    speaker: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class SpeakerTurn:
    start: float
    end: float
    speaker: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class TranscriptionInfo:
    language: str
    language_probability: float
    duration: float
    transcription_backend: str
    diarization_backend: str
    notes_backend: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class ArtifactPaths:
    output_dir: Path
    transcript_txt: Path
    transcript_json: Path
    speaker_transcript_md: Path
    organized_notes_md: Path
    run_manifest_json: Path


@dataclass
class PipelineResult:
    audio_path: Path
    artifacts: ArtifactPaths
    info: TranscriptionInfo
    segments: list[TranscriptSegment]
    speaker_turns: list[SpeakerTurn]

