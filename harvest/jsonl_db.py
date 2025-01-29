import os
import json
from datetime import datetime
from typing import Dict, Any, List
from .db import DB

class JSONLDB(DB):
    """
    A database that stores chat interactions in a JSONL file.
    """
    def __init__(self, db_path: str = "chat_history.jsonl"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Loads the JSONL file if it exists, otherwise creates an empty one."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as file:
                self.data = [json.loads(line) for line in file]
        else:
            self.data = []

    async def add(self, model: str, messages: List[Dict[Any, Any]]) -> None:
        """Save chat interaction to JSONL database."""
        self.data.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "messages": messages
        })
        with open(self.db_path, 'w') as file:
            for entry in self.data:
                file.write(json.dumps(entry) + '\n')
