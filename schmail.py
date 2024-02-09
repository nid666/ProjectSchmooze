from email.message import EmailMessage
import smtplib
import json
import email_bodys as body
import events_database as edb
import os
import mimetypes

PATH_CREDENTIALS_FILE = "secret/creds.json"

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
    def approve(uuid:str, BCC=True):
        
        event_dict = edb.event.details.unserialize(uuid)
        subject = body.format.subject.get_approve(event_dict)
        email_raw = body.format.raw_email.get_approve(event_dict)
        email_html = body.format.html_email.get_approve(event_dict)
        email_attachments = body.format.attachments.get_approve(event_dict)

        recipients = event_dict['recipients'].copy()
        recipients.append(event_dict['sender'])

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)

    @staticmethod
    def request(uuid:str, request_link:str, BCC=True):
        
        event_dict = edb.event.details.unserialize(uuid)
        subject = body.format.subject.get_request(event_dict)
        email_raw = body.format.raw_email.get_request(event_dict, request_link)
        email_html = body.format.html_email.get_request(event_dict, request_link)
        email_attachments = body.format.attachments.get_request(event_dict)

        recipients = [event_dict['sender']]

        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)

    @staticmethod
    def invite(uuid:str, voting_link:str, BCC=True):
        
        event_dict = edb.event.details.unserialize(uuid)
        subject = body.format.subject.get_invite(event_dict)
        email_raw = body.format.raw_email.get_invite(event_dict, voting_link)
        email_html = body.format.html_email.get_invite(event_dict, voting_link)
        email_attachments = body.format.attachments.get_invite(event_dict)

        recipients = event_dict['recipients']
        
        return SEND_EMAIL(Bcc=BCC, subject=subject, email_raw=email_raw, email_html=email_html, attachments=email_attachments, recipients=recipients)




