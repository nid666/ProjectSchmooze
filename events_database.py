import uuid
import pickle
import os

PATH_DIR_ALL_EVENT_DATAS = "events"
TAG_EVENT_DATA_FILE_NAME = "details"

def generate_UUID() -> str:
    # Generate a unique UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def generate_EVENT_DICT() -> dict:
    return {"uuid":"",         # str
            "date":"",         # str in date format
            "times":[],        # list of str(s) in time format
            "locations":[],    # list of str(s)
            "budget":0,        # int
            "sender":"",       # str in email format
            "recipients":[]}   # list os str(s) in email format

def PATH_DIR_EVENT_DATA(event_uuid:str) -> str:
    path = os.path.join(PATH_DIR_ALL_EVENT_DATAS, event_uuid)
    os.makedirs(PATH_DIR_ALL_EVENT_DATAS, exist_ok=True)
    os.makedirs(path, exist_ok=True)
    return path

def PATH_FILE_EVENT_DETAIL_FILE(event_uuid:str) -> str:
    return os.path.join(PATH_DIR_EVENT_DATA(event_uuid), f"{TAG_EVENT_DATA_FILE_NAME}.pkl")

def PATH_FILE_EVENT_VOTE_FILE(event_uuid:str, voting_uuid:str) -> str:
    return os.path.join(PATH_DIR_EVENT_DATA(event_uuid), f"{voting_uuid}.pkl")

class event:

    class voting:

        @staticmethod
        def get_current_winner() -> None:
            # time > location
            # how to handle conflicts within recipient times, and between recipient times and location availablility (booked, closed, ...)
            # recipients speciy times?
            return


        # boolean function used to indicate approval email
        @staticmethod
        def is_complete() -> bool:
            return False

        # handles revotes by comparing, editing existing pkl file with unique voting_uuid
        @staticmethod
        def send(voting_uuid: str):
            return        

    class details:

        @staticmethod
        def serialize(event_dict: dict) -> None:
            file_path = PATH_FILE_EVENT_DETAIL_FILE(event_dict["uuid"])
            try:
                with open(file_path, 'wb') as file:
                    pickle.dump(event_dict, file)
            except Exception as e:
                print(f"An error occurred: {e}")

        @staticmethod
        def unserialize(event_uuid="all", verbose=False) -> dict:
            
            file_path = PATH_FILE_EVENT_DETAIL_FILE(event_uuid)
            
            if file_path.lower().endswith("all"):
                
                # implement returning all events for analysis later
                """
                aggregated_dict = {}
                try:
                    # Iterate over all files in the directory
                    for filename in os.listdir(PATH_DIR_ALL_EVENT_DATAS):
                        if filename.endswith('.pkl'):
                            if filename.lower().startswith(TAG_EVENT_DATA_FILE_NAME):
                                continue
                            file_path = os.path.join(PATH_DIR_ALL_EVENTS, filename)
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
                """
                
            try:
                with open(file_path, 'rb') as file:
                    data = pickle.load(file)
                    return data
            except Exception as e:
                print(f"An error occurred: {e}")

            return {}

