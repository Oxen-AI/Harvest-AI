import sqlite3
import json
from typing import Dict, Any, List
from .db import DB

class SQLiteDB(DB):
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model VARCHAR(255),
                messages TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    async def add(self, model: str, messages: List[Dict[Any, Any]]) -> None:
        """Save chat interaction to SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO chat_history (model, messages) VALUES (?, ?)',
            (model, json.dumps(messages))
        )
        
        conn.commit()
        conn.close()
