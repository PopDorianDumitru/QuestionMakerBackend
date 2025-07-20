from typing import Any, Dict
from database.database_handler import DatabaseHandler
from services.database_service import DatabaseService
from database.firebase_handler import handler
from utils.firebase_auth import verify_firebase_token

class FirebaseService(DatabaseService):
    def __init__(self, db_handler: DatabaseHandler) -> None:
        self.db_handler = db_handler
    
    async def add_user(self, user_data: Dict[str, Any]) -> str:
        return await self.db_handler.add_user(user_data)
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        return await self.db_handler.get_user(user_id)
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        await self.db_handler.update_user(user_id, data)
    
    async def delete_user(self, user_id: str) -> None:
        await self.db_handler.delete_user(user_id)

    def get_token(self, bearer_token: str) -> str:
        bearer_token = bearer_token.replace("Bearer ", "")
        return bearer_token

    async def login(self, user_data: Dict[str, Any], authorization: str) -> str:
        token = self.get_token(authorization)
        user = verify_firebase_token(token)
        exists = await self.get_user(user["uid"])
        if exists == {}:
            await self.add_user(user)
        return user
service = FirebaseService(handler)