---
name: audio-notes-automation
description: Use this skill when you need to transcribe audio or video into source-grounded text, label speakers when diarization is configured, and generate organized notes or study-ready artifacts from files such as wma, mp3, wav, m4a, or mp4.
---

# Audio Notes Automation

## Overview

This skill runs the repository pipeline that converts an audio file into transcript artifacts, speaker-attributed transcript markdown, and organized notes. Use it for lecture recordings, interviews, meetings, and study materials where you need repeatable extraction rather than ad hoc prompting.

## Workflow

1. Confirm the input file path and desired output directory.
2. Read [references/setup.md](./references/setup.md) only if dependency or credential details are needed.
3. Run [scripts/run_audio_notes.py](./scripts/run_audio_notes.py) so the repository `src/` package is used directly.
4. Report the generated artifact paths.
5. If diarization is unavailable, say the run completed with single-speaker fallback instead of implying multi-speaker labeling succeeded.

## Default Command

```powershell
python .\skills\audio-notes-automation\scripts\run_audio_notes.py run "C:\path\to\audio.wma"
```

Common options:

- `--language en`
- `--output-dir C:\path\to\artifacts`
- `--diarize` or `--no-diarize`
- `--notes-backend extractive`
- `--notes-backend openai --openai-model gpt-5-mini`

## Outputs

Expect these files in the artifact directory:

- `transcript.txt`
- `transcript.json`
- `speaker_transcript.md`
- `organized_notes.md`
- `run_manifest.json`

## Failure Modes

- If `pyannote.audio` is not installed or no `HF_TOKEN` is available, the pipeline falls back to a single speaker label such as `SPEAKER_00`.
- If `OPENAI_API_KEY` is missing and notes backend is `auto`, the pipeline falls back to extractive notes.
- If the audio file lives in a non-ASCII path and any third-party decoder fails, copy it to an ASCII-only path and rerun.

## References

- Read [references/setup.md](./references/setup.md) for setup, environment variables, and example commands.
- Use [scripts/run_audio_notes.py](./scripts/run_audio_notes.py) instead of retyping the module invocation manually.

