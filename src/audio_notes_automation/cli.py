from __future__ import annotations

from pathlib import Path

import typer

from .pipeline import run_pipeline

app = typer.Typer(add_completion=False, help="Transcribe audio, label speakers, and generate organized notes.")


@app.callback()
def main() -> None:
    """Command group for audio notes automation."""


@app.command()
def run(
    audio_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
    output_dir: Path | None = typer.Option(None, help="Directory for generated artifacts."),
    whisper_model: str = typer.Option("small", help="faster-whisper model name."),
    language: str | None = typer.Option(None, help="Language hint such as en or zh."),
    device: str = typer.Option("cpu", help="Execution device for transcription and diarization."),
    compute_type: str = typer.Option("int8", help="Whisper compute type."),
    beam_size: int = typer.Option(5, help="Beam size for transcription."),
    vad_filter: bool = typer.Option(True, help="Enable VAD filtering."),
    diarize: bool = typer.Option(True, "--diarize/--no-diarize", help="Enable speaker diarization when available."),
    diarization_model: str = typer.Option(
        "pyannote/speaker-diarization-3.1",
        help="Hugging Face diarization model identifier.",
    ),
    hf_token: str | None = typer.Option(None, help="Optional Hugging Face access token."),
    hf_token_env: str = typer.Option("HF_TOKEN", help="Environment variable checked for the HF token."),
    fallback_speaker: str = typer.Option("SPEAKER_00", help="Speaker label used when diarization is unavailable."),
    notes_backend: str = typer.Option("extractive", help="Notes backend: extractive, openai, or auto."),
    openai_model: str = typer.Option("gpt-5-mini", help="OpenAI model for note generation."),
    openai_api_key_env: str = typer.Option("OPENAI_API_KEY", help="Environment variable checked for the OpenAI API key."),
) -> None:
    result = run_pipeline(
        audio_path,
        output_dir=output_dir,
        whisper_model=whisper_model,
        language=language,
        device=device,
        compute_type=compute_type,
        beam_size=beam_size,
        vad_filter=vad_filter,
        diarize=diarize,
        diarization_model=diarization_model,
        hf_token=hf_token,
        hf_token_env=hf_token_env,
        fallback_speaker=fallback_speaker,
        notes_backend=notes_backend,
        openai_model=openai_model,
        openai_api_key_env=openai_api_key_env,
    )

    typer.echo(f"Audio: {result.audio_path}")
    typer.echo(f"Transcript: {result.artifacts.transcript_txt}")
    typer.echo(f"Speaker transcript: {result.artifacts.speaker_transcript_md}")
    typer.echo(f"Organized notes: {result.artifacts.organized_notes_md}")
    typer.echo(f"Manifest: {result.artifacts.run_manifest_json}")
    typer.echo(f"Transcription backend: {result.info.transcription_backend}")
    typer.echo(f"Diarization backend: {result.info.diarization_backend}")
    typer.echo(f"Notes backend: {result.info.notes_backend}")


if __name__ == "__main__":
    app()
