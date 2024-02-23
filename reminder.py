import _mail as sender
import database as db
import datetime

DOMAIN_NAME = "http://www.moodfor.xyz"

def reminder():

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    formatted_tomorrow = tomorrow.strftime('%Y-%m-%d')

    query = "SELECT uuid FROM events WHERE deadline = ?"
    params = (formatted_tomorrow,)
    events_tomorrow = tables.query(query, params, fetch="all")

    for event in events_tomorrow:
        uuid = event[0]
        sender.send.reminder(uuid)

    today = datetime.date.today()
    formatted_today = today.strftime('%Y-%m-%d')

    query = "SELECT uuid FROM events WHERE deadline = ?"
    params = (formatted_today,)
    events_today = tables.query(query, params, fetch="all")

    for event in events_today:
        uuid = event[0]
        db.events.set.complete(uuid)
        sender.send.request(uuid, f"{DOMAIN_NAME}?uuid={uuid}&apr=get", True)

reminder()
