#!/bin/bash
# Test Whisper API with sample file
set -e
BASE="${1:-http://127.0.0.1:9876}"
FILE="${2:-input/yangyang.aac}"

echo "=== Health check ==="
curl -s "$BASE/health" | jq .

echo -e "\n=== Models ==="
curl -s "$BASE/models" | jq .

echo -e "\n=== Transcribe to text (base) ==="
curl -s -X POST "$BASE/transcribe" -F "file=@$FILE" -F "model=base" -F "output_format=text" | jq -r '.text' | head -5

echo -e "\n=== Transcribe to SRT (base) ==="
curl -s -X POST "$BASE/transcribe" -F "file=@$FILE" -F "model=base" -F "output_format=srt" | jq -r '.srt' | head -20

echo -e "\n=== All tests passed ==="
