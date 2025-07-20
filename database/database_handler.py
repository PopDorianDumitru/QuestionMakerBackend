from abc import ABC, abstractmethod
from typing import Any, Dict, List

class DatabaseHandler(ABC):

    @abstractmethod
    async def add_user(self, user_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> None:
        pass
