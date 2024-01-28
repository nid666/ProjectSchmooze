from email.message import EmailMessage
import smtplib
import json
import email_bodys as body
import events_database as edb

PATH_CREDENTIALS_FILE = "secret/creds.json"

TAG_COMPANY_NAME = "SCHMOOZE"

def GET_CREDENTIALS():

    file_path = PATH_CREDENTIALS_FILE
    
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
    
def SEND_EMAIL(Bcc=True, subject="", email_raw="", email_html="", recipients=[]) -> bool:

    creds = GET_CREDENTIALS()
    ADDRESS = creds[0]
    PASSWORD = creds[1]
    
    if ADDRESS == "" or PASSWORD == "" or email_raw == "" or recipients == None: return False

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

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(ADDRESS, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return True

class send:

    @staticmethod
    def approve(uuid:str, BCC=True):
        
        event_dict = edb.unserialize_event(uuid)
        subject = f"[{TAG_COMPANY_NAME}] Add your event on {event_dict['date']} to your calendar!"
        email_raw = body.format.raw_email.get_approve()
        email_html = body.format.html_email.get_approve()

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, recipients=event_dict['emails'])

    @staticmethod
    def request(uuid:str, BCC=True):
        
        event_dict = edb.unserialize_event(uuid)
        subject = f"[{TAG_COMPANY_NAME}] Your event on {event_dict['date']} needs approval!"
        email_raw = body.format.raw_email.get_request()
        email_html = body.format.html_email.get_request()
        
        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, recipients=event_dict['emails'])

    @staticmethod
    def invite(uuid:str, BCC=True):
        
        event_dict = edb.unserialize_event(uuid)
        subject = f"[{TAG_COMPANY_NAME}] {event_dict['sender']} sent you an invitation on {event_dict["date"]}!"
        email_raw = body.format.raw_email.get_invite()
        email_html = body.format.html_email.get_invite()
        
        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, recipients=event_dict['emails'])
