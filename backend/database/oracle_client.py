"""Oracle Database client for VacanceAI"""

import oracledb
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config import settings


# Connection pool (initialized at startup)
_pool: Optional[oracledb.ConnectionPool] = None


def init_pool():
    """Initialize the Oracle connection pool."""
    global _pool
    _pool = oracledb.create_pool(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=f"{settings.oracle_host}:{settings.oracle_port}/{settings.oracle_service}",
        min=2,
        max=10,
        increment=1,
        mode=oracledb.SYSDBA if settings.oracle_user.upper() == "SYS" else 0,
    )
    print(f"Oracle pool initialized: {settings.oracle_host}:{settings.oracle_port}/{settings.oracle_service}")


def close_pool():
    """Close the Oracle connection pool."""
    global _pool
    if _pool:
        _pool.close()
        _pool = None
        print("Oracle pool closed")


@contextmanager
def get_db_connection():
    """Get a database connection from the pool with auto-commit/rollback."""
    conn = _pool.acquire()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.release(conn)


def _rows_to_dicts(cursor) -> List[Dict[str, Any]]:
    """Convert cursor results to list of dicts with lowercase column names."""
    if cursor.description is None:
        return []
    columns = [col[0].lower() for col in cursor.description]
    rows = cursor.fetchall()
    result = []
    for row in rows:
        d = {}
        for col_name, value in zip(columns, row):
            # Read CLOB values as strings
            if hasattr(value, 'read'):
                value = value.read()
            d[col_name] = value
        result.append(d)
    return result


def execute_query(sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        return _rows_to_dicts(cursor)


def execute_query_single(sql: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Execute a SELECT query and return a single result or None."""
    results = execute_query(sql, params)
    return results[0] if results else None


def execute_insert(sql: str, params: Optional[Dict] = None, returning: Optional[str] = None) -> Optional[str]:
    """Execute an INSERT and optionally return a generated value.

    If returning is specified, uses RETURNING INTO to get the generated value.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if returning:
            out_var = cursor.var(oracledb.STRING)
            sql_with_returning = f"{sql} RETURNING {returning} INTO :out_id"
            params = params or {}
            params["out_id"] = out_var
            cursor.execute(sql_with_returning, params)
            return out_var.getvalue()[0]
        else:
            cursor.execute(sql, params or {})
            return None


def execute_insert_returning_row(sql: str, params: Optional[Dict] = None, table: str = None, id_col: str = "id") -> Optional[Dict[str, Any]]:
    """Execute an INSERT, return the generated ID, then fetch the full row."""
    generated_id = execute_insert(sql, params, returning=id_col)
    if generated_id and table:
        return execute_query_single(f"SELECT * FROM {table} WHERE {id_col} = :id", {"id": generated_id})
    return None


def execute_update(sql: str, params: Optional[Dict] = None) -> int:
    """Execute an UPDATE and return the number of rows affected."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        return cursor.rowcount


def execute_delete(sql: str, params: Optional[Dict] = None) -> int:
    """Execute a DELETE and return the number of rows affected."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        return cursor.rowcount


def execute_scalar(sql: str, params: Optional[Dict] = None) -> Any:
    """Execute a query and return a single scalar value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        row = cursor.fetchone()
        if row:
            value = row[0]
            if hasattr(value, 'read'):
                value = value.read()
            return value
        return None
