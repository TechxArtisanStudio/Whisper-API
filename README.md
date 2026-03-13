# Whisper API

HTTP API server for local Whisper transcription. Accepts any audio/video format and returns SRT or plain text.

## Requirements

- Python 3.10+
- ffmpeg (must be installed and on PATH)
- ~1GB RAM for `base`, ~10GB for `large-v3`

## Model location (configurable)

Create `.env` in the project root (copy from `.env.example`):

- **WHISPER_MODEL_ROOT** – Directory containing `base.pt`, `large-v3.pt`, etc. (default: `models/` at project root)
- **WHISPER_MODEL_BASE** – Full path to `base.pt` (overrides MODEL_ROOT for base)
- **WHISPER_MODEL_LARGE_V3** – Full path to `large-v3.pt` (overrides MODEL_ROOT for large-v3)

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
./run.sh
```

Serves on `0.0.0.0` (shareable on network). Prints local and network URLs.

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9876
```

## Endpoints

- `GET /health` - Health check
- `GET /models` - List models (base, large-v3)
- `POST /transcribe` - Transcribe file (multipart form)

**Swagger UI:** http://localhost:9876/docs  
**ReDoc:** http://localhost:9876/redoc  
**OpenAPI JSON:** http://localhost:9876/openapi.json

### Transcribe

```bash
curl -X POST "http://localhost:9876/transcribe" \
  -F "file=@input/yangyang.aac" \
  -F "model=base" \
  -F "output_format=text"
```

Options:
- `file` (required): Audio/video file
- `model`: `base` or `large-v3` (default: base)
- `output_format`: `srt` or `text` (default: text)
- `language`: Optional, e.g. `en`, `zh` (omit for auto-detect)

## Test

```bash
# Start server first: ./run.sh
./test_transcribe.sh
```

Save SRT to file:
```bash
curl -s -X POST "http://localhost:9876/transcribe" -F "file=@input/yangyang.aac" -F "model=base" -F "output_format=srt" | jq -r '.srt' > output/yangyang.srt
```
