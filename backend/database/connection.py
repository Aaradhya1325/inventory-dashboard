import aiosqlite
import httpx
import os
from pathlib import Path
from typing import Any, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """Abstract database adapter interface"""
    
    async def execute(self, sql: str, params: tuple = ()) -> int:
        """Execute SQL and return last row id"""
        raise NotImplementedError
    
    async def execute_many(self, sql: str, params_list: list) -> None:
        """Execute SQL with multiple parameter sets"""
        raise NotImplementedError
    
    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """Fetch single row as dict"""
        raise NotImplementedError
    
    async def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows as list of dicts"""
        raise NotImplementedError
    
    async def executescript(self, sql: str) -> None:
        """Execute SQL script"""
        raise NotImplementedError


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter for local development"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def connect(self) -> None:
        """Initialize database connection"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        logger.info(f"SQLite database connected at {self.db_path}")
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    @property
    def connection(self) -> aiosqlite.Connection:
        if not self._connection:
            raise RuntimeError("Database not connected")
        return self._connection
    
    async def execute(self, sql: str, params: tuple = ()) -> int:
        cursor = await self.connection.execute(sql, params)
        await self.connection.commit()
        return cursor.lastrowid or 0
    
    async def execute_many(self, sql: str, params_list: list) -> None:
        await self.connection.executemany(sql, params_list)
        await self.connection.commit()
    
    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        cursor = await self.connection.execute(sql, params)
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        cursor = await self.connection.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def executescript(self, sql: str) -> None:
        await self.connection.executescript(sql)
        await self.connection.commit()


class D1Adapter(DatabaseAdapter):
    """Cloudflare D1 adapter for production"""
    
    def __init__(self, account_id: str, api_token: str, database_id: str):
        self.account_id = account_id
        self.api_token = api_token
        self.database_id = database_id
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> None:
        """Initialize HTTP client"""
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        logger.info("Cloudflare D1 adapter initialized")
    
    async def disconnect(self) -> None:
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("D1 client not connected")
        return self._client
    
    async def _query(self, sql: str, params: list = []) -> dict:
        """Execute D1 query"""
        response = await self.client.post(
            f"{self.base_url}/query",
            json={"sql": sql, "params": params}
        )
        response.raise_for_status()
        return response.json()
    
    async def execute(self, sql: str, params: tuple = ()) -> int:
        result = await self._query(sql, list(params))
        meta = result.get("result", [{}])[0].get("meta", {})
        return meta.get("last_row_id", 0)
    
    async def execute_many(self, sql: str, params_list: list) -> None:
        for params in params_list:
            await self._query(sql, list(params))
    
    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        result = await self._query(sql, list(params))
        results = result.get("result", [{}])[0].get("results", [])
        return results[0] if results else None
    
    async def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        result = await self._query(sql, list(params))
        return result.get("result", [{}])[0].get("results", [])
    
    async def executescript(self, sql: str) -> None:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            await self._query(stmt)


# Global database instance
_db: Optional[DatabaseAdapter] = None


async def get_database() -> DatabaseAdapter:
    """Get database adapter instance"""
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db


async def init_database() -> DatabaseAdapter:
    """Initialize database adapter"""
    global _db
    
    if settings.use_d1:
        _db = D1Adapter(
            settings.cloudflare_account_id,
            settings.cloudflare_api_token,
            settings.d1_database_id
        )
    else:
        _db = SQLiteAdapter(settings.database_url)
    
    await _db.connect()
    return _db


async def close_database() -> None:
    """Close database connection"""
    global _db
    if _db:
        await _db.disconnect()
        _db = None
