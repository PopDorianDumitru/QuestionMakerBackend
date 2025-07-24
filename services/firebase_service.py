from typing import Any, Dict
from database.database_handler import DatabaseHandler
from services.database_service import DatabaseService
from database.firebase_handler import handler
from utils.firebase_auth import verify_firebase_token
from settings import settings
from services.stripe_service import create_checkout_session, create_customer, is_user_subscribed, unsubscribe
from fastapi import HTTPException

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

    async def login(self, authorization: str) -> str:
        token = self.get_token(authorization)
        user = verify_firebase_token(token)
        exists = await self.get_user(user["uid"])
        if exists == {}:
            exists = await self.add_user(user)
        if "stripeCustomerId" not in exists:
            customer = create_customer(user)
            await self.update_user(user["uid"], {"stripeCustomerId": customer.id})
        return exists
    
    async def subscribe(self, authorization: str) -> None:
        token = self.get_token(authorization)
        user = verify_firebase_token(token)
        user = await self.get_user(user["uid"])
        stripe_customer_id = user["stripeCustomerId"]
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="Customer not found")      
        if is_user_subscribed(stripe_customer_id):  
            raise HTTPException(status_code=400, detail="User already subscribed")
        try:
            checkout_session = create_checkout_session(stripe_customer_id)
            return {"url": checkout_session.url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def unsubscribe(self, authorization: str) -> None:
        token = self.get_token(authorization)
        user = verify_firebase_token(token)
        user = await self.get_user(user["uid"])
        stripe_customer_id = user["stripeCustomerId"]
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="Customer not found")
        if not is_user_subscribed(stripe_customer_id):
            raise HTTPException(status_code=400, detail="User not subscribed")
        try:
            unsubscribe(stripe_customer_id)
            return {"message": "User unsubscribed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def canCreateQuiz(self, authorization: str) -> bool:
        if authorization == None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = self.get_token(authorization)
        user = verify_firebase_token(token)
        firestore_user = await self.get_user(user["uid"])
        if firestore_user["payingUser"]:
            return
        if not firestore_user["usedFreeTier"]:
            await self.update_user(user["uid"], {"usedFreeTier": True})
            return
        raise HTTPException(status_code=400, detail="Free tier limit reached")

service = FirebaseService(handler)