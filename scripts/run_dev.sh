#!/usr/bin/env bash
# Prefer using the project's virtualenv uvicorn if available (works when venv not activated)
if [ -x ".venv/bin/uvicorn" ]; then
  .venv/bin/uvicorn api.main:app --reload "$@"
else
  uvicorn api.main:app --reload "$@"
fi
