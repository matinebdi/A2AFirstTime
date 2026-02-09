"""Database module for VacanceAI - Oracle"""
from .oracle_client import init_pool, close_pool, execute_query, execute_query_single, execute_insert, execute_update, execute_delete

__all__ = ["init_pool", "close_pool", "execute_query", "execute_query_single", "execute_insert", "execute_update", "execute_delete"]
