import pandas as pd 
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://donatas:Meileyracia42@cluster0.v4cy82i.mongodb.net/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = cluster["Cluster0"]
collection = db["tokens"]


logged_in_client = {}

# This is already connected to test_ui.py
def set_shared_state(client_name, patient_name, token):
    collection.update_one(
        {"token": token},
        {"$set": {
            "client_name": client_name,
            "patient_name": patient_name
        }},
        upsert=True
    )

    print(f"Shared state set for token {token}: client_name={client_name}, patient_name={patient_name}")


def get_shared_state(token):
    doc = collection.find_one({"token": token})
    if not doc:
        return None, None, None
    return doc["client_name"], doc["patient_name"], doc["token"]


# class RouteSchema(BaseModel):
#     url_id: str = Field(..., description="Unique identifier for the URL")
#     url_path: str = Field(..., description="Path of the URL")
#     patient_id: Optional[str] = Field(None, description="ID of the patient associated with the URL")
#     patient_name: Optional[str] = Field(None, description="Name of the patient associated with the URL")
#     timestamp: pd.Timestamp = Field(..., description="Timestamp when the URL was accessed")
#     entry: str = Field(..., description="Entry associated with the URL")
#     entries: List[str] = Field(..., description="List of entries associated with the URL")
#     total_entries: int = Field(..., description="Total number of entries associated with the URL")


# class Programmes():
#     no_programme = None
#     cbt_programme = 'CBT Programme'
#     act_programme = 'ACT Programme'
#     custom_programme = 'Custom Programme'