"""Custom SQLAlchemy types for Oracle 21c"""

import json
from typing import Any, Optional

from sqlalchemy import Numeric, types
from sqlalchemy.dialects.oracle import CLOB


class JSONEncodedCLOB(types.TypeDecorator):
    """Stores JSON as CLOB in Oracle, deserializes to Python dict/list."""

    impl = CLOB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if hasattr(value, "read"):
            value = value.read()
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value


class OracleBoolean(types.TypeDecorator):
    """Maps Python bool to Oracle NUMBER(1)."""

    impl = Numeric(1, 0)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return 1 if value else 0

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return bool(value)
