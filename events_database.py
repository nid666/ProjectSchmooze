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
        def _is_ready_(uuid:str):
            event_dict = event.details.unserialize(uuid)

            check_dict = {"times": {}, "locations": {}}
            for e_k in event_dict["votes"].keys():
                e_v = event_dict["votes"][e_k]
                location = e_v["selected_location"]
                if location not in check_dict["locations"].keys():
                    check_dict["locations"][location] = 1
                else:
                    check_dict["locations"][location] += 1
                time = e_v["selected_time"]
                if time not in check_dict["times"].keys():
                    check_dict["times"][time] = 1
                else:
                    check_dict["times"][time] += 1

            rec_max = int((len(event_dict["recipients"]) / 2) + 1)
            max_times_key, max_times_value = max(check_dict["times"].items(), key=lambda x: x[1])
            max_locations_key, max_locations_value = max(check_dict["locations"].items(), key=lambda x: x[1])

            time_max = (max_times_value >= rec_max)
            loc_max = (max_locations_value >= rec_max)
            len_max = len(event_dict["votes"]) == len(event_dict["recipients"])

            print(f"{max_times_key} : {max_times_value}\n{max_locations_key} : {max_locations_value}\nrec max: {rec_max}\ntime max: {time_max}\nloc amx:{loc_max}\nlen max: {len_max}")

            return (time_max and loc_max) or len_max # returns true if # of time, locations is greater than len(recipients)+1
            

        @staticmethod
        def vote(uuid:str, vote_dict:dict)->bool:
            event_dict = event.details.unserialize(uuid)
            event_dict["votes"][vote_dict["voting_id"]] = vote_dict
            event.details.serialize(event_dict)

            print("VOTE CAST!")

            if event.voting._is_ready_(uuid):
                print("EMAIL SENT")
                notify.send.request(uuid, f"http://localhost:8501/?uuid={uuid}&apr=get", True) # temporary WEBSITE placeholder for approval page
            else:
                print("EMAIL NOT SENT")

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

