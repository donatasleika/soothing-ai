import pandas as pd 
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_CREDS = ["MONGO_CREDS"]

cluster = MongoClient(f"{MONGO_CREDS}", tls=True, tlsAllowInvalidCertificates=True)
db = cluster["Cluster0"]
collection = db["tokens"]


logged_in_client = {}

# This is already connected to test_ui.py
def set_shared_state(client_name, patient_name, token, patient_id):
    collection.update_one(
        {"token": token},
        {"$set": {
            "client_name": client_name,
            "patient_name": patient_name,
            "patient_id": patient_id
        }},
        upsert=True
    )

    print(f"Shared state set for token {token}: client_name={client_name}, patient_name={patient_name}")


def get_shared_state(token):
    doc = collection.find_one({"token": token})
    if not doc:
        return None, None, None
    return doc["client_name"], doc["patient_name"], doc["token"], doc["_id"]


