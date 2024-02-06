import os
import arrow
from ics import Calendar, Event
from datetime import datetime, timedelta

PATH_DIR_MAIL = "mail"
TAG_COMPANY_NAME = "SCHMOOZE"

# IMPLEMENT timezone options in events database!
def PATH_FILE_CAL_EVENT(name: str, location: str, desc: str, date: str, time_range: str, organizer: str, timezone='America/New_York') -> str:
    # Split the time range into start and end times
    start_time_str, end_time_str = wrapper.time_split(time_range)
    
    # Convert start and end times to 24-hour format
    start_time_24hr = wrapper.convert_time_to_24hr(start_time_str)
    end_time_24hr = wrapper.convert_time_to_24hr(end_time_str)

    # Set file path for the .ics file
    path = os.path.join(PATH_DIR_MAIL, f"{name}.ics")
    
    # Create calendar and event objects
    cal = Calendar()
    event = Event()
    
    # Set event details
    event.name = name
    event.location = location
    event.description = desc
    event.organizer = organizer

    # Set event start and end times with the specified timezone
    event.begin = arrow.get(f"{date} {start_time_24hr}", 'YYYY-MM-DD HH:mm', tzinfo=timezone)
    event.end = arrow.get(f"{date} {end_time_24hr}", 'YYYY-MM-DD HH:mm', tzinfo=timezone)

    # Add event to calendar and write to file
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
        time_obj = datetime.strptime(str(time_str), "%I:%M %p")
        return time_obj.strftime("%H:%M")

    @staticmethod
    def time_split(time_slot):
        return time_slot.split(" - ")

    @staticmethod
    def date_desc(date_string):
        # Parse the input date string into a datetime object
        date_obj = datetime.strptime(str(date_string), "%Y-%m-%d")
        
        # Define a small helper function to determine the ordinal suffix for the day
        def get_ordinal_suffix(day):
            if 11 <= day <= 13:
                return 'th'
            else:
                suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
                # Return 'th' as default if the day does not match any key in the suffixes dict
                return suffixes.get(day % 10, 'th')
        
        # Format the date, appending the ordinal suffix to the day
        formatted_date = date_obj.strftime(f"%B {date_obj.day}{get_ordinal_suffix(date_obj.day)}, %Y")
        return formatted_date

    @staticmethod
    def length_hours(time_slot):
        # Split the time slot into start and end times
        start_time_str, end_time_str = wrapper.time_split(time_slot)
        
        # Convert start and end times to 24-hour format
        start_time_24hr = wrapper.convert_time_to_24hr(start_time_str)
        end_time_24hr = wrapper.convert_time_to_24hr(end_time_str)
        
        # Convert times to datetime objects to calculate the duration
        start_time_obj = datetime.strptime(start_time_24hr, "%H:%M")
        end_time_obj = datetime.strptime(end_time_24hr, "%H:%M")
        
        # Handle case where end time is the next day
        if end_time_obj <= start_time_obj:
            end_time_obj += timedelta(days=1)
        
        # Calculate the duration in hours
        duration = (end_time_obj - start_time_obj).total_seconds() / 3600.0
        return duration
        

class format:

    class subject:

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

            return f"[{TAG_COMPANY_NAME}] Add {winning_location[0]} on {wrapper.date_desc(date)} ({winning_time[0]}) to your calendar!"

        @staticmethod
        def get_request(event: dict)->str:
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

            return f"[{TAG_COMPANY_NAME}] Your event on {wrapper.date_desc(date)} needs approval!"

        @staticmethod
        def get_invite(event: dict)->str:
            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']

            return f"[{TAG_COMPANY_NAME}] {organizer} sent an invitation on {wrapper.date_desc(date)}!"
    
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

            row1 = f"{organizer}'s event on {wrapper.date_desc(date)} ({winning_time[0]}) at {winning_location[0]} has been booked!"
            row2 = f"Add this event to your calendar"
            
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

            row1 = f"{winning_location[0]} on {wrapper.date_desc(date)} ({winning_time[0]}) needs approval!"
            row2 = f"Approve Event - {request_link}"
            row3 = "Times:"
            row4 = '\n'.join(f"{t} ({score}/{len(guests)})" for t, score in sorted(wrapper.get_scores_time(event['votes']).items(), key=lambda item: item[0], reverse=True))
            row5 = "Locations:"
            row6 = '\n'.join(f"{l} ({score}/{len(guests)})" for l, score in sorted(wrapper.get_scores_location(event['votes']).items(), key=lambda item: item[0], reverse=True))
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6

        @staticmethod
        def get_invite(event: dict, voting_link:str)->str:

            uuid = event['uuid']
            date = event['date']
            times = event['times']
            locations = event['locations']
            budget = event['budget']
            organizer = event['sender']
            guests = event['recipients']

            row1 = f"{organizer} is inviting you to an event on {wrapper.date_desc(date)}!"
            row2 = f"Vote Now - {voting_link}"
            row3 = "Times:"
            row4 = '\n'.join(f"{t}" for t in times)
            row5 = "Locations:"
            row6 = '\n'.join(f"{l}" for l in locations)
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6
        
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
                        <p style="font-size: 16px; color: #555; text-align: center;">
                            {organizer}'s event on <strong>{wrapper.date_desc(date)} ({winning_time[0]})</strong> at <strong>{winning_location[0]}</strong> has been booked!
                        </p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="#" style="background-color: #4CAF50; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Add this event to your calendar</a>
                        </p>
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_request(event_dict: dict, request_link: str) -> str:
            organizer = event_dict['sender']
            guests = event_dict['recipients']
            winning_time = wrapper.get_winning_time(event_dict['votes'])
            date = event_dict['date']
            winning_location = wrapper.get_winning_location(event_dict['votes'])

            times_list_items = ''.join(f"<p style='font-size: 11px; color: #555;'>{t} ({score}/{len(guests)})</p>" for t, score in sorted(wrapper.get_scores_time(event_dict['votes']).items(), key=lambda item: item[0], reverse=True))
            locations_list_items = ''.join(f"<p style='font-size: 11px; color: #555;'>{l} ({score}/{len(guests)})</p>" for l, score in sorted(wrapper.get_scores_location(event_dict['votes']).items(), key=lambda item: item[0], reverse=True))

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #007bff; text-align: center;">Approval Needed!</h2>
                        <p style="font-size: 16px; color: #555; text-align: center;"><strong>{winning_location[0]}</strong> on <strong>{wrapper.date_desc(date)} ({winning_time[0]})</strong> needs approval!</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{request_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Approve Event</a>
                        </p>
                        <div style="margin: 30px 0; border-top: 2px solid #ccc;"></div>
                        <h3 style="color: #333;">Times:</h3>
                        {times_list_items}
                        <h3 style="color: #333;">Locations:</h3>
                        {locations_list_items}
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_invite(event_dict: dict, voting_link: str) -> str:
            organizer = event_dict['sender']
            date = event_dict['date']
            times = event_dict['times']
            locations = event_dict['locations']

            times_list_items = ''.join(f"<p style='font-size: 11px; color: #555;'>{t}</p>" for t in times)
            locations_list_items = ''.join(f"<p style='font-size: 11px; color: #555;'>{l}</p>" for l in locations)

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff9800; text-align: center;">You're Invited!</h2>
                        <p style="font-size: 16px; color: #555; text-align: center;">{organizer} is inviting you to an event on <strong>{wrapper.date_desc(date)}</strong>!</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{voting_link}" style="background-color: #ff9800; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Vote Now</a>
                        </p>
                        <div style="margin: 30px 0; border-top: 2px solid #ccc;"></div>
                        <h3 style="color: #333;"><strong>Times:</strong></h3>
                        {times_list_items}
                        <h3 style="color: #333;"><strong>Locations:</strong></h3>
                        {locations_list_items}
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
            ret.append(PATH_FILE_CAL_EVENT(f"{winning_loc_name}_{date}", winning_loc_name, f"{winning_loc_name} @ {wrapper.date_desc(date)} ({winning_time_name}) with {organizer}!", date, winning_time_name, organizer))
        
            return ret

        @staticmethod
        def get_request(event_dict: dict)->list:
            
            return []

        @staticmethod
        def get_invite(event_dict: dict)->list:
            
            return []
