#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: ./scripts/alembic_autogenerate.sh \"mensagem\""
  exit 1
fi

MESSAGE="$1"

alembic revision --autogenerate -m "$MESSAGE"
