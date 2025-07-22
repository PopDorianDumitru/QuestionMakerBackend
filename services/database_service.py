from typing import Any, Dict
from database.database_handler import DatabaseHandler

class DatabaseService:
    def __init__(self, db_handler: DatabaseHandler) -> None:
        pass
    async def add_user(self, user_data: Dict[str, Any]) -> str:
        pass

    async def login(self, authorization: str) -> str:
        pass

    async def subscribe(self, authorization: str) -> None:
        pass

    async def unsubscribe(self, authorization: str) -> None:
        pass

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        pass

    async def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        pass

    async def delete_user(self, user_id: str) -> None:
        pass