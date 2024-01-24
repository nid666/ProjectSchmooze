from email.message import EmailMessage
import smtplib

PRG_EMAIL = "delete.bins@gmail.com"
PRG_PASS = "gcpi mepa cxqm lqsa"
TAG_PROGRAM_NAME = "SCHMOOZE"
TAG_SUBJECT = " sent you an invitation on "
TAG_BODY_HEADER = " invited you to an event on "
TAG_SELECT_TIME = "Please select a time:"
TAG_SELECT_RESERVATION = "Please select a reservation:"

def get_HTML(locations: dict, times: list) -> str:
    html = f"<p>{TAG_SELECT_TIME}</p>\n"
    for t in times:
        html += f"""<p style="text-align: center;"><strong>{t}</strong></p>\n"""
    html += f"<p>&nbsp;</p>\n<p>{TAG_SELECT_RESERVATION}</p>\n"
    for l in locations.keys():
        html += f"""<p style="text-align: center;"><img src="{locations[l]}" alt=""/></p>
<p style="text-align: center;">{l}</p>\n\n"""
    return f"<html>\n<body>\n{html}</body>\n</html>"

def get_RAW(locations: dict, times: list) -> str:
    raw = f"{TAG_SELECT_TIME}\n\n"
    for t in times:
        raw += f"{t}\n"
    raw += f"\n{TAG_SELECT_RESERVATION}\n\n"
    for l in locations.keys():
        raw += f"{l}: {locations[l]}\n\n"
    return raw
    
def email(ADDRESS="", PASSWORD="", subject="", email_raw="", email_html="", Bcc=True, recipients=[]) -> bool:
    
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

def send_email(SENDER:str, DATE: str, RECIPIENTS: list, BCC: bool, locations: dict, times: list) -> bool:
    # recipients is a list of recipient's email addresses
    # locations: {location: image_link, ...}
    
    SUBJECT = f"[{TAG_PROGRAM_NAME}] {SENDER}{TAG_SUBJECT}{DATE}!"
    RAW = f"{SENDER}{TAG_SUBJECT}{DATE}.\n\n"
    RAW += get_RAW(locations, times)
    HTML = f"<p>{SENDER}{TAG_SUBJECT}{DATE}.</p>\n"
    HTML += get_HTML(locations, times)
    
    return email(ADDRESS=PRG_EMAIL, PASSWORD=PRG_PASS, subject=SUBJECT, email_raw=RAW, email_html=HTML, Bcc=BCC, recipients=RECIPIENTS)
