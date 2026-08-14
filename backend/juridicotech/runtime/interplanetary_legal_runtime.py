"""Interplanetary Legal Runtime launcher.

Permite executar o runtime principal com o comando pedido:
python runtime/interplanetary_legal_runtime.py
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

import uvicorn


def _bootstrap_import_path() -> None:
    # Garante que "backend" esteja no sys.path para resolver "app.main".
    backend_root = Path(__file__).resolve().parents[2]
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)


def main() -> None:
    _bootstrap_import_path()

    host = os.getenv("LEGAL_RUNTIME_HOST", "0.0.0.0")
    port = int(os.getenv("LEGAL_RUNTIME_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
