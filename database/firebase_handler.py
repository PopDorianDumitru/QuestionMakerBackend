import firebase_admin
from firebase_admin import firestore
from database.database_handler import DatabaseHandler
from typing import Any, Dict
from database.firebase_client import db
from dataclasses import dataclass, asdict

@dataclass
class User:
    email: str
    payingUser: bool
    usedFreeTier: bool    
    username: str
    freeTrial: bool

class FirestoreHandler(DatabaseHandler):
    def __init__(self, db: firestore.Client):
        self.db = db

    async def add_user(self, user_data: Dict[str, Any]) -> str:
        doc_ref = self.db.collection("users").document(user_data["uid"])
        user = User(user_data["email"], False, False, user_data["name"], False)
        doc_ref.set(asdict(user))
        return doc_ref.id

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        doc = self.db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return {}

    async def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        self.db.collection("users").document(user_id).update(data)

    async def delete_user(self, user_id: str) -> None:
        self.db.collection("users").document(user_id).delete()

handler = FirestoreHandler(db)