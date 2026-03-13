"""
Core transcription logic: convert media to WAV, load Whisper, transcribe, format output.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Union

import whisper

import config

# Cached models: model_name -> loaded model
_model_cache: dict[str, whisper.Whisper] = {}

ALLOWED_MODELS = ("base", "large-v3")

# Per-model path overrides from config (project root .env)
_MODEL_PATHS = {
    "base": config.WHISPER_MODEL_BASE,
    "large-v3": config.WHISPER_MODEL_LARGE_V3,
}


def convert_to_wav(input_file: str, wav_path: str) -> None:
    """
    Extract audio from video/audio file and convert to WAV using ffmpeg.
    Supports any format that ffmpeg can handle.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-loglevel",
        "error",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr or result.stdout}")


def _get_model(model_name: str) -> whisper.Whisper:
    if model_name not in ALLOWED_MODELS:
        raise ValueError(f"Model must be one of {ALLOWED_MODELS}, got: {model_name}")
    if model_name not in _model_cache:
        path = _MODEL_PATHS.get(model_name)
        if path:
            # Per-model path: load from .pt file directly
            _model_cache[model_name] = whisper.load_model(path)
        else:
            # Use model name; download_root from config if set
            kwargs = {}
            if config.WHISPER_MODEL_ROOT:
                kwargs["download_root"] = config.WHISPER_MODEL_ROOT
            _model_cache[model_name] = whisper.load_model(model_name, **kwargs)
    return _model_cache[model_name]


def segments_to_srt(segments: list[dict]) -> str:
    """Generate SRT string from Whisper transcription segments."""
    lines: list[str] = []
    for i, segment in enumerate(segments, 1):
        start_time = segment["start"]
        end_time = segment["end"]
        start_srt = (
            f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{start_time % 60:06.3f}".replace(
                ".", ","
            )
        )
        end_srt = (
            f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{end_time % 60:06.3f}".replace(
                ".", ","
            )
        )
        text = segment.get("text", "").strip()
        lines.append(f"{i}\n{start_srt} --> {end_srt}\n{text}\n")
    return "\n".join(lines)


def segments_to_text(segments: list[dict]) -> str:
    """Generate plain text from Whisper transcription segments (no timestamps)."""
    return "\n".join(segment.get("text", "").strip() for segment in segments)


def transcribe(
    input_path: str,
    model_name: str = "base",
    language: Union[str, None] = None,
    output_format: Literal["srt", "text"] = "text",
) -> tuple[str, list[dict]]:
    """
    Transcribe media file and return formatted output plus raw segments.

    Args:
        input_path: Path to audio/video file.
        model_name: Whisper model (base or large-v3).
        language: Optional language code (e.g. en, zh). None = auto-detect.
        output_format: 'srt' or 'text'.

    Returns:
        (formatted_output, segments)
    """
    model = _get_model(model_name)
    opts: dict = {"verbose": False}
    if language:
        opts["language"] = language

    # Always convert to WAV for consistency (handles any ffmpeg-supported format)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
    try:
        convert_to_wav(input_path, wav_path)
        result = model.transcribe(wav_path, **opts)
    finally:
        Path(wav_path).unlink(missing_ok=True)

    segments = result.get("segments", [])

    if output_format == "srt":
        output = segments_to_srt(segments)
    else:
        output = segments_to_text(segments)

    return output, segments
