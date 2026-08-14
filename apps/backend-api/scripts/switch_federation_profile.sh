#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
ENV_EXAMPLE_FILE="${ROOT_DIR}/.env.example"

usage() {
  cat <<'EOF'
Uso:
  ./scripts/switch_federation_profile.sh <local|auto|real> [--dry-run] [--no-backup]

Perfis:
  local  -> memory/memory/memory
  auto   -> auto/auto/auto
  real   -> redis/neo4j/otel

Opcoes:
  --dry-run    Exibe as alteracoes sem gravar no arquivo .env
  --no-backup  Nao cria backup .env.bak.<timestamp>
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

PROFILE="$1"
shift

DRY_RUN=false
NO_BACKUP=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --no-backup)
      NO_BACKUP=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Opcao desconhecida: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

case "$PROFILE" in
  local)
    MEMORY_BACKEND="memory"
    GRAPH_BACKEND="memory"
    OBS_BACKEND="memory"
    ;;
  auto)
    MEMORY_BACKEND="auto"
    GRAPH_BACKEND="auto"
    OBS_BACKEND="auto"
    ;;
  real)
    MEMORY_BACKEND="redis"
    GRAPH_BACKEND="neo4j"
    OBS_BACKEND="otel"
    ;;
  *)
    echo "Perfil invalido: $PROFILE" >&2
    usage
    exit 1
    ;;
esac

TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

WORK_FILE="$ENV_FILE"

if [[ "$DRY_RUN" == "true" ]]; then
  if [[ -f "$ENV_FILE" ]]; then
    cp "$ENV_FILE" "$TMP_FILE"
  elif [[ -f "$ENV_EXAMPLE_FILE" ]]; then
    cp "$ENV_EXAMPLE_FILE" "$TMP_FILE"
  else
    : > "$TMP_FILE"
  fi
  WORK_FILE="$TMP_FILE"
else
  if [[ ! -f "$ENV_FILE" ]]; then
    if [[ -f "$ENV_EXAMPLE_FILE" ]]; then
      cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
      echo "Criado .env a partir de .env.example"
    else
      touch "$ENV_FILE"
      echo "Criado .env vazio"
    fi
  fi

  if [[ "$NO_BACKUP" != "true" ]]; then
    TS="$(date +%Y%m%d%H%M%S)"
    cp "$ENV_FILE" "${ENV_FILE}.bak.${TS}"
    echo "Backup criado: .env.bak.${TS}"
  fi
fi

set_kv() {
  local file="$1"
  local key="$2"
  local value="$3"
  local update_tmp
  update_tmp="$(mktemp)"

  if grep -Eq "^[[:space:]]*${key}=" "$file"; then
    awk -v k="$key" -v v="$value" '
      BEGIN { replaced=0 }
      {
        if ($0 ~ "^[[:space:]]*" k "=" && replaced==0) {
          print k "=" v
          replaced=1
        } else {
          print $0
        }
      }
    ' "$file" > "$update_tmp"
    mv "$update_tmp" "$file"
  else
    printf "\n%s=%s\n" "$key" "$value" >> "$file"
    rm -f "$update_tmp"
  fi
}

set_kv "$WORK_FILE" "FEDERATION_MEMORY_BACKEND" "$MEMORY_BACKEND"
set_kv "$WORK_FILE" "FEDERATION_GRAPH_BACKEND" "$GRAPH_BACKEND"
set_kv "$WORK_FILE" "FEDERATION_OBSERVABILITY_BACKEND" "$OBS_BACKEND"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] Perfil alvo: $PROFILE"
  grep -E "^FEDERATION_(MEMORY|GRAPH|OBSERVABILITY)_BACKEND=" "$WORK_FILE" | cat
  exit 0
fi

echo "Perfil aplicado: $PROFILE"
grep -E "^FEDERATION_(MEMORY|GRAPH|OBSERVABILITY)_BACKEND=" "$ENV_FILE" | cat
