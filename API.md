# Whisper API – Integration Guide

HTTP API for transcribing audio/video to text or SRT subtitles. Use this guide to integrate the API into your applications.

**Base URL:** `http://localhost:9876` (or your server host)

**Interactive docs:** `http://localhost:9876/docs` (Swagger UI)

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/models` | List available models |
| POST | `/transcribe` | Transcribe audio/video file |

---

## Health Check

**Request:**
```
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## List Models

**Request:**
```
GET /models
```

**Response:**
```json
{
  "models": ["base", "large-v3"]
}
```

---

## Transcribe

**Request:** `POST /transcribe` (multipart/form-data)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | file | Yes | — | Audio or video file (any format supported by ffmpeg: mp3, wav, aac, m4a, mp4, webm, etc.) |
| `model` | string | No | `base` | Whisper model: `base` or `large-v3` |
| `output_format` | string | No | `text` | Output format: `text` or `srt` |
| `language` | string | No | auto | Language code (e.g. `en`, `zh`, `ja`). Omit for auto-detect. |

**Limits:** Max file size 500 MB

### Response (output_format=text)

```json
{
  "text": "Transcribed plain text...",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "First segment..."
    }
  ]
}
```

### Response (output_format=srt)

```json
{
  "srt": "1\n00:00:00,000 --> 00:00:02,500\nFirst segment...\n\n2\n...",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "First segment..."
    }
  ]
}
```

### Error Response

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid model, format, empty file, unsupported media) |
| 413 | File too large (>500MB) |
| 500 | Server error (e.g. ffmpeg not found, transcription failed) |

```json
{
  "detail": "Error message"
}
```

---

## Example Calls

### cURL

```bash
# Plain text
curl -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=text"

# SRT with timestamps
curl -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=srt"

# Force Chinese
curl -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=text" \
  -F "language=zh"
```

### Save to file (cURL)

```bash
# Save full JSON response
curl -s -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=text" > output.json

# Save plain text only (requires jq)
curl -s -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=text" | jq -r '.text' > output.txt

# Save SRT to file (requires jq)
curl -s -X POST "http://localhost:9876/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "output_format=srt" | jq -r '.srt' > output.srt
```

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:9876"

# Transcribe to text
with open("audio.mp3", "rb") as f:
    r = requests.post(
        f"{BASE_URL}/transcribe",
        files={"file": ("audio.mp3", f, "audio/mpeg")},
        data={
            "model": "base",
            "output_format": "text",
            "language": "zh",  # optional
        },
    )
r.raise_for_status()
result = r.json()
print(result["text"])

# Transcribe to SRT
with open("audio.mp3", "rb") as f:
    r = requests.post(
        f"{BASE_URL}/transcribe",
        files={"file": ("audio.mp3", f, "audio/mpeg")},
        data={"model": "base", "output_format": "srt"},
    )
r.raise_for_status()
srt_content = r.json()["srt"]
```

### Python (httpx, async)

```python
import httpx

async def transcribe(file_path: str, output_format: str = "text"):
    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, "rb") as f:
            r = await client.post(
                "http://localhost:9876/transcribe",
                files={"file": (file_path, f)},
                data={"model": "base", "output_format": output_format},
            )
        r.raise_for_status()
        return r.json()
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("model", "base");
formData.append("output_format", "text");

const response = await fetch("http://localhost:9876/transcribe", {
  method: "POST",
  body: formData,
});

if (!response.ok) {
  const err = await response.json();
  throw new Error(err.detail || "Transcription failed");
}

const result = await response.json();
console.log(result.text);
```

### Node.js (fetch or axios)

```javascript
const FormData = require("form-data");
const fs = require("fs");
const fetch = require("node-fetch"); // or use native fetch in Node 18+

const form = new FormData();
form.append("file", fs.createReadStream("audio.mp3"));
form.append("model", "base");
form.append("output_format", "srt");

const response = await fetch("http://localhost:9876/transcribe", {
  method: "POST",
  body: form,
  headers: form.getHeaders(),
});

const result = await response.json();
console.log(result.srt);
```

---

## Model Comparison

| Model | Size | Speed | Accuracy | RAM |
|-------|------|-------|----------|-----|
| `base` | ~150MB | Fast | Good | ~1GB |
| `large-v3` | ~3GB | Slower | Best | ~10GB |

Use `base` for quick transcription; use `large-v3` when you need higher accuracy.
