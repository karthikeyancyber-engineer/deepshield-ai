#!/bin/sh
set -e

cd /app/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 5

cd /app/frontend
PORT=${PORT:-10000} npx next start -p ${PORT:-10000} -H 0.0.0.0 &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGTERM SIGINT

wait
