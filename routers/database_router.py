from typing import Optional
from fastapi import APIRouter, Header
from services.database_service import DatabaseService
from services.firebase_service import service

database_router = APIRouter()

def get_service() -> DatabaseService:
    return service

@database_router.post("/login")
async def add_user(authorization: Optional[str] = Header(None)):
    message = await get_service().login(authorization)
    return {"user": message}

# @database_router.put("/update_user/{user_id}")
# async def update_user(user_data: dict = {}, data: dict = {}):
#     await get_service().update_user(user_data, data)
#     return {"message": "User updated successfully"}

# @database_router.delete("/delete_user/{user_id}")
# async def delete_user(user_data: dict = {}):
#     await get_service().delete_user(user_data)
#     return {"message": "User deleted successfully"}

@database_router.post("/subscribe")
async def subscribe(authorization: Optional[str] = Header(None)):
    url = await get_service().subscribe(authorization)
    return {"message": url}

@database_router.post("/unsubscribe")
async def unsubscribe(authorization: Optional[str] = Header(None)):
    message = await get_service().unsubscribe(authorization)
    return message