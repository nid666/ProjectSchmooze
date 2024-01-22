from email.message import EmailMessage
import smtplib

PRG_EMAIL = "admin@admin.com"
PRG_PASS = "admin"
TAG_PROGRAM_NAME = "SCHMOOZE"
TAG_SUBJECT = " sent you an invitation on "
TAG_BODY_HEADER = " invited you to an event on "
TAG_SELECT_TIME = "Please select a time:"
TAG_SELECT_RESERVATION = "Please select a reservation:"

def get_HTML(locations, times) -> str:
    html = f"<p>{TAG_SELECT_TIME}</p>\n"
    for t in times.keys():
        html += f"""<p style="text-align: center;"><a href="{times[t]}"><strong>{t}</strong></a></p>\n"""
    html += f"<p>&nbsp;</p>\n<p>{TAG_SELECT_RESERVATION}</p>\n"
    for l in locations.keys():
        html += f"""<p style="text-align: center;"><img src="{locations[l][1]}" alt=""/></p>
<p style="text-align: center;"><a href="{locations[l][0]}">{l}</a></p>\n\n"""
    return html

def get_RAW(locations, times) -> str:
    raw = f"{TAG_SELECT_TIME}\n\n"
    for t in times.keys():
        raw += f"{t}: {times[t]}\n"
    raw += f"\n{TAG_SELECT_RESERVATION}\n\n"
    for l in locations.keys():
        raw += f"{l} ({locations[l][1]}):\n{locations[l][0]}\n\n"
    return raw
    
def email(ADDRESS="", PASSWORD="", subject="", email_raw="", email_html="", Bcc=True, *recipients) -> bool:
    
    if ADDRESS == "" or PASSWORD == "" or email_raw == "" or recipients == []: return False

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

def send_email(SENDER:str, DATE: str, RECIPIENTS: list, locations: dict, times: dict) -> bool:
    # recipients is a list of recipient's email addresses
    # locations dict format: {reservation_name: [voting_link, image_link], ...}
    # times dict format: {time: voting_link, ...}
    
    SUBJECT = f"[{TAG_PROGRAM_NAME}] {SENDER}{TAG_SUBJECT}{DATE}!"
    RAW = "{SENDER}{TAG_SUBJECT}{DATE}.\n\n"
    RAW = RAW + get_RAW(locations, times)
    HTML = get_HTML(locations, times)
    
    return email(ADDRESS=PRG_EMAIL, PASSWORD=PRG_PASS, subject=SUBJECT, email_raw=RAW, email_html=HTML, recipients=RECIPIENTS)
