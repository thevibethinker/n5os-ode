"""
Memory Capability — DB Helpers

Core database connection and generic query helpers.
All memory modules use this for DB access. No raw SQL should leak outside this package.
"""

from pathlib import Path

import duckdb
import yaml

_conn_cache: dict[str, duckdb.DuckDBPyConnection] = {}
_config_cache: dict | None = None


def _load_config() -> dict:
    """Load memory capability config."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    config_path = Path(__file__).resolve().parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            _config_cache = yaml.safe_load(f)
    else:
        _config_cache = {}
    return _config_cache


def get_db(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    """
    Get or create a DuckDB connection.

    Args:
        db_path: Override path to DB file. Defaults to config.yaml db_path.

    Returns:
        DuckDB connection object.
    """
    if db_path is None:
        cfg = _load_config()
        db_path = cfg.get("db_path", "Zoffice/data/office.db")

    p = Path(db_path)
    if not p.is_absolute():
        # Resolve relative to workspace root (3 levels up from this file)
        p = Path(__file__).resolve().parents[3] / db_path
    db_path = str(p)

    if db_path not in _conn_cache:
        _conn_cache[db_path] = duckdb.connect(db_path)
    return _conn_cache[db_path]


def execute_query(query: str, params: list | None = None, db_path: str | None = None) -> list[dict]:
    """
    Execute a query and return results as a list of dicts.

    Args:
        query: SQL query string with ? placeholders.
        params: Parameter list for the query.
        db_path: Override DB path.

    Returns:
        List of dicts for SELECT queries, empty list for INSERT/UPDATE/DELETE.
    """
    conn = get_db(db_path)
    if params:
        result = conn.execute(query, params)
    else:
        result = conn.execute(query)

    # For non-SELECT queries, return empty list
    if result.description is None:
        return []

    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def reset_cache() -> None:
    """Reset connection and config caches (for testing)."""
    global _conn_cache, _config_cache
    for conn in _conn_cache.values():
        try:
            conn.close()
        except Exception:
            pass
    _conn_cache.clear()
    _config_cache = None
