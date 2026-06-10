"""
N5 Database Connection Manager
==============================

Provides connection pooling and management for SQLite databases used across N5.

Features:
- Connection reuse (singleton pattern per database)
- Thread-safe connections via thread-local storage
- Context manager support for clean resource handling
- Automatic connection health checks
- Lazy initialization

Usage:
    # Simple usage - get a reusable connection
    from N5.lib.db import get_crm_db, get_brain_db

    conn = get_crm_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    # Connection stays open for reuse

    # Context manager - auto-commit on success, rollback on error
    from N5.lib.db import crm_transaction

    with crm_transaction() as conn:
        conn.execute("INSERT INTO profiles ...")
        # Auto-commits if no exception

    # Direct pool access for advanced use
    from N5.lib.db import DatabasePool

    pool = DatabasePool("/path/to/db.sqlite")
    with pool.connection() as conn:
        ...
"""

import sqlite3
import threading
import logging
import os
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager

# Import centralized paths
from N5.lib.paths import (
    CRM_DB, BRAIN_DB, CONVERSATIONS_DB, WELLNESS_DB,
    PRODUCTIVITY_DB, LUMA_EVENTS_DB, ZO_FEEDBACK_DB,
    WORKOUTS_DB
)

LOG = logging.getLogger("n5.db")


class DatabasePool:
    """
    SQLite connection pool with thread-local storage.

    SQLite connections are not thread-safe by default. This class provides:
    - One connection per thread (thread-local storage)
    - Connection reuse within the same thread
    - Automatic cleanup on thread exit
    - Health checking and reconnection
    """

    # Class-level registry of all pools for cleanup
    _pools: dict[str, 'DatabasePool'] = {}
    _pools_lock = threading.Lock()

    def __init__(self, db_path: str | Path,
                 check_same_thread: bool = False,
                 timeout: float = 30.0,
                 isolation_level: Optional[str] = None):
        """
        Initialize a database pool.

        Args:
            db_path: Path to SQLite database file
            check_same_thread: SQLite check_same_thread parameter
            timeout: Connection timeout in seconds
            isolation_level: SQLite isolation level (None for autocommit)
        """
        self.db_path = str(db_path)
        self.check_same_thread = check_same_thread
        self.timeout = timeout
        self.isolation_level = isolation_level

        # Thread-local storage for connections
        self._local = threading.local()

        # Track connection count for stats
        self._connection_count = 0
        self._lock = threading.Lock()

        # Register this pool
        with DatabasePool._pools_lock:
            DatabasePool._pools[self.db_path] = self

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with standard settings."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=self.check_same_thread,
            timeout=self.timeout,
            isolation_level=self.isolation_level
        )

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Use WAL mode for better concurrency (if not already set)
        try:
            conn.execute("PRAGMA journal_mode = WAL")
        except sqlite3.OperationalError:
            pass  # Database might be read-only

        with self._lock:
            self._connection_count += 1

        LOG.debug(f"Created new connection to {self.db_path} (total: {self._connection_count})")
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection for the current thread.

        Returns existing connection if available, creates new one if needed.
        Connection is reused across calls within the same thread.
        """
        # Check for existing connection in thread-local storage
        conn = getattr(self._local, 'connection', None)

        if conn is not None:
            # Verify connection is still valid
            try:
                conn.execute("SELECT 1")
                return conn
            except sqlite3.Error:
                LOG.warning(f"Stale connection to {self.db_path}, reconnecting")
                self._close_thread_connection()

        # Create new connection
        conn = self._create_connection()
        self._local.connection = conn
        return conn

    def _close_thread_connection(self):
        """Close the connection for the current thread."""
        conn = getattr(self._local, 'connection', None)
        if conn is not None:
            try:
                conn.close()
            except sqlite3.Error:
                pass
            self._local.connection = None
            with self._lock:
                self._connection_count = max(0, self._connection_count - 1)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for getting a connection.

        The connection is NOT closed after the context - it's kept for reuse.
        Use transaction() if you want auto-commit/rollback behavior.
        """
        yield self.get_connection()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for a transaction with auto-commit/rollback.

        Commits on successful exit, rolls back on exception.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self):
        """Close the connection for the current thread."""
        self._close_thread_connection()

    def close_all(self):
        """Close all connections (call during shutdown)."""
        # Note: We can only close the current thread's connection
        # Other threads' connections will be cleaned up when those threads exit
        self._close_thread_connection()

    @classmethod
    def close_all_pools(cls):
        """Close all registered pools (call during application shutdown)."""
        with cls._pools_lock:
            for pool in cls._pools.values():
                pool.close_all()

    @property
    def stats(self) -> dict:
        """Get pool statistics."""
        return {
            "db_path": self.db_path,
            "active_connections": self._connection_count,
            "has_thread_connection": hasattr(self._local, 'connection') and self._local.connection is not None
        }


# =============================================================================
# SINGLETON POOLS FOR COMMON DATABASES
# =============================================================================

# Lazy initialization - pools created on first access
_crm_pool: Optional[DatabasePool] = None
_brain_pool: Optional[DatabasePool] = None
_conversations_pool: Optional[DatabasePool] = None
_wellness_pool: Optional[DatabasePool] = None
_productivity_pool: Optional[DatabasePool] = None
_luma_pool: Optional[DatabasePool] = None
_workouts_pool: Optional[DatabasePool] = None

_init_lock = threading.Lock()


def _get_pool(pool_var_name: str, db_path: Path) -> DatabasePool:
    """Helper to lazily initialize a pool singleton."""
    global _crm_pool, _brain_pool, _conversations_pool, _wellness_pool
    global _productivity_pool, _luma_pool, _workouts_pool

    pool = globals().get(pool_var_name)
    if pool is None:
        with _init_lock:
            # Double-check after acquiring lock
            pool = globals().get(pool_var_name)
            if pool is None:
                pool = DatabasePool(db_path)
                globals()[pool_var_name] = pool
    return pool


# =============================================================================
# PUBLIC API - Connection Getters
# =============================================================================

def get_crm_db() -> sqlite3.Connection:
    """Get a reusable connection to the CRM database."""
    global _crm_pool
    if _crm_pool is None:
        with _init_lock:
            if _crm_pool is None:
                _crm_pool = DatabasePool(CRM_DB)
    return _crm_pool.get_connection()


def get_brain_db() -> sqlite3.Connection:
    """Get a reusable connection to the semantic memory database."""
    global _brain_pool
    if _brain_pool is None:
        with _init_lock:
            if _brain_pool is None:
                _brain_pool = DatabasePool(BRAIN_DB)
    return _brain_pool.get_connection()


def get_conversations_db() -> sqlite3.Connection:
    """Get a reusable connection to the conversations database."""
    global _conversations_pool
    if _conversations_pool is None:
        with _init_lock:
            if _conversations_pool is None:
                _conversations_pool = DatabasePool(CONVERSATIONS_DB)
    return _conversations_pool.get_connection()


def get_wellness_db() -> sqlite3.Connection:
    """Get a reusable connection to the wellness database."""
    global _wellness_pool
    if _wellness_pool is None:
        with _init_lock:
            if _wellness_pool is None:
                _wellness_pool = DatabasePool(WELLNESS_DB)
    return _wellness_pool.get_connection()


def get_productivity_db() -> sqlite3.Connection:
    """Get a reusable connection to the productivity database."""
    global _productivity_pool
    if _productivity_pool is None:
        with _init_lock:
            if _productivity_pool is None:
                _productivity_pool = DatabasePool(PRODUCTIVITY_DB)
    return _productivity_pool.get_connection()


def get_luma_db() -> sqlite3.Connection:
    """Get a reusable connection to the Luma events database."""
    global _luma_pool
    if _luma_pool is None:
        with _init_lock:
            if _luma_pool is None:
                _luma_pool = DatabasePool(LUMA_EVENTS_DB)
    return _luma_pool.get_connection()


def get_workouts_db() -> sqlite3.Connection:
    """Get a reusable connection to the workouts database."""
    global _workouts_pool
    if _workouts_pool is None:
        with _init_lock:
            if _workouts_pool is None:
                _workouts_pool = DatabasePool(WORKOUTS_DB)
    return _workouts_pool.get_connection()


# =============================================================================
# PUBLIC API - Transaction Context Managers
# =============================================================================

@contextmanager
def crm_transaction() -> Generator[sqlite3.Connection, None, None]:
    """Transaction context manager for CRM database."""
    global _crm_pool
    if _crm_pool is None:
        with _init_lock:
            if _crm_pool is None:
                _crm_pool = DatabasePool(CRM_DB)
    with _crm_pool.transaction() as conn:
        yield conn


@contextmanager
def brain_transaction() -> Generator[sqlite3.Connection, None, None]:
    """Transaction context manager for semantic memory database."""
    global _brain_pool
    if _brain_pool is None:
        with _init_lock:
            if _brain_pool is None:
                _brain_pool = DatabasePool(BRAIN_DB)
    with _brain_pool.transaction() as conn:
        yield conn


@contextmanager
def wellness_transaction() -> Generator[sqlite3.Connection, None, None]:
    """Transaction context manager for wellness database."""
    global _wellness_pool
    if _wellness_pool is None:
        with _init_lock:
            if _wellness_pool is None:
                _wellness_pool = DatabasePool(WELLNESS_DB)
    with _wellness_pool.transaction() as conn:
        yield conn


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

def get_db_connection(db_path: str | Path = None) -> sqlite3.Connection:
    """
    Backward-compatible function matching existing get_db_connection() pattern.

    If db_path matches a known database, returns pooled connection.
    Otherwise creates a new DatabasePool for the path.

    Note: For new code, prefer the specific getters (get_crm_db, etc.)
    """
    if db_path is None:
        db_path = CRM_DB

    db_path_str = str(db_path)

    # Check if this matches a known database
    if db_path_str == str(CRM_DB):
        return get_crm_db()
    elif db_path_str == str(BRAIN_DB):
        return get_brain_db()
    elif db_path_str == str(CONVERSATIONS_DB):
        return get_conversations_db()
    elif db_path_str == str(WELLNESS_DB):
        return get_wellness_db()
    elif db_path_str == str(PRODUCTIVITY_DB):
        return get_productivity_db()
    elif db_path_str == str(LUMA_EVENTS_DB):
        return get_luma_db()
    elif db_path_str == str(WORKOUTS_DB):
        return get_workouts_db()

    # Unknown database - create or reuse a pool for it
    with DatabasePool._pools_lock:
        if db_path_str in DatabasePool._pools:
            return DatabasePool._pools[db_path_str].get_connection()

    # Create new pool
    pool = DatabasePool(db_path_str)
    return pool.get_connection()


# =============================================================================
# UTILITIES
# =============================================================================

def get_pool_stats() -> dict:
    """Get statistics for all active pools."""
    with DatabasePool._pools_lock:
        return {
            path: pool.stats
            for path, pool in DatabasePool._pools.items()
        }


def close_all_connections():
    """Close all pooled connections (call during shutdown)."""
    DatabasePool.close_all_pools()
