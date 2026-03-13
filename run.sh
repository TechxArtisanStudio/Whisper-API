#!/bin/bash
# Run Whisper API server on 0.0.0.0 (share across network)
cd "$(dirname "$0")"

# Load PORT from .env if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi
PORT="${PORT:-9876}"

# Get local IP for display
get_local_ip() {
  python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 1))
    print(s.getsockname()[0])
except Exception:
    print('127.0.0.1')
finally:
    s.close()
" 2>/dev/null || echo "127.0.0.1"
}

LOCAL_IP=$(get_local_ip)

echo "=========================================="
echo "  Whisper API"
echo "=========================================="
echo "  Host: 0.0.0.0 (all interfaces)"
echo "  Port: $PORT"
echo ""
echo "  Local:    http://localhost:$PORT"
echo "  Swagger:  http://localhost:$PORT/docs"
echo "  Network:  http://$LOCAL_IP:$PORT"
echo "=========================================="
echo ""

uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
