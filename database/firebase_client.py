import firebase_admin
from firebase_admin import credentials, firestore
from settings import settings
import json

cred_json = settings.firebase_credentials
cred_dict = json.loads(cred_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()