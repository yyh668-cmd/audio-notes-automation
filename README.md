# Audio Notes Automation

`audio-notes-automation` is a local-first workflow for turning audio files into structured study materials. It transcribes common audio formats, optionally diarizes speakers, and produces grounded organized notes plus reusable transcript artifacts.

## What It Does

- Transcribes audio with `faster-whisper`
- Accepts multiple formats supported by FFmpeg/PyAV decoders, including `wma`, `mp3`, `m4a`, `wav`, and `mp4`
- Labels speakers with `pyannote.audio` when Hugging Face diarization credentials are configured
- Falls back to a single-speaker label when diarization is unavailable, so the pipeline still completes
- Generates:
  - raw timestamped transcript
  - speaker-formatted transcript
  - organized notes
  - run manifest JSON
- Can optionally use OpenAI to produce cleaner organized notes while remaining grounded to the transcript

## Detailed Steps

### 1. Prepare the environment

```powershell
python -m pip install -e .
```

Optional diarization dependencies:

```powershell
python -m pip install -e .[diarization]
```

### 2. Configure optional credentials

For speaker diarization:

```powershell
$env:HF_TOKEN = "your_huggingface_token"
```

For OpenAI-backed note generation:

```powershell
$env:OPENAI_API_KEY = "your_openai_api_key"
```

### 3. Run the pipeline

```powershell
audio-notes-automation run "C:\path\to\lecture.wma" --language en --notes-backend extractive
```

If diarization is configured:

```powershell
audio-notes-automation run "C:\path\to\lecture.m4a" --language en --diarize
```

If you want OpenAI-generated organized notes:

```powershell
audio-notes-automation run "C:\path\to\lecture.mp3" --notes-backend openai --openai-model gpt-5-mini
```

### 4. Review the outputs

The command creates an artifact directory next to the source audio:

- `transcript.txt`
- `transcript.json`
- `speaker_transcript.md`
- `organized_notes.md`
- `run_manifest.json`

### 5. Install or reuse the bundled Codex skill

The repository includes a Codex skill at `skills/audio-notes-automation/SKILL.md`. The skill tells Codex how to run the pipeline, what outputs to expect, and where to look for setup details.

## Project Layout

```text
src/audio_notes_automation/
  cli.py
  diarization.py
  models.py
  notes.py
  pipeline.py
  transcription.py
  utils.py
skills/audio-notes-automation/
  SKILL.md
  agents/openai.yaml
  references/setup.md
  scripts/run_audio_notes.py
```

## How the Automation Works

1. Load the audio file.
2. Transcribe it with `faster-whisper`.
3. If diarization is enabled and credentials exist, run `pyannote.audio`.
4. Align transcript segments to speaker turns.
5. Render transcript artifacts.
6. Generate organized notes using either:
   - `extractive` mode: purely transcript-driven sectioning
   - `openai` mode: grounded note generation from the transcript

## Current Validation

The project has been validated locally on the `Unit 3.wma` lecture in this workspace with:

- transcription enabled
- single-speaker fallback labeling
- extractive organized notes generation

Speaker diarization was not fully validated in this workspace because no Hugging Face diarization token is configured.

## GitHub Publishing Checklist

1. Create a new GitHub repository named `audio-notes-automation`.
2. Add this folder as the repository root.
3. Commit the project files.
4. Add your remote.
5. Push the branch.

Example:

```powershell
git init
git add .
git commit -m "Initial commit for audio notes automation"
git branch -M main
git remote add origin https://github.com/<your-account>/audio-notes-automation.git
git push -u origin main
```

