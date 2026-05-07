from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import os
from typing import Iterator

import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/juridicotech")
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    connection = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield connection
    finally:
        connection.close()


def init_schema() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
