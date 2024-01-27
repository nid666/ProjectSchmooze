import uuid
import pickle
import os

PKL_PATH_DIR = "events"

def generate_UUID() -> str:
    # Generate a unique UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def PKL_PATH_FILE(uuid:str) -> str:
    return os.path.join(PKL_PATH_DIR, f"{uuid}.pkl")

def serialize_event(event_dict: dict) -> None:
    file_path = PKL_PATH_FILE(event_dict["uuid"])
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(event_dict, file)
        #print(f"Dictionary successfully serialized to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def unserialize_event(uuid:str) -> dict:
    path = PKL_PATH_FILE(uuid)
    with open(path, 'rb') as file:
        data = pickle.load(file)
        return data
    
def unserialize_events() -> dict:
    aggregated_dict = {}
    try:
        # Iterate over all files in the directory
        for filename in os.listdir(PKL_PATH_DIR):
            if filename.endswith('.pkl'):
                file_path = os.path.join(PKL_PATH_DIR, filename)
                with open(file_path, 'rb') as file:
                    # Deserialize the contents of the pickle file
                    data = pickle.load(file)
                    # Use the filename without extension as the key
                    key = os.path.splitext(filename)[0]
                    aggregated_dict[key] = data
        return aggregated_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
