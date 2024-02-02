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
    print("date string :: " + f"{date}{wrapper.convert_time_to_24hr(start_time)}")
    #event.begin = datetime.strptime(f"{date}{wrapper.convert_time_to_24hr(start_time)}", "%Y-%m-%d %H:%M")

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
            if element not in ret_dict.keys():
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
            if element not in ret_dict.keys():
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
        def get_approve(event: dict)->str:

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
            
            return row1 + '\n\n' + row2

        @staticmethod
        def get_request(event: dict, request_link:str)->str:

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

            row1 = f"Your event on {winning_time} ({date}) at {winning_location} needs approval!"
            row2 = f"Approve: {request_link}"
            row3 = "RESULTS:"
            row4 = "Times - " + ', '.join(f"{t} ({score})" for t, score in wrapper.get_scores_time(event['votes']).items())
            row5 = "Locations - " + ', '.join(f"{l} ({score})" for l, score in wrapper.get_scores_location(event['votes']).items())
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n' + row5

        @staticmethod
        def get_invite(event: dict, voting_link:str)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            row1 = f"{organizer} is inviting you to an event on {date}!"
            row2 = f"Vote: {voting_link}"
            row3 = "Times - " + ', '.join(f"{t}" for t in wrapper.get_scores_time(event['votes']).keys())
            row4 = "Locations - " + ', '.join(f"{l}" for l in wrapper.get_scores_location(event['votes']).keys())
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n' + row4
        
    class html_email:

        @staticmethod
        def get_approve(event_dict: dict) -> str:
            organizer = event_dict['sender']
            winning_time = wrapper.get_winning_time(event_dict['votes'])
            date = event_dict['date']
            winning_location = wrapper.get_winning_location(event_dict['votes'])

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #4CAF50; text-align: center;">Event Approved</h2>
                        <p style="font-size: 16px; color: #555;">
                            {organizer}'s event on <strong>{winning_time} ({date})</strong> at <strong>{winning_location}</strong> has been booked!
                        </p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="#" style="background-color: #4CAF50; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Add to Calendar</a>
                        </p>
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_request(event_dict: dict, request_link: str) -> str:
            organizer = event_dict['sender']
            winning_time = wrapper.get_winning_time(event_dict['votes'])
            date = event_dict['date']
            winning_location = wrapper.get_winning_location(event_dict['votes'])

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #007bff; text-align: center;">Approval Needed</h2>
                        <p style="font-size: 16px; color: #555;">Your event on <strong>{winning_time} ({date})</strong> at <strong>{winning_location}</strong> needs approval!</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{request_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Approve Event</a>
                        </p>
                        <h3 style="color: #333;">RESULTS:</h3>
                        <p style="font-size: 14px; color: #555;">Times - {', '.join(f"{t} ({score})" for t, score in wrapper.get_scores_time(event_dict['votes']).items())}</p>
                        <p style="font-size: 14px; color: #555;">Locations - {', '.join(f"{l} ({score})" for l, score in wrapper.get_scores_location(event_dict['votes']).items())}</p>
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_invite(event_dict: dict, voting_link: str) -> str:
            organizer = event_dict['sender']
            date = event_dict['date']

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff9800; text-align: center;">You're Invited!</h2>
                        <p style="font-size: 16px; color: #555;">{organizer} is inviting you to an event on <strong>{date}</strong>!</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{voting_link}" style="background-color: #ff9800; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Vote Now</a>
                        </p>
                        <h3 style="color: #333;">Options:</h3>
                        <p style="font-size: 14px; color: #555;">Times - {', '.join(f"{t}" for t in wrapper.get_scores_time(event_dict['votes']).keys())}</p>
                        <p style="font-size: 14px; color: #555;">Locations - {', '.join(f"{l}" for l in wrapper.get_scores_location(event_dict['votes']).keys())}</p>
                    </div>
                </body>
            </html>
            """
            return html_content

    class attachments:

        @staticmethod
        def get_approve(event: dict)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']
            votes = event['votes']

            winning_time_obj = wrapper.get_winning_time(votes)
            winning_time_name = winning_time_obj[0]
            winning_time_count = winning_time_obj[1]
            #print(f"wtime: {winning_time}")
            winning_loc_obj = wrapper.get_winning_location(votes)
            winning_loc_name = winning_loc_obj[0]
            winning_loc_count = winning_loc_obj[1]
            #print(f"wloc: {winning_location}")

            ret = []

            # PATH_FILE_CAL_EVENT(name:str, location:str, desc:str, date:str, time_range:str)
            ret.append(PATH_FILE_CAL_EVENT(f"{organizer}--{date}({winning_time_name})", winning_loc_name, "{winning_loc_name} @ {date} ({winning_time_name}) with {organizer}!", date, winning_time_name))
        
            return ret

        @staticmethod
        def get_request(event_dict: dict)->list:
            
            return []

        @staticmethod
        def get_invite(event_dict: dict)->list:
            
            return []
