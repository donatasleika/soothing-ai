from pymongo.mongo_client import MongoClient
import ssl
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_CREDS = ["MONGO_CREDS"]

cluster = MongoClient(f"mongodb+srv://{MONGO_CREDS}/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = cluster["Cluster0"]


projects = {}


total_entries = []
client_name = 'joe-hudson'
total_url_tokens = []
new_url_usable = []


client_data = {
    "client_id": "1234",
    "client_name": "Joe Hudson"
}


patient_data = {
    "patient_id": "1",
    "client_id": "1234",
    "patient_name": "Donatas Leika",
    "private_url_token": "abc123xyz"
}

entry_data = {
    "entry_id": "1",
    "patient_id": "1",
    "time_of_entry": "2023-10-01 12:00",
    "description": "Feeling my body is tense, need to relax",
    "tags": ["test", "entry"]
}

collection = db[f"{client_data['client_name']}_{client_data['client_id']}_Patients"]


def check_num_entries(client_data: dict, patient_data: dict) -> None:
    total_entries = []
    collection_name = f"{client_data['client_name']}_{client_data['client_id']}_Patients"
    collection = db[collection_name]
    
    doc = collection.find_one({"_id": patient_data["patient_id"]})
    print(patient_data["patient_id"])

    if not doc:
        print("No patient found with the given ID.")
        return
    
    num_entries = len(doc.get("entries", []))

    if num_entries > 0:
        total_entries.append(num_entries)
        print(total_entries)
        print(f"Number of entries for patient {patient_data['patient_name']}: {num_entries}")

        return total_entries
        
    else:
        print("No entries found for this patient.")



def check_url_tokens(new_url_token: str, client_data: dict) -> bool:
    return collection.find_one({
        "private_url_token": new_url_token,
        "client_id": client_data["client_id"]
    }) is not None 


def insert_client(client_name: str, client_id: str) -> None:
    collection_name = f"{client_name}_{client_id}_Patients"
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        return db[collection_name]
    

id = 1234

# collection = insert_client(client_data["client_name"], client_data["client_id"])

def find_all_patient_ids():
    global projects
    results = collection.find({})
    for result in results:
        patient_id = result.get("_id")
        if patient_id:
            projects[patient_id] = result
    return projects

def find_clients(name: str):
    pass

def find_patient(id: str) -> str:
    global projects
    result = collection.find_one({
        "_id": id
    })
    # for result in results:
    if result:
        projects[id] = result
    else:
        projects[id] = None
    print(result)
    return result

def find_entries(patient_name: str):
    results = collection.find({
        "patient_name": patient_name
    })
    return list(results)

def find_all_patients(client_data: dict):
    collection_name = f"{client_data['client_name']}_{client_data['client_id']}_Patients"
    collection = db[collection_name]
    results = collection.find({})
    if results is None:
        print("No patients found for this client.")
        return []
    
    # Assuming results is a cursor, we can convert it to a list
    results = list(results)
    print(results)
    return results

    # for result in results:
    #     # projects["entries": []] = result
    #     print(result)
    
def read_receipts(patient_data, entry_data):
        collection_name = f"{patient_data['client_name']}_{patient_data['client_id']}_Patients"
        collection = db[collection_name]

        res = collection.update_one(
            {
                "patient_name": entry_data["patient_name"],
                "entries.entry_id": entry_data["entry_id"],
            },
            {
                "$set": {
                    "entries.$.read": True,
                    "entries.$.read_at": datetime.utcnow(),
                }
            },
            upsert=False,
        )
        # Optional: return a boolean for the caller
        return res.matched_count == 1 and res.modified_count >= 1

def collection_name_for(cd) -> str:
    return f"{cd['client_name']}_{cd['client_id']}_Patients"  # preserves spaces in client_name

def find_read_entries(client_data, patient_name: str) -> list:
    coll = db[collection_name_for(client_data)]
    pipeline = [
        {"$match": {"patient_name": patient_name}},
        {"$unwind": "$entries"},
        {"$match": {"entries.read": False}},  # boolean True
        {"$replaceRoot": {"newRoot": "$entries"}},
    ]
    return coll.aggregate(pipeline)


def insert_one_patient(client_data, patient_data):
    collection_name = f"{client_data['client_name']}_{client_data['client_id']}_Patients"
    collection = db[collection_name]
    collection.insert_one({
        "_id": patient_data["patient_id"],
        "client_id": patient_data["client_id"],
        "patient_name": patient_data["patient_name"],
        "private_url_token": patient_data["private_url_token"],
        "entries": []
    })
    print("Data has been uploaded")


# Need a counter for total and a +1 entry counter
    


def insert_one_entry(client_data, entry_data, tag_data):
    collection_name = f"{client_data['client_name']}_{client_data['client_id']}_Patients"
    
    full_entry = {**entry_data, "tags":tag_data}
    
    collection.update_one(
        {"patient_name": entry_data["patient_name"]},
        {"$push": {
            "entries": full_entry}},
        upsert=True
    )
    print("Entry has been uploaded")


def insert_many(data):
    collection.insert_many([
        {

        }
    ])


def delete_patient(patient_id: str):
    collection.delete_one({"_id": patient_id})
    print(f"Patient with ID {patient_id} has been deleted.")


# find_id(id)


# insert_client(client_data["client_name"], client_data["client_id"])

# insert_one_patient(client_data, patient_data)

# insert_one_entry(client_data, entry_data)

if __name__ == "__main__":
    client_data = {
    "client_id": "1234",
    "client_name": "Joe Hudson"
    }

    patient_data = {
        "patient_id": "1",
        "client_id": "1234",
        "patient_name": "Donatas Leika",
        "private_url_token": "abc123xyz"
    }

    entry_data = {
        "entry_id": "1",
        "patient_id": "1",
        "time_of_entry": "2023-10-01 12:00",
        "description": "Feeling my body is tense, need to relax",
        "tags": ["test", "entry"]
    }

    # check_num_entries(client_data, patient_data)
    # find_entries(patient_data["patient_name"])
    find_all_patients(client_data)
