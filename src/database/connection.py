"""
Database connection utilities with context manager support.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator


@contextmanager
def get_database_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with automatic commit/rollback.
    
    Args:
        db_path: Path to the SQLite database file
        
    Yields:
        sqlite3.Connection: Database connection
        
    Example:
        with get_database_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos")
            results = cursor.fetchall()
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def execute_query(db_path: str, query: str, params: tuple = ()) -> list:
    """
    Execute a SELECT query and return results.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        params: Query parameters
        
    Returns:
        List of query results
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_insert(db_path: str, query: str, params: tuple = ()) -> None:
    """
    Execute an INSERT/UPDATE/DELETE query.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        params: Query parameters
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)


def execute_many(db_path: str, query: str, params_list: list) -> None:
    """
    Execute a query with multiple parameter sets.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        params_list: List of parameter tuples
    """
    with get_database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)