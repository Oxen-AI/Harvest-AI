
import json
from typing import Dict, Any, List
from .db import DB

class NoOpDB(DB):
    async def add(self, model: str, messages: List[Dict[Any, Any]]) -> None:
        """No-op implementation of the DB interface."""
        pass
