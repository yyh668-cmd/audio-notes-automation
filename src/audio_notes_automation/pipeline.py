from __future__ import annotations

from pathlib import Path

from .diarization import assign_speakers, diarize_audio
from .models import ArtifactPaths, PipelineResult, TranscriptionInfo
from .notes import generate_notes, render_speaker_transcript_markdown, render_transcript_text
from .transcription import transcribe_audio
from .utils import ensure_output_dir, prepare_audio_input, write_json, write_text


def build_artifact_paths(output_dir: Path) -> ArtifactPaths:
    return ArtifactPaths(
        output_dir=output_dir,
        transcript_txt=output_dir / "transcript.txt",
        transcript_json=output_dir / "transcript.json",
        speaker_transcript_md=output_dir / "speaker_transcript.md",
        organized_notes_md=output_dir / "organized_notes.md",
        run_manifest_json=output_dir / "run_manifest.json",
    )


def run_pipeline(
    audio_path: Path,
    *,
    output_dir: Path | None,
    whisper_model: str,
    language: str | None,
    device: str,
    compute_type: str,
    beam_size: int,
    vad_filter: bool,
    diarize: bool,
    diarization_model: str,
    hf_token: str | None,
    hf_token_env: str,
    fallback_speaker: str,
    notes_backend: str,
    openai_model: str,
    openai_api_key_env: str,
) -> PipelineResult:
    audio_path = audio_path.resolve()
    target_dir = output_dir.resolve() if output_dir else (audio_path.parent / f"{audio_path.stem}_artifacts").resolve()
    ensure_output_dir(target_dir)
    artifacts = build_artifact_paths(target_dir)
    prepared_audio_path = prepare_audio_input(audio_path, target_dir)

    segments, language_detected, language_probability, duration = transcribe_audio(
        prepared_audio_path,
        model_name=whisper_model,
        device=device,
        compute_type=compute_type,
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )

    speaker_turns, diarization_backend = diarize_audio(
        prepared_audio_path,
        duration=duration,
        diarize=diarize,
        diarization_model=diarization_model,
        hf_token=hf_token,
        hf_token_env=hf_token_env,
        device=device,
        fallback_speaker=fallback_speaker,
    )
    segments = assign_speakers(segments, speaker_turns, fallback_speaker=fallback_speaker)

    info = TranscriptionInfo(
        language=language_detected,
        language_probability=language_probability,
        duration=duration,
        transcription_backend=f"faster-whisper:{whisper_model}",
        diarization_backend=diarization_backend,
        notes_backend=notes_backend,
    )

    transcript_text = render_transcript_text(segments)
    speaker_transcript = render_speaker_transcript_markdown(segments)
    notes_text = generate_notes(
        audio_path,
        segments,
        info,
        backend=notes_backend,
        openai_model=openai_model,
        openai_api_key_env=openai_api_key_env,
    )

    write_text(artifacts.transcript_txt, transcript_text)
    write_text(artifacts.speaker_transcript_md, speaker_transcript)
    write_text(artifacts.organized_notes_md, notes_text)
    write_json(
        artifacts.transcript_json,
        {
            "audio_path": str(audio_path),
            "prepared_audio_path": str(prepared_audio_path),
            "info": info.to_dict(),
            "segments": [segment.to_dict() for segment in segments],
            "speaker_turns": [turn.to_dict() for turn in speaker_turns],
        },
    )
    write_json(
        artifacts.run_manifest_json,
        {
            "audio_path": str(audio_path),
            "prepared_audio_path": str(prepared_audio_path),
            "artifacts": {
                "output_dir": str(artifacts.output_dir),
                "transcript_txt": str(artifacts.transcript_txt),
                "transcript_json": str(artifacts.transcript_json),
                "speaker_transcript_md": str(artifacts.speaker_transcript_md),
                "organized_notes_md": str(artifacts.organized_notes_md),
                "run_manifest_json": str(artifacts.run_manifest_json),
            },
            "info": info.to_dict(),
        },
    )

    return PipelineResult(
        audio_path=audio_path,
        artifacts=artifacts,
        info=info,
        segments=segments,
        speaker_turns=speaker_turns,
    )
