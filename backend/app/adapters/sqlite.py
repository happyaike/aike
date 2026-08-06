"""SQLite database adapter."""

import sqlite3
import asyncio
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urlparse
from datetime import datetime, date

from app.adapters.base import (
    DatabaseAdapter,
    ConnectionConfig,
    QueryResult,
    MetadataResult,
)


def _parse_sqlite_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    if path.startswith("/"):
        path = path[1:]
    if not path:
        path = ":memory:"
    return path


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter using built-in sqlite3."""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._db_path = _parse_sqlite_url(config.url)
        self._conn: Optional[sqlite3.Connection] = None
        self._loop = asyncio.get_event_loop()

    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        try:
            path = _parse_sqlite_url(self.config.url)
            conn = sqlite3.connect(path)
            conn.execute("SELECT 1")
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)

    async def get_connection_pool(self) -> sqlite3.Connection:
        if self._conn is None:
            path = _parse_sqlite_url(self.config.url)
            self._conn = sqlite3.connect(path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    async def close_connection_pool(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    async def extract_metadata(self) -> MetadataResult:
        conn = await self.get_connection_pool()

        tables_query = """
            SELECT name, type FROM sqlite_master
            WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        rows = conn.execute(tables_query).fetchall()

        tables: List[Dict[str, Any]] = []
        views: List[Dict[str, Any]] = []

        for row in rows:
            obj_name = row["name"]
            obj_type = row["type"]

            columns = await self._get_columns(conn, obj_name)
            row_count = None
            if obj_type == "table":
                try:
                    count = conn.execute(f'SELECT COUNT(*) as cnt FROM "{obj_name}"').fetchone()
                    row_count = count["cnt"]
                except Exception:
                    pass

            table_meta = {
                "name": obj_name,
                "type": "table" if obj_type == "table" else "view",
                "schemaName": "main",
                "columns": columns,
            }
            if row_count is not None:
                table_meta["rowCount"] = row_count

            if obj_type == "table":
                tables.append(table_meta)
            else:
                views.append(table_meta)

        return MetadataResult(tables=tables, views=views)

    async def _get_columns(
        self, conn: sqlite3.Connection, table_name: str
    ) -> List[Dict[str, Any]]:
        pragma = f'PRAGMA table_info("{table_name}")'
        cols = conn.execute(pragma).fetchall()

        columns: List[Dict[str, Any]] = []
        for col in cols:
            column_meta = {
                "name": col["name"],
                "dataType": col["type"] or "TEXT",
                "nullable": col["notnull"] == 0,
                "primaryKey": col["pk"] > 0,
                "unique": False,
                "defaultValue": col["dflt_value"],
            }
            columns.append(column_meta)

        return columns

    async def execute_query(self, sql: str) -> QueryResult:
        conn = await self.get_connection_pool()

        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        description = cursor.description

        columns: List[Dict[str, str]] = []
        result_rows: List[Dict[str, Any]] = []

        if description:
            for desc in description:
                col_name = desc[0]
                col_type = "TEXT"
                columns.append({"name": col_name, "dataType": col_type})

        for row in rows:
            processed_row = {}
            for key in row.keys():
                value = row[key]
                if isinstance(value, datetime):
                    processed_row[key] = value.isoformat()
                elif isinstance(value, date):
                    processed_row[key] = value.isoformat()
                else:
                    processed_row[key] = value
            result_rows.append(processed_row)

        return QueryResult(
            columns=columns,
            rows=result_rows,
            row_count=len(result_rows),
        )

    def get_dialect_name(self) -> str:
        return "sqlite"

    def get_identifier_quote_char(self) -> str:
        return '"'
