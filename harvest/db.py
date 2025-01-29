from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DB(ABC):
    """
    Abstract base class for chat history database implementations.
    Different database implementations should inherit from this class.
    """

    @abstractmethod
    async def add(self, model: str, messages: List[Dict[Any, Any]]) -> None:
        """
        Save a chat interaction to the database.
        
        Args:
            model: The model name ie: "deepseek-r1"
            messages: The list of messages in the format of the OpenAI API ie: [{"role": "user", "content": "Hello!"}]
        """
        pass
