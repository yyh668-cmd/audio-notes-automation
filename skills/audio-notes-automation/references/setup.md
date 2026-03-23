# Setup Notes

## Purpose

This repository pipeline has three layers:

1. transcription with `faster-whisper`
2. optional speaker diarization with `pyannote.audio`
3. organized notes generation with either extractive logic or OpenAI

## Install

From the repository root:

```powershell
python -m pip install -e .
```

Optional diarization extras:

```powershell
python -m pip install -e .[diarization]
```

## Credentials

Speaker diarization needs a Hugging Face token:

```powershell
$env:HF_TOKEN = "your_token"
```

OpenAI notes generation needs an API key:

```powershell
$env:OPENAI_API_KEY = "your_key"
```

## Commands

Basic grounded run:

```powershell
python .\skills\audio-notes-automation\scripts\run_audio_notes.py run "C:\path\to\audio.wma" --notes-backend extractive
```

Diarization-enabled run:

```powershell
python .\skills\audio-notes-automation\scripts\run_audio_notes.py run "C:\path\to\meeting.m4a" --diarize
```

OpenAI notes run:

```powershell
python .\skills\audio-notes-automation\scripts\run_audio_notes.py run "C:\path\to\lecture.mp3" --notes-backend openai --openai-model gpt-5-mini
```

## Artifact Contract

Every successful run should leave:

- `transcript.txt`
- `transcript.json`
- `speaker_transcript.md`
- `organized_notes.md`
- `run_manifest.json`

