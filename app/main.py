"""
Whisper API server: transcribe audio/video to SRT or plain text.
"""
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.transcribe import ALLOWED_MODELS, transcribe

app = FastAPI(
    title="Whisper API",
    description="Transcribe audio/video to SRT or plain text using local Whisper models (base, large-v3)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Response schemas for Swagger
class HealthResponse(BaseModel):
    status: str


class ModelsResponse(BaseModel):
    models: list[str]


class TranscribeResponse(BaseModel):
    text: str | None = None
    srt: str | None = None
    segments: list[dict]


MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/models", response_model=ModelsResponse, tags=["System"])
def models():
    """List available Whisper models (base, large-v3)."""
    return {"models": list(ALLOWED_MODELS)}


@app.post(
    "/transcribe",
    response_model=TranscribeResponse,
    tags=["Transcription"],
)
async def transcribe_endpoint(
    file: UploadFile = File(..., description="Audio or video file (any format supported by ffmpeg)"),
    model: str = Form("base", description="Whisper model: base or large-v3"),
    output_format: str = Form("text", description="Output format: srt (with timestamps) or text (plain)"),
    language: str | None = Form(None, description="Language code (e.g. en, zh). Omit for auto-detect."),
):
    """
    Transcribe uploaded audio/video file to text or SRT subtitles.
    """
    if model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"model must be one of {list(ALLOWED_MODELS)}, got: {model}",
        )
    if output_format not in ("srt", "text"):
        raise HTTPException(
            status_code=400,
            detail="output_format must be 'srt' or 'text'",
        )

    # Read upload with size limit
    content = b""
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 500MB)")
        content += chunk

    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    suffix = Path(file.filename or "audio").suffix or ".bin"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(content)
        input_path = f.name

    try:
        output, segments = transcribe(
            input_path=input_path,
            model_name=model,
            language=language,
            output_format=output_format,
        )
    except RuntimeError as e:
        if "ffmpeg" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Invalid or unsupported media: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(input_path).unlink(missing_ok=True)

    if output_format == "srt":
        return JSONResponse(
            content={"srt": output, "segments": segments},
            media_type="application/json",
        )
    return JSONResponse(content={"text": output, "segments": segments})
