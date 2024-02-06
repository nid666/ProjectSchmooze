import uuid
import pickle
import os
import schmail as notify

PATH_DIR_ALL_EVENTS = "events"

def generate_UUID() -> str:
    # Generate a unique UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def PATH_FILE_EVENT(uuid:str) -> str:
    return os.path.join(PATH_DIR_ALL_EVENTS, f"{uuid}.pkl")

class event:

    class voting:

        @staticmethod
        def vote(uuid:str, vote_dict:dict)->bool:
            event_dict = event.details.unserialize(uuid)
            event_dict["votes"][vote_dict["voting_id"]] = vote_dict
            event.details.serialize(event_dict)

            majority_index = (len(event_dict["recipients"]) / 2) + 1

            all_voted = (len(event_dict["votes"])) >= majority_index
            if(all_voted): notify.send.request(uuid, "google.com", True) # temporary WEBSITE placeholder for approval page

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
            file_path = PATH_FILE_EVENT(event_dict["uuid"])
            try:
                with open(file_path, 'wb') as file:
                    pickle.dump(event_dict, file)
            except Exception as e:
                print(f"An error occurred: {e}")

        # run without arguments to get all events
        @staticmethod
        def unserialize(event_uuid="all") -> dict:
            
            file_path = PATH_FILE_EVENT(event_uuid)

            # Check if the file exists, if not and the event_uuid is not 'all', return None
            if not event_uuid == "all" and not os.path.exists(file_path):
                print(f"No file found for UUID: {event_uuid}")
                return None
            
            if file_path.lower().endswith("all"):
                
                aggregated_dict = {}
                try:
                    # Iterate over all files in the directory
                    for filename in os.listdir(PATH_DIR_ALL_EVENT_DATAS):
                        if filename.endswith('.pkl'):
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
                
                
            try:
                with open(file_path, 'rb') as file:
                    data = pickle.load(file)
                    return data
            except Exception as e:
                print(f"An error occurred: {e}")

            return {}

