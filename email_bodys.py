import os
from ics import Calendar, Event
from datetime import datetime, timedelta

PATH_DIR_MAIL = "mail"

def PATH_FILE_CAL_EVENT(name:str, location:str, desc:str, date:str, time_range:str)->str:
    
    path = os.path.join(PATH_DIR_MAIL, f"{date}__{time_range}.ics")
    start_time, end_time = wrapper.time_split(time_range)
    
    cal = Calendar()

    event = Event()
    event.name = name
    event.location = location
    event.description = desc
    event.duration = timedelta(hours=wrapper.length_hours(time_range))
    event.begin = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")

    cal.events.add(event)

    with open(path, 'w') as f:
        f.writelines(cal.serialize_iter())
    
    return path

class wrapper:

    @staticmethod
    def get_scores_location(votes_dict:dict)->dict:
        ret_dict = {}
        for v in votes_dict.values():
            element = v["selected_location"]
            if element in ret_dict.keys():
                ret_dict[element] = 1
                continue
            ret_dict[element] += 1
        return ret_dict
    
    @staticmethod
    def get_winning_location(votes_dict:dict)->tuple:
        location_scores = wrapper.get_scores_location(votes_dict)
        winning_key = max(location_scores, key=location_scores.get)
        return (winning_key, location_scores[winning_key])

    @staticmethod
    def get_scores_time(votes_dict:dict)->dict:
        ret_dict = {}
        for v in votes_dict.values():
            element = v["selected_time"]
            if element in ret_dict.keys():
                ret_dict[element] = 1
                continue
            ret_dict[element] += 1
        return ret_dict

    @staticmethod
    def get_winning_time(votes_dict:dict)->tuple:
        time_scores = wrapper.get_scores_time(votes_dict)
        winning_key = max(time_scores, key=time_scores.get)
        return (winning_key, time_scores[winning_key])

    @staticmethod
    def convert_time_to_24hr(time_str):
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        return time_obj.strftime("%H:%M")

    @staticmethod
    def time_split(time_slot):
        return time_slot.split(" - ")

    @staticmethod
    def length_hours(time_slot):
        # Function to convert time to 24-hour format
        
        # Split the time slot into start and end times
        start_time_str, end_time_str = wrapper.time_split(time_slot)
        
        # Convert start and end times to 24-hour format
        start_time_24hr = wrapper.convert_time_to_24hr(start_time_str)
        end_time_24hr = wrapper.convert_time_to_24hr(end_time_str)
        
        # Parse the 24-hour format times into datetime objects
        start_time_obj = datetime.strptime(start_time_24hr, "%H:%M")
        end_time_obj = datetime.strptime(end_time_24hr, "%H:%M")
        
        # Calculate the difference in hours
        time_difference = end_time_obj - start_time_obj
        hours_difference = time_difference.total_seconds() / 3600  # Convert seconds to hours
        
        return hours_difference

    

class format:
    
    class raw_email:

        @staticmethod
        def get_approve(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)

            row1 = f"{organizer}'s event on {winning_time} ({date}) at {winning_location} has been booked!"
            row2 = f"Add this event to your calendar:"
            
            
            return 

        @staticmethod
        def get_request(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

        @staticmethod
        def get_invite(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""
        
    class html_email:

        @staticmethod
        def get_approve(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

        @staticmethod
        def get_request(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

        @staticmethod
        def get_invite(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

    class attachments:

        @staticmethod
        def get_approve(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

        @staticmethod
        def get_request(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""

        @staticmethod
        def get_invite(event_dict: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time = wrapper.get_winning_time(votes)
            winning_location = wrapper.get_winning_location(votes)
            
            return ""
