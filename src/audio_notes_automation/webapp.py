from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import streamlit as st

from .pipeline import run_pipeline


@contextmanager
def temporary_environment(overrides: dict[str, str | None]):
    previous: dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            if value:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(30, 136, 229, 0.14), transparent 30%),
                radial-gradient(circle at top right, rgba(255, 152, 0, 0.12), transparent 28%),
                linear-gradient(180deg, #f7f4ee 0%, #f4efe7 100%);
        }
        .ana-hero {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(33, 33, 33, 0.08);
            border-radius: 20px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 18px 40px rgba(62, 39, 35, 0.08);
            margin-bottom: 1rem;
        }
        .ana-tag {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: #0d47a1;
            color: white;
            font-size: 0.8rem;
            letter-spacing: 0.04em;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _save_uploaded_file(uploaded_file, working_dir: Path) -> Path:
    suffix = Path(uploaded_file.name).suffix or ".bin"
    target_path = working_dir / f"uploaded_audio{suffix}"
    target_path.write_bytes(uploaded_file.getbuffer())
    return target_path


def render_app() -> None:
    st.set_page_config(
        page_title="Audio Notes Automation",
        page_icon="🎧",
        layout="wide",
    )
    _inject_styles()

    st.markdown(
        """
        <div class="ana-hero">
            <div class="ana-tag">AUDIO NOTES AUTOMATION</div>
            <h1 style="margin: 0;">Transcribe audio, label speakers, and generate organized notes</h1>
            <p style="margin: 0.6rem 0 0 0;">
                Upload a lecture, interview, or meeting recording. The app will run the existing pipeline,
                then show the transcript, speaker transcript, organized notes, and downloadable artifacts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Run Settings")
        whisper_model = st.selectbox("Whisper model", ["small", "small.en", "medium", "medium.en"], index=0)
        language = st.text_input("Language hint", value="en", help="Leave blank to auto-detect.")
        diarize = st.toggle("Enable speaker diarization", value=True)
        notes_backend = st.selectbox("Notes backend", ["extractive", "auto", "openai"], index=0)
        openai_model = st.text_input("OpenAI notes model", value="gpt-5-mini")
        hf_token = st.text_input("HF_TOKEN (optional)", type="password")
        openai_api_key = st.text_input("OPENAI_API_KEY (optional)", type="password")
        st.caption("If diarization dependencies or tokens are missing, the app will fall back to SPEAKER_00.")

    uploaded_file = st.file_uploader(
        "Upload an audio file",
        type=["wma", "mp3", "m4a", "wav", "mp4", "aac", "flac"],
        accept_multiple_files=False,
    )

    if uploaded_file is None:
        st.info("Upload an audio file to begin.")
        return

    st.write(f"Selected file: `{uploaded_file.name}`")

    if not st.button("Process audio", type="primary", use_container_width=True):
        return

    working_dir = Path(tempfile.mkdtemp(prefix="audio_notes_web_"))
    audio_path = _save_uploaded_file(uploaded_file, working_dir)
    output_dir = working_dir / "artifacts"

    env_overrides = {
        "HF_TOKEN": hf_token.strip() or None,
        "OPENAI_API_KEY": openai_api_key.strip() or None,
    }

    with st.spinner("Running transcription pipeline. This can take a while for longer audio files."):
        with temporary_environment(env_overrides):
            result = run_pipeline(
                audio_path,
                output_dir=output_dir,
                whisper_model=whisper_model,
                language=language.strip() or None,
                device="cpu",
                compute_type="int8",
                beam_size=5,
                vad_filter=True,
                diarize=diarize,
                diarization_model="pyannote/speaker-diarization-3.1",
                hf_token=hf_token.strip() or None,
                hf_token_env="HF_TOKEN",
                fallback_speaker="SPEAKER_00",
                notes_backend=notes_backend,
                openai_model=openai_model.strip() or "gpt-5-mini",
                openai_api_key_env="OPENAI_API_KEY",
            )

    transcript_text = result.artifacts.transcript_txt.read_text(encoding="utf-8")
    speaker_transcript = result.artifacts.speaker_transcript_md.read_text(encoding="utf-8")
    organized_notes = result.artifacts.organized_notes_md.read_text(encoding="utf-8")
    manifest_json = result.artifacts.run_manifest_json.read_text(encoding="utf-8")

    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("Language", result.info.language)
    metric_two.metric("Duration (s)", f"{result.info.duration:.2f}")
    metric_three.metric("Diarization", result.info.diarization_backend)

    st.success("Processing finished.")

    tab_notes, tab_speakers, tab_transcript, tab_manifest = st.tabs(
        ["Organized Notes", "Speaker Transcript", "Transcript", "Manifest"]
    )

    with tab_notes:
        st.markdown(organized_notes)
        st.download_button(
            "Download organized notes",
            data=organized_notes,
            file_name="organized_notes.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tab_speakers:
        st.markdown(speaker_transcript)
        st.download_button(
            "Download speaker transcript",
            data=speaker_transcript,
            file_name="speaker_transcript.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tab_transcript:
        st.code(transcript_text, language="text")
        st.download_button(
            "Download transcript",
            data=transcript_text,
            file_name="transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab_manifest:
        st.code(manifest_json, language="json")
        st.download_button(
            "Download manifest",
            data=manifest_json,
            file_name="run_manifest.json",
            mime="application/json",
            use_container_width=True,
        )
