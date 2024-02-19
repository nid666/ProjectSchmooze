#from apscheduler.schedulers.background import BackgroundScheduler
from email.message import EmailMessage
from yaml.loader import SafeLoader
from ics import Calendar, Event
from datetime import datetime
from datetime import timedelta
import database as db
import mimetypes
import smtplib
import arrow
import sched
import pytz
import yaml
import json
import os

TAG_COMPANY_NAME = "SCHMOOZE"

PATH_FILE_CREDENTIALS = "pages/creds.json"
PATH_DIR_MAIL = "pages/mail"
DOMAIN_NAME = "http://localhost:8501/"
VOTING_PAGE = os.path.join(DOMAIN_NAME, "votingPage")

def GET_CREDENTIALS():

    file_path = PATH_FILE_CREDENTIALS
    
    if not os.path.exists(file_path):
        raise ValueError(f"'{file_path}' does not exist!")

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

        # 'CHECK FOR REQUIRED KEYS' START
        has_email = False
        has_password = False
        key_error_msg = ""

        if 'email' not in data:
            key_error_msg += "The file does not have the 'email' key"
        else:
            has_email = True
        if 'password' not in data:
            to_append_start = "The file does not have "
            to_append_end = "the 'password' key'"
            if(not has_email):
                key_error_msg += " or "
            else:
                key_error_msg += to_append_start
            key_error_msg += to_append_start
        else:
            has_password = True
        if (not has_email) or (not has_password):
            raise ValueError(key_error_msg + ".")
        # 'CHECK FOR REQUIRED KEYS' END

        email = data['email']
        password = data['password']

        return (email, password)

# ------------------------------  ------------------------------ #

# IMPLEMENT timezone options in events database!
def PATH_FILE_CAL_EVENT(name: str, location: str, desc: str, date: str, time_range: str, organizer: str, timezone:str) -> str:
    start_time_str, end_time_str = wrapper.time_split(time_range)
    start_time_24hr = wrapper.convert_time_to_24hr(start_time_str)
    end_time_24hr = wrapper.convert_time_to_24hr(end_time_str)
    path = os.path.join(PATH_DIR_MAIL, f"{name}.ics")

    cal = Calendar()
    event = Event()
    event.name = name
    event.location = location
    event.description = desc
    event.organizer = organizer
    event.begin = arrow.get(f"{date} {start_time_24hr}", 'YYYY-MM-DD HH:mm', tzinfo=timezone)
    event.end = arrow.get(f"{date} {end_time_24hr}", 'YYYY-MM-DD HH:mm', tzinfo=timezone)
    cal.events.add(event)
    with open(path, 'w') as f:
        f.writelines(cal.serialize_iter())
    
    return path

class wrapper:

    @staticmethod
    def attendees_list(event_id:str, HTML=False):

        email = db.events.get.organizer_email(event_id)
        company = db.events.get.company(event_id)
        name = db.people.get.name(email)

        ret = ""
        ret = f"{name} from {company} - {email} (organizer)"
        if HTML: ret = "<p style='font-size: 11px; color: #555;'>" + ret + "</p>"
        ret += "\n"
        
        guests = list(db.events.get.votes(event_id).keys())
        for e in guests:
            insert = ""
            if db.people.exists.email(e):
                name = db.people.get.name(e)
                insert += f"{name} - {e}"
                if HTML:
                    insert = "<p style='font-size: 11px; color: #555;'>" + insert + "</p>"
                insert += "\n"
            else:
                insert += f"{e}"
                if HTML:
                    insert = "<p style='font-size: 11px; color: #555;'>" + insert + "</p>"
                insert += "\n"
            ret += insert

        return ret[:-1]

    @staticmethod
    def convert_time_to_24hr(time_str):
        time_obj = datetime.strptime(str(time_str), "%I:%M %p")
        return time_obj.strftime("%H:%M")

    @staticmethod
    def time_split(time_slot):
        return time_slot.split(" - ")

    @staticmethod
    def date_desc(date_string):
        date_obj = datetime.strptime(str(date_string), "%Y-%m-%d")
        def get_ordinal_suffix(day):
            if 11 <= day <= 13:
                return 'th'
            else:
                suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
                return suffixes.get(day % 10, 'th')
        formatted_date = date_obj.strftime(f"%B {date_obj.day}{get_ordinal_suffix(date_obj.day)}, %Y")
        return formatted_date

    @staticmethod
    def length_hours(time_slot):
        start_time_str, end_time_str = wrapper.time_split(time_slot)
        start_time_24hr = wrapper.convert_time_to_24hr(start_time_str)
        end_time_24hr = wrapper.convert_time_to_24hr(end_time_str)
        start_time_obj = datetime.strptime(start_time_24hr, "%H:%M")
        end_time_obj = datetime.strptime(end_time_24hr, "%H:%M")
        if end_time_obj <= start_time_obj:
            end_time_obj += timedelta(days=1)
        duration = (end_time_obj - start_time_obj).total_seconds() / 3600.0
        return duration

class mail:

    class subject:

        @staticmethod
        def get_approve(event_id:str)->str:

            date = db.events.get.date(event_id)
            winning_time, winning_location = db.votes.winner(event_id)

            return f"[{TAG_COMPANY_NAME}] Add {winning_location} on {wrapper.date_desc(date)} ({winning_time}) to your calendar!"

        @staticmethod
        def get_request(event_id: str)->str:
            
            date = db.events.get.date(event_id)
            winning_location = db.votes.winner(event_id)[1]

            return f"[{TAG_COMPANY_NAME}] {winning_location} on {wrapper.date_desc(date)} needs approval!"

        @staticmethod
        def get_invite(event_id: str)->str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)

            return f"[{TAG_COMPANY_NAME}] {name} from {company} sent an invitation on {wrapper.date_desc(date)}!"

        @staticmethod
        def get_reminder(event_id: str)->str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)

            return f"[{TAG_COMPANY_NAME}] A reminder to vote for ({company}) {name}'s event on {wrapper.date_desc(date)}!"
    
    class raw_email:

        @staticmethod
        def get_approve(event_id: str)->str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            winning_time, winning_location = db.votes.winner(event_id)

            row1 = "Event Approved"
            row2 = f"{name} from {company} has booked {winning_location} on {wrapper.date_desc(date)} at {winning_time}!"
            row3 = f"'{comment}'"
            row4 = f"Add {winning_location} to your calendar"
            row5 = "Attendees:"
            row6 = wrapper.attendees_list(event_id, False)
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6

        @staticmethod
        def get_request(event_id: str, request_link:str)->str:

            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            winning_time, winning_location = db.votes.winner(event_id)
            tally = db.votes.tally(event_id)
            len_guests = len(db.events.get.votes(event_id).keys())

            winning_time_votes = tally["times"][winning_time]
            winning_location_votes = tally["locations"][winning_location]

            times = ""
            for t in tally["times"].keys():
                t_count = tally["times"][t]
                time = f"{t} - {tally['times'][t]} out of {len_guests} votes"
                if t == winning_time: time += " (winner)"
                times += f"{t}\n"
            times = times[:-1]

            locations = ""
            for l in tally["locations"].keys():
                l_count = tally["locations"][l]
                location = f"{l} - {l_count} out of {len_guests} votes"
                if l == winning_location: location += " (winner)"

            row1 = "Approval Needed!"
            row2 = f"{winning_location} on {wrapper.date_desc(date)} ({winning_time}) needs approval!"
            row3 = f"'{comment}'"
            row4 = f"Approve Event - {request_link}"
            row5 = "Times:"
            row6 = times
            row7 = "Locations:"
            row8 = locations
            row9 = "Attendees:"
            row10 = wrapper.attendees_list(event_id, False)
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6 + '\n\n' + row7 + '\n\n' + row8 + '\n\n' + row9 + '\n\n' + row10

        @staticmethod
        def get_invite(event_id: str, voting_link:str)->str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            tally = db.votes.tally(event_id)

            row1 = "You're Invited!"
            row2 = f"{name} from {company} is inviting you to an event on {wrapper.date_desc(date)}!"
            row3 = f"'{comment}'"
            row4 = f"Vote Now - {voting_link}"
            row5 = "Times:"
            row6 = '\n'.join(f"{t}" for t in tally["times"].keys())
            row7 = "Locations:"
            row8 = '\n'.join(f"{l}" for l in tally["locations"].keys())
            row9 = "Attendees:"
            row10 = wrapper.attendees_list(event_id)
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6 + '\n\n' + row7 + '\n\n' + row8 + '\n\n' + row9 + '\n\n' + row10

        @staticmethod
        def get_reminder(event_id: str, voting_link:str)->str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            tally = db.votes.tally(event_id)

            tomorrow = today + timedelta(days=1)
            formatted_tomorrow = tomorrow.strftime('%Y-%m-%d')

            row1 = f"LAST DAY TO VOTE: {formatted_tomorrow}"
            row2 = f"{name} from {company} is inviting you to an event on {wrapper.date_desc(date)}!"
            row3 = f"'{comment}'"
            row4 = f"Votes Close Tomorrow - {voting_link}"
            row5 = "Times:"
            row6 = '\n'.join(f"{t}" for t in tally["times"].keys())
            row7 = "Locations:"
            row8 = '\n'.join(f"{l}" for l in tally["locations"].keys())
            row9 = "Attendees:"
            row10 = wrapper.attendees_list(event_id)
            
            return row1 + '\n\n' + row2 + '\n\n' + row3 + '\n\n' + row4 + '\n\n' + row5 + '\n\n' + row6 + '\n\n' + row7 + '\n\n' + row8 + '\n\n' + row9 + '\n\n' + row10
        
    class html_email:

        @staticmethod
        def get_approve(event_id: str) -> str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            winning_time, winning_location = db.votes.winner(event_id)

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #4CAF50; text-align: center;">Event Approved</h2>
                        <p style="font-size: 16px; color: #555; text-align: center;">
                            {name} from {company} has booked <strong>{winning_location}</strong> on <strong>{wrapper.date_desc(date)} at {winning_time}</strong>!
                        </p>
                        <p style="font-size: 14px; color: #555; text-align: center;">'{comment}'</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="#" style="background-color: #4CAF50; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Add {winning_location} to your calendar</a>
                        </p>
                        <h3 style="color: #333;">Attendees:</h3>
                        {wrapper.attendees_list(event_id, True)}
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_request(event_id: str, request_link: str) -> str:

            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            winning_time, winning_location = db.votes.winner(event_id)
            tally = db.votes.tally(event_id)
            len_guests = len(db.events.get.votes(event_id).keys())

            winning_time_votes = tally["times"][winning_time]
            winning_location_votes = tally["locations"][winning_location]

            times = ""
            for t in tally["times"].keys():
                t_count = tally["times"][t]
                time = f"<p style='font-size: 11px; color: #555;'>{t} - {tally['times'][t]} out of {len_guests} votes"
                if t == winning_time: time += " (winner)"
                time += "</p>"
                times += f"{time}\n"
            times = times[:-1]

            locations = ""
            for l in tally["locations"].keys():
                l_count = tally["locations"][l]
                location = f"<p style='font-size: 11px; color: #555;'>{l} - {l_count} out of {len_guests} votes"
                if l == winning_location: location += " (winner)"
                location += "</p>"
                locations += f"{location}\n"
            locations = locations[:-1]

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #007bff; text-align: center;">Approval Needed!</h2>
                        <p style="font-size: 16px; color: #555; text-align: center;"><strong>{winning_location}</strong> on <strong>{wrapper.date_desc(date)} ({winning_time})</strong> needs approval!</p>
                        <p style="font-size: 14px; color: #555; text-align: center;">'{comment}'</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{request_link}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Approve Event</a>
                        </p>
                        <div style="margin: 30px 0; border-top: 2px solid #ccc;"></div>
                        <h3 style="color: #333;">Times:</h3>
                        {times}
                        <h3 style="color: #333;">Locations:</h3>
                        {locations}
                        <h3 style="color: #333;">Attendees:</h3>
                        {wrapper.attendees_list(event_id, True)}
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_invite(event_id: str, voting_link: str) -> str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            time_options = db.events.get.times(event_id)
            location_options = db.events.get.locations(event_id)

            times = '\n'.join(f"<p style='font-size: 11px; color: #555;'>{t}</p>" for t in time_options)
            locations = '\n'.join(f"<p style='font-size: 11px; color: #555;'>{l}</p>" for l in location_options)

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff9800; text-align: center;">You're Invited!</h2>
                        <p style="font-size: 16px; color: #555; text-align: center;"><strong>{name}</strong> from <strong>{company}</strong> is inviting you to an event on <strong>{wrapper.date_desc(date)}</strong>!</p>
                        <p style="font-size: 14px; color: #555; text-align: center;">'{comment}'</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{voting_link}" style="background-color: #ff9800; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Vote Now</a>
                        </p>
                        <div style="margin: 30px 0; border-top: 2px solid #ccc;"></div>
                        <h3 style="color: #333;"><strong>Times:</strong></h3>
                        {times}
                        <h3 style="color: #333;"><strong>Locations:</strong></h3>
                        {locations}
                        <h3 style="color: #333;">Attendees:</h3>
                        {wrapper.attendees_list(event_id, True)}
                    </div>
                </body>
            </html>
            """
            return html_content

        @staticmethod
        def get_reminder(event_id: str, voting_link: str) -> str:

            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)
            company = db.events.get.company(event_id)
            date = db.events.get.date(event_id)
            comment = db.events.get.comment(event_id)
            tally = db.votes.tally(event_id)

            tomorrow = today + timedelta(days=1)
            formatted_tomorrow = tomorrow.strftime('%Y-%m-%d')

            times = '\n'.join(f"<p style='font-size: 11px; color: #555;'>{t}</p>" for t in tally["times"].keys())
            locations = '\n'.join(f"<p style='font-size: 11px; color: #555;'>{l}</p>" for l in tally["locations"].keys())

            html_content = f"""
            <html>
                <head></head>
                <body style="background-color: #f7f7f7; font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff9800; text-align: center;">LAST DAY TO VOTE: <strong>{formatted_tomorrow}</strong></h2>
                        <p style="font-size: 16px; color: #555; text-align: center;">{name} from {company} is inviting you to an event on <strong>{wrapper.date_desc(date)}</strong>!</p>
                        <p style="font-size: 14px; color: #555; text-align: center;">'{comment}'</p>
                        <p style="text-align: center; margin-top: 25px;">
                            <a href="{voting_link}" style="background-color: #ff9800; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Votes Close Tomorrow</a>
                        </p>
                        <div style="margin: 30px 0; border-top: 2px solid #ccc;"></div>
                        <h3 style="color: #333;"><strong>Times:</strong></h3>
                        {times}
                        <h3 style="color: #333;"><strong>Locations:</strong></h3>
                        {locations}
                        <h3 style="color: #333;">Attendees:</h3>
                        {wrapper.attendees_list(event_id, True)}
                    </div>
                </body>
            </html>
            """
            return html_content

    class attachments:

        @staticmethod
        def get_approve(event_id: str)->str:
            tally = db.votes.tally(event_id)
            date = db.events.get.date(event_id)
            winning_time, winning_location = db.votes.winner(event_id)
            winning_time_votes = tally["times"][winning_time]
            winning_location_votes = tally["locations"][winning_location]
            email = db.events.get.organizer_email(event_id)
            name = db.people.get.name(email)

            ret = []
            ret.append(PATH_FILE_CAL_EVENT(f"{winning_location}_{date}", winning_location, f"{winning_location} @ {wrapper.date_desc(date)} ({winning_time}) with {name}!",
                                           date, winning_time, name, db.events.get.timezone(event_id)))

            return ret

        @staticmethod
        def get_request(event_id: str)->list:
            
            return []

        @staticmethod
        def get_invite(event_id: str)->list:
            
            return []

        @staticmethod
        def get_reminder(event_id:str)->list:
            return []

# ------------------------------  ------------------------------ #
    
def SEND_EMAIL(Bcc=True, subject="", email_raw="", email_html="", attachments=[], recipients=[]):
    
    creds = GET_CREDENTIALS()
    ADDRESS = creds[0]
    PASSWORD = creds[1]

    if ADDRESS == "" or PASSWORD == "" or email_raw == "" or not recipients:
        return False

    x = 'Bcc'
    y = 'To'
    if Bcc:
        x = 'To'
        y = 'Bcc'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = ADDRESS
    msg[x] = ADDRESS
    msg[y] = ', '.join(recipients)
    msg.set_content(email_raw)

    if email_html != "":
        msg.add_alternative(email_html, subtype='html')

    # Add attachments
    for file_path in attachments:
        # Guess the content type based on the file's extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # If the type cannot be guessed, use a generic binary type
            mime_type = 'application/octet-stream'

        mime_type, mime_subtype = mime_type.split('/', 1)

        with open(file_path, 'rb') as file:
            msg.add_attachment(file.read(),
                               maintype=mime_type,
                               subtype=mime_subtype,
                               filename=os.path.basename(file_path))

    try:
        #print(f"user:'{ADDRESS}'\npass:'{PASSWORD}'\n")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(ADDRESS, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    # local versions of attachments deleted only when email(s) are successfully sent
    # NOTE: don't call sequentially. Multiple recipients -> list argument
    for filepath in attachments:
        if os.path.exists(filepath):
            os.remove(filepath)

    return True

class send:

    @staticmethod
    def approve(event_id:str, BCC=True):
        
        subject = mail.subject.get_approve(event_id)
        email_raw = mail.raw_email.get_approve(event_id)
        email_html = mail.html_email.get_approve(event_id)
        email_attachments = mail.attachments.get_approve(event_id)

        recipients = list(db.events.get.votes(event_id).keys()).copy()
        recipients.append(db.events.get.organizer_email(event_id))

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)

    @staticmethod
    def request(event_id:str, request_link:str, BCC=True):
        
        subject = mail.subject.get_request(event_id)
        email_raw = mail.raw_email.get_request(event_id, request_link)
        email_html = mail.html_email.get_request(event_id, request_link)
        email_attachments = mail.attachments.get_request(event_id)

        recipients = [db.events.get.organizer_email(event_id)]

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)

    @staticmethod
    def invite(event_id:str, voting_domain:str, BCC=True):
        
        subject = mail.subject.get_invite(event_id)
        email_attachments = mail.attachments.get_invite(event_id)

        recipients = list(db.events.get.votes(event_id).keys())

        #send for atendes
        ret = True
        for attendee in recipients:
            vid = db.events.get.votes(event_id)[attendee]
            website = os.path.join(VOTING_PAGE, f"?uuid={event_id}&vid={vid}")
            email_raw = mail.raw_email.get_invite(event_id, website)
            email_html = mail.html_email.get_invite(event_id, website)
            sent_rec = SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=[attendee])
            ret = ret and sent_rec

        #send for organizer
        website = os.path.join(VOTING_PAGE, f"?uuid={event_id}&vid={event_id}")
        email_raw = mail.raw_email.get_invite(event_id, website)
        email_html = mail.html_email.get_invite(event_id, website)
        sent = SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=[db.events.get.organizer_email(event_id)])
        
        return ret and sent

    @staticmethod
    def reminder():
        
        subject = mail.subject.get_reminder(event_id)
        email_raw = mail.raw_email.get_reminder(event_id, request_link)
        email_html = mail.html_email.get_reminder(event_id, request_link)
        email_attachments = mail.attachments.get_reminder(event_id)

        recipients = db.events.get.votes(event_id).keys().copy()
        recipients = recipients.append(event_id)

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)
