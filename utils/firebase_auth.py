# auth_utils.py

from firebase_admin import auth
from typing import Dict
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError
from fastapi import HTTPException

import os

def verify_firebase_token(id_token: str) -> Dict:
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not verify token")
