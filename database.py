import os
import uuid
import json
import yaml
import datetime
import sqlite3
import _mail as sender
from datetime import datetime
from yaml.loader import SafeLoader

# ------------------------------  ------------------------------ #

# TEMPORARY FUNCTIONS USED FOR PRESENTATION (MEANT TO BE DELETED AND REPLACED ELENTUALLY BY OPTIMAL, EFFICIENT SOLUTIONS
# EASY IMPLEMENTATIONS TO BE REPLACED LATER

def to_time_str_list(time_tuples):
    return [f"{start} - {end}" for start, end in time_tuples]

def to_24_format(time_str_list):
    def convert_to_12_hour(time_str):
        hour, minute = map(int, time_str.split(':'))
        part = "AM" if hour < 12 else "PM"
        hour = hour % 12
        hour = 12 if hour == 0 else hour
        return f"{hour:02d}:{minute:02d} {part}"
    return [f"{convert_to_12_hour(start)} - {convert_to_12_hour(end)}" for start, end in (time.split(' - ') for time in time_str_list)]

def time_tuple_wrapper(tuples:list)->list:
    return to_24_format(to_time_str_list(tuples))

# ------------------------------  ------------------------------ #

def UUID() -> str:
    return str(uuid.uuid4())

def YAML() -> dict:
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def list_to_str(l: list) -> str:
    try:
        return json.dumps(l)
    except Exception as e:
        print(e)
        return ""
        
def str_to_list(s: str) -> list:
    try:
        return json.loads(s)
    except Exception as e:
        print(e)
        return []

def dict_to_str(d: dict) -> str:
    try:
        return json.dumps(d)
    except Exception as e:
        print(e)
        return ""
        
def str_to_dict(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception as e:
        print(e)
        return {}

# ------------------------------  ------------------------------ #

DOMAIN_NAME = "https://www.moodfor.xyz"
PATH_FILE_DB = "tables.db"

conn = sqlite3.connect(PATH_FILE_DB)
cursor_start = conn.cursor()

if not os.path.exists(PATH_FILE_DB):
    with open(PATH_FILE_DB, 'w') as f:
        pass

# Create 'people' table
cursor_start.execute('''
CREATE TABLE IF NOT EXISTS people (
    email TEXT UNIQUE PRIMARY KEY NOT NULL,
    username TEXT UNIQUE,
    name TEXT
);
''') # enforce unique usernames, and unique person name in post

# Create 'voting' table
cursor_start.execute('''
CREATE TABLE IF NOT EXISTS voting (
    event_id TEXT NOT NULL,
    voting_id TEXT UNIQUE PRIMARY KEY NOT NULL,
    chosen_location TEXT,
    chosen_time TEXT
);
''')

# Create 'events' table
# Storing 'times' and 'locations' as JSON strings in TEXT columns
# 'votes' is also stored as a JSON string
cursor_start.execute('''
CREATE TABLE IF NOT EXISTS events (
    uuid TEXT UNIQUE PRIMARY KEY NOT NULL,
    company TEXT,
    organizer TEXT NOT NULL REFERENCES people(email),
    organizer_loc TEXT NOT NULL,
    date TEXT NOT NULL,
    comment TEXT,
    deadline TEXT NOT NULL,
    budget TEXT,
    timezone TEXT NOT NULL,
    times TEXT NOT NULL,
    locations TEXT NOT NULL,
    votes TEXT NOT NULL
);
''')# votes = {pid REFERENCES people(email):uid REFERENCES voting(voting_id)}

# ------------------------------  ------------------------------ #

class tables:

    @staticmethod
    def query(query: str, params: tuple = (), fetch: str = "all") -> tuple:
        conn = sqlite3.connect(PATH_FILE_DB)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            operation = query.lower().strip().split()[0]

            if operation in ["insert", "update", "delete"]:
                conn.commit()
                return (cursor.rowcount,)

            elif operation == "select":
                if fetch == "all":
                    return tuple(cursor.fetchall())
                elif fetch == "one":
                    return (cursor.fetchone(),)
            return (None,)

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return (None,)

    @staticmethod
    def print(table_name):

        conn = sqlite3.connect(PATH_FILE_DB)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            exists = cursor.fetchone()
            
            if exists:
                print(f"Table '{table_name}' exists. Fetching its contents...")
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                print(f"Table '{table_name}' does not exist.")
        
        except sqlite3.OperationalError as e:
            print(f"An error occurred: {e}")
        
        finally:
            conn.close()
            print("\n\n------ print {table_name} table end ------\n\n")


# ------------------------------  ------------------------------ #


class people:

    class exists:

        @staticmethod
        def email(email:str) -> bool:
            result = tables.query("SELECT 1 FROM people WHERE email = ?", (email,), "one")
            return result[0] is not None

        @staticmethod
        def username(username:str) -> bool:
            result = tables.query("SELECT 1 FROM people WHERE username = ?", (username,), "one")
            return result[0] is not None

    class get:

        @staticmethod
        def username(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT username FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT username FROM people WHERE username = ?", (s,), "one")
            return result[0][0] if result else None

        @staticmethod
        def email(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT email FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT email FROM people WHERE username = ?", (s,), "one")
            return result[0][0] if result else None

        @staticmethod
        def name(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT name FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT name FROM people WHERE username = ?", (s,), "one")
            return result[0][0] if result else None
        
    class set:

        @staticmethod
        def username(s:str, new:str) -> bool:
            if people.exists.email(s) and not people.exists.username(new):
                result = tables.query("UPDATE people SET username = ? WHERE email = ?", (new, s))
                return result[0] > 0
            elif people.exists.username(s) and not people.exists.username(new):
                result = tables.query("UPDATE people SET username = ? WHERE username = ?", (new, s))
                return result[0] > 0
            return False

        @staticmethod
        def email(s:str, new:str) -> bool:
            if people.exists.email(s) and not people.exists.email(new):
                result = tables.query("UPDATE people SET email = ? WHERE email = ?", (new, s))
                return result[0] > 0
            elif people.exists.username(s) and not people.exists.email(new):
                result = tables.query("UPDATE people SET email = ? WHERE username = ?", (new, s))
                return result[0] > 0
            return False

        @staticmethod
        def name(s:str, new:str) -> bool:
            if people.exists.email(s):
                result = tables.query("UPDATE people SET name = ? WHERE email = ?", (new, s))
                return result[0] > 0
            elif people.exists.username(s):
                result = tables.query("UPDATE people SET name = ? WHERE username = ?", (new, s))
                return result[0] > 0
            return False

    @staticmethod
    def sync():
        yalm_dict = YAML()
        yalm_accounts = yalm_dict['credentials']['usernames']
        for username in yalm_accounts.keys():
            email = yalm_accounts[username]["email"]
            name = yalm_accounts[username]["name"]
            print(f"syncing: {username}->{email}->{name}")
            if not people.exists.email(email) or not people.exists.username(username):
                print("sync complete!")
                people.create(email, username, name)
            else:
                print("sync failed!")

    @staticmethod
    def create(email:str = "", username:str = "", name:str = "")->bool:
        if email == "": return False
        result = tables.query("INSERT INTO people (email, username, name) VALUES (?, ?, ?)", (email, username, name))
        return result[0] > 0

class votes:

    @staticmethod
    def exists(event_id: str, voting_id:str) -> bool:
        return tables.query("SELECT 1 FROM voting WHERE event_id = ? AND voting_id = ?", (event_id, voting_id), "one") != (None,)

    class get:

        @staticmethod
        def location(event_id: str, voting_id: str) -> str:
            result = tables.query("SELECT chosen_location FROM voting WHERE event_id = ? AND voting_id = ?", (event_id, voting_id), "one")
            return result[0][0] if result and result[0] else None

        @staticmethod
        def time(event_id: str, voting_id: str) -> str:
            result = tables.query("SELECT chosen_time FROM voting WHERE event_id = ? AND voting_id = ?", (event_id, voting_id), "one")
            return result[0][0] if result and result[0] else None

    @staticmethod
    def create(event_id:str = "", voting_id:str = ""):
        if not events.exists(event_id): return False
        if voting_id == "": return False
        result = tables.query("INSERT INTO voting (event_id, voting_id, chosen_location, chosen_time) VALUES (?, ?, ?, ?)", (event_id, voting_id, None, None))
        return result[0] > 0

    @staticmethod
    def cast(event_id:str = "", voting_id:str = "", chosen_location:str = None, chosen_time:str = None)->bool:
        if not events.exists(event_id): return False
        if not events._is.active(event_id): return False
        if not votes.exists(event_id, voting_id): return False

        result = tables.query("UPDATE voting SET chosen_location = ?, chosen_time = ? WHERE event_id = ? AND voting_id = ?", (chosen_location, chosen_time, event_id, voting_id))

        max_votes_count = len(events.get.votes(event_id).keys())
        maj_votes_count = ((max_votes_count+1)//2)+1
        tally = votes.tally(event_id)
        w_time, w_location = votes.winner(event_id)
        w_time_score = tally['times'][w_time]
        w_location_score = tally['locations'][w_location]

        print(f"tally is:\n{tally}\n")
        print(f"winningtime:{w_time}\nwinninglocation:{w_location}\n")

        print(f"w_time_score is {w_time_score}")
        print(f"w_location_score is {w_location_score}")
        print(f"w_time is {w_time}")
        print(f"w_location is {w_location}")

        print(f"w_time_score >= maj_votes_count -> ({w_time_score >= maj_votes_count})")
        print(f"w_location_score >= maj_votes_count -> ({w_location_score >= maj_votes_count})")

        if (w_time_score >= maj_votes_count and w_location_score >= maj_votes_count):
            print("vote sent")
            events.set.complete(event_id)
            sender.send.request(event_id, f"{DOMAIN_NAME}/aprPage/?uuid={event_id}&apr=get", True)
        else:
            print("vote not sent")

        if result[0] is not None and result[0] > 0:
            print(f"CAST SUCCESS::\n\tRESULT[0]: {result[0]}\n\tevent id: {event_id}\n\tvid: {voting_id}\n\tchosen location: {chosen_location}\n\tchosen time: {chosen_time}\n")
            return result[0] > 0
        else:
            print(f"CAST ERROR::\n\tRESULT[0]: {result[0]}\n\tevent id: {event_id}\n\tvid: {voting_id}\n\tchosen location: {chosen_location}\n\tchosen time: {chosen_time}\n")
            
    @staticmethod
    def tally(event_id: str = "") -> dict:
        if not events.exists(event_id): return {}
        rows = tables.query("SELECT chosen_location, chosen_time FROM voting WHERE event_id = ?", (event_id,))

        location_counts = {}
        event_locations = events.get.locations(event_id)
        for l in event_locations:
            location_counts[l] = 0

        time_counts = {}
        event_times = events.get.times(event_id)
        for t in event_times:
            time_counts[t] = 0

        for chosen_location, chosen_time in rows:
            if chosen_location is not None and chosen_location in location_counts.keys():
                location_counts[chosen_location] += 1
            if chosen_time is not None and chosen_time in time_counts.keys():
                time_counts[chosen_time] += 1

        sorted_locations = {k: v for k, v in sorted(location_counts.items(), key=lambda item: item[1], reverse=True)}
        sorted_times = {k: v for k, v in sorted(time_counts.items(), key=lambda item: item[1], reverse=True)}

        return {
            'locations': sorted_locations,
            'times': sorted_times
        }

    @staticmethod
    def winner(event_id: str) -> tuple:
        voting_dict = votes.tally(event_id)
        return (list(voting_dict['times'].keys())[0], list(voting_dict['locations'].keys())[0])
    
class events:

    @staticmethod
    def exists(event_id: str) -> bool:
        return tables.query("SELECT 1 FROM events WHERE uuid = ?", (event_id,), "one") != (None,)

    @staticmethod
    def create(event_id: str, company:str, organizer_email: str, organizer_loc: str, date: str, comment:str, deadline: str, budget: str, timezone:str, times: list, locations: list, votes: dict) -> bool:

        location_str = dict_to_str(organizer_loc)

        print(f"times pre-format:\n\t{times}")
        wrapper_times = time_tuple_wrapper(times)
        print(f"times pre-format:\n\t{wrapper_times}")
        times_str = list_to_str(wrapper_times)
        
        locations_str = list_to_str(locations)
        votes_str = dict_to_str(votes)

        result = tables.query("INSERT INTO events (uuid, company, organizer, organizer_loc, date, comment, deadline, budget, timezone, times, locations, votes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                (event_id, company, organizer_email, location_str, date, comment, deadline, budget, timezone, times_str, locations_str, votes_str))

        print(result)
        return result[0] > 0

    class _is:

        @staticmethod
        def attendee(eid:str, vid:str)->bool:
            in_votes_dict = vid in events.get.votes(eid).values()
            return events.exists(eid) and in_votes_dict
        
        @staticmethod
        def complete(event_id: str) -> bool:
            result = tables.query("SELECT deadline FROM events WHERE uuid = ?", (event_id,), "one")
            if result and result[0] and result[0][0] == "COMPLETED":
                return True
            return False

        @staticmethod
        def cancel(event_id: str) -> bool:
            result = tables.query("SELECT deadline FROM events WHERE uuid = ?", (event_id,), "one")
            if result and result[0] and result[0][0] == "CANCELLED":
                return True
            return False

        @staticmethod
        def active(event_id: str) -> bool:
            result = tables.query("SELECT deadline FROM events WHERE uuid = ?", (event_id,), "one")
            if result and result[0] and result[0][0] != "CANCELLED" and result[0][0] != "COMPLETED":
                return True
            return False

    class set:
        @staticmethod
        def complete(event_id: str) -> bool:
            if events._is.active(event_id):
                result = tables.query("UPDATE events SET deadline = 'COMPLETED' WHERE uuid = ?", (event_id,))
                return result[0] > 0
            return False

        @staticmethod
        def cancel(event_id: str) -> bool:
            if events._is.active(event_id):
                result = tables.query("UPDATE events SET deadline = 'CANCELLED' WHERE uuid = ?", (event_id,))
                return result[0] > 0
            return False

        
    class get:

        @staticmethod
        def company(event_id: str) -> str:
            result = tables.query("SELECT company FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def organizer_email(event_id: str) -> str:
            result = tables.query("SELECT organizer FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def organizer_loc(event_id: str) -> str:
            result = tables.query("SELECT organizer_loc FROM events WHERE uuid = ?", (event_id,), "one")
            return str_to_dict(result[0][0]) if result else None

        @staticmethod
        def date(event_id: str) -> str:
            result = tables.query("SELECT date FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def comment(event_id: str) -> str:
            result = tables.query("SELECT comment FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def deadline(event_id: str) -> str:
            result = tables.query("SELECT deadline FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def budget(event_id: str) -> str:
            result = tables.query("SELECT budget FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def timezone(event_id: str) -> str:
            result = tables.query("SELECT timezone FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def times(event_id: str) -> list:
            result = tables.query("SELECT times FROM events WHERE uuid = ?", (event_id,), "one")
            return str_to_list(result[0][0]) if result else []

        @staticmethod
        def locations(event_id: str) -> list:
            result = tables.query("SELECT locations FROM events WHERE uuid = ?", (event_id,), "one")
            return str_to_list(result[0][0]) if result else []

        @staticmethod
        def votes(event_id: str) -> dict:
            result = tables.query("SELECT votes FROM events WHERE uuid = ?", (event_id,), "one")
            return str_to_dict(result[0][0]) if result else {}

class analysis:

    def averages(date_range="", avg_type="", mode="all", exclude="", *flags):
        return

people.sync()

"""
events.exists() -- WORKS
events.create() -- WORKS

'''
print(f"\nThe table '{EVENT_ID1}' exists: {events.exists(EVENT_ID1)}\n")
print_table("events")
print("CREATING NEW EVENT -> " + str(events.create(event_id=E1["event_id"],
              company=E1["company"],
              organizer_email=E1["organizer_email"],
              organizer_loc=E1["organizer_loc"],
              date=E1["date"],
              comment=E1["comment"],
              deadline=E1["deadline"],
              budget=E1["budget"],
              timezone=E1["timezone"],
              times=E1["times"],
              locations=E1["locations"],
              votes=E1["votes"]))
print(f"\nThe table '{EVENT_ID1}' exists: {events.exists(EVENT_ID1)}\n")
print_table("events")
'''


events._is.attendee() -- WORKS


'''
print_table("events")

FAKE_ID = "FAKE_VID"

print(f"{VOTING1_ID1} is attending {EVENT_ID1}: {events._is.attendee(EVENT_ID1, VOTING1_ID1)}")
print(f"{VOTING1_ID2} is attending {EVENT_ID1}: {events._is.attendee(EVENT_ID1, VOTING1_ID2)}")
print(f"{FAKE_ID} is attending {EVENT_ID1}: {events._is.attendee(EVENT_ID1, FAKE_ID)}")
'''

events._is.active()   -- WORKS
events._is.complete() -- WORKS
events._is.cancel()   -- WORKS
events.set.complete() -- WORKS
events.set.cancel()   -- WORKS

'''

print(f"\n\nevent is active: {events._is.active(E1['event_id'])}\n\n")

print(f"\n\nevent is complete: {events._is.complete(E1['event_id'])}\n\n")
print(f"\n\nevent is cancel: {events._is.cancel(E1['event_id'])}\n\n")

print_table("events")

print("setting events...\n")
print(f"CANCEL: {events.set.cancel(E1['event_id'])}")
print(f"COMPLETE: {events.set.complete(E1['event_id'])}")

print_table("events")

print(f"\n\nevent is complete: {events._is.complete(E1['event_id'])}\n\n")
print(f"\n\nevent is cancel: {events._is.cancel(E1['event_id'])}\n\n")

print(f"\n\nevent is active: {events._is.active(E1['event_id'])}\n\n")

print_table("events")

'''

is_attendee = events._is.attendee(eid="placeholder_event_id", vid="placeholder_voting_id")
is_event_complete = events._is.complete(event_id="placeholder_event_id")
is_event_cancelled = events._is.cancel(event_id="placeholder_event_id")
is_event_active = events._is.active(event_id="placeholder_event_id")
set_event_complete = events.set.complete(event_id="placeholder_event_id")
set_event_cancel = events.set.cancel(event_id="placeholder_event_id")
company_name = events.get.company(event_id="placeholder_event_id")
organizer_email = events.get.organizer_email(event_id="placeholder_event_id")
organizer_location = events.get.organizer_loc(event_id="placeholder_event_id")
event_date = events.get.date(event_id="placeholder_event_id")
event_comment = events.get.comment(event_id="placeholder_event_id")
event_deadline = events.get.deadline(event_id="placeholder_event_id")
event_budget = events.get.budget(event_id="placeholder_event_id")
event_timezone = events.get.timezone(event_id="placeholder_event_id")
event_times = events.get.times(event_id="placeholder_event_id")
event_locations = events.get.locations(event_id="placeholder_event_id")
event_votes = events.get.votes(event_id="placeholder_event_id")

'''

WORKS

print(f"company:  {events.get.company(E1['event_id'])}")
print(f"organizer_email:  {events.get.organizer_email(E1['event_id'])}")
print(f"organizer_loc:  {events.get.organizer_loc(E1['event_id'])}")
print(f"date:  {events.get.date(E1['event_id'])}")
print(f"comment:  {events.get.comment(E1['event_id'])}")
print(f"deadline:  {events.get.deadline(E1['event_id'])}")
print(f"budget:  {events.get.budget(E1['event_id'])}")
print(f"timezone:  {events.get.timezone(E1['event_id'])}")
print(f"times:  {events.get.times(E1['event_id'])}")
print(f"locations:  {events.get.locations(E1['event_id'])}")
print(f"votes:  {events.get.votes(E1['event_id'])}")

'''

print_table("people")

print("before sync...")
people.sync()

print_table("people")

people.create("echo@gmail.com", "bm30", "Black")

print_table("people")

print(f"Does username 'bm30' exist?: {people.exists.username('bm30')}")
print(f"Does username 'bm40' exist?: {people.exists.username('bm40')}")
print(f"Does email 'echo@gmail.com' exist?: {people.exists.email('echo@gmail.com')}")
print(f"Does email 'dlb330@rutgers.edu' exist?: {people.exists.email('dlb330@rutgers.edu')}")

print_table("people")

print(f"Username for 'bm30': {people.get.username('bm30')}")
print(f"updated username: {people.set.username('bm30', 'bm40')}")
print(f"Updated username for 'bm30': {people.get.username('bm40')}")

print_table("people")

print(f"Email for 'bm40': {people.get.email('bm40')}")
print(f"updated email: {people.set.email('bm40', 'replaced@gmail.com')}")
print(f"Updated email for 'bm40': {people.get.email('bm40')}")

print_table("people")

print(f"Name for 'bm40': {people.get.name('bm40')}")
print(f"updated name: {people.set.name('bm40', 'White')}")
print(f"Updated name for 'bm40': {people.get.name('bm40')}")

print_table("people")

print(f"Username for 'replaced@gmail.com': {people.get.username('replaced@gmail.com')}")
print(f"updated username: {people.set.username('replaced@gmail.com', 'bm50')}")
print(f"Updated username for 'replaced@gmail.com': {people.get.username('replaced@gmail.com')}")

print_table("people")

print(f"Email for 'replaced@gmail.com': {people.get.email('replaced@gmail.com')}")
print(f"updated email: {people.set.email('replaced@gmail.com', 'echo@gmail.com')}")
print(f"Updated email for 'echo@gmail.com': {people.get.email('echo@gmail.com')}")

print_table("people")

print(f"Name for 'replaced@gmail.com' replaced with 'echo@gmail.com': {people.get.name('echo@gmail.com')}")
print(f"updated name: {people.set.name('echo@gmail.com', 'Black')}")
print(f"Updated name for 'replaced@gmail.com': {people.get.name('echo@gmail.com')}")

print_table("people")

print("after sync...")
people.sync()

#people.sync()

# VOTES TEST

#result_create_vote = votes.create(event_id="placeholder_event_id", voting_id="placeholder_voting_id")
#result_cast_vote = votes.cast(event_id="placeholder_event_id", voting_id="placeholder_voting_id", chosen_location="placeholder_location", chosen_time="placeholder_time")
#tally_result = votes.tally(event_id="placeholder_event_id")
#winner_time, winner_location = votes.winner(event_id="placeholder_event_id")




print("[[ STARTING TEST! ]]\n\n")

L1 = "L1"
L2 = "L2"
L3 = "L3"
L4 = "L4"
T1 = "T1"
T2 = "T2"
T3 = "T3"

print("CREATING NEW EVENT -> " + str(events.create(event_id=E1["event_id"],
              company=E1["company"],
              organizer_email=E1["organizer_email"],
              organizer_loc=E1["organizer_loc"],
              date=E1["date"],
              comment=E1["comment"],
              deadline=E1["deadline"],
              budget=E1["budget"],
              timezone=E1["timezone"],
              times=E1["times"],
              locations=E1["locations"],
              votes=E1["votes"])))

print_table("voting")

print(f"Voting row 1 created: {votes.create(EVENT_ID1, VOTING1_ID1)}")
print(f"Voting row 2 created: {votes.create(EVENT_ID1, VOTING1_ID2)}")

print(f"Vote 1 location: {votes.get.location(EVENT_ID1, VOTING1_ID1)}")
print(f"Vote 1 time: {votes.get.time(EVENT_ID1, VOTING1_ID1)}")
print(f"Vote 2 location: {votes.get.location(EVENT_ID1, VOTING1_ID2)}")
print(f"Vote 2 time: {votes.get.time(EVENT_ID1, VOTING1_ID2)}")

print_table("voting")

print(f"Vote 1 casted: {votes.cast(EVENT_ID1, VOTING1_ID1, 'Nobu', '11:00 AM - 12:00 PM')}")
print(f"vote 2 casted: {votes.cast(EVENT_ID1, VOTING1_ID2, 'Supercharged', '11:00 AM - 12:00 PM')}")

print(f"Vote 1 location: {votes.get.location(EVENT_ID1, VOTING1_ID1)}")
print(f"Vote 1 time: {votes.get.time(EVENT_ID1, VOTING1_ID1)}")
print(f"Vote 2 location: {votes.get.location(EVENT_ID1, VOTING1_ID2)}")
print(f"Vote 2 time: {votes.get.time(EVENT_ID1, VOTING1_ID2)}")

print_table("voting")

print(f"Event 1 tally:\n\n{votes.tally(EVENT_ID1)}")
print(f"Event 1 winners:\n\n {votes.winner(EVENT_ID1)}")

print_table("voting")

os.remove(PATH_FILE_DB)

"""

"""

EVENT_ID1 = "E1"
VOTING1_ID1 = "V1_1"
VOTING1_ID2 = "V1_2"


E1 = {
    "event_id":EVENT_ID1,
    "company":"fg13",
    "organizer_email":"echo@gmail.com",
    "organizer_loc":{},
    "date":"2024/03/01",
    "comment":"this is a members only event! present you referal card at entry!",
    "deadline":"2024/02/28",
    "budget":400,
    "timezone":"America/New_York",
    "times":[('10:00','11:00'), ('11:00','12:00')],
    "locations":["Nobu", "Five Guys", "Supercharged"],
    "votes":{
        "replaced@gmail.com":VOTING1_ID1,
        "dlb330@rutgers.edu":VOTING1_ID2,
        "dlb660@rutgers.edu":"fsgsgfs",
        "Bruh6@gmail.com":"h3rrh3rh",
        "tahoo.yahoo@gmail.com":"cdggcddgc",
        "tanker.gmail.com":"gbssbbtt"
        }
    }

print("CREATING NEW EVENT -> " + str(events.create(event_id=E1["event_id"],
              company=E1["company"],
              organizer_email=E1["organizer_email"],
              organizer_loc=E1["organizer_loc"],
              date=E1["date"],
              comment=E1["comment"],
              deadline=E1["deadline"],
              budget=E1["budget"],
              timezone=E1["timezone"],
              times=E1["times"],
              locations=E1["locations"],
              votes=E1["votes"])))

tables.print("voting")

for email in E1['votes'].keys():
    print(f"Voting row created: {votes.create(EVENT_ID1, E1['votes'][email])}")

count = 1
for email in E1['votes'].keys():
    print(f"Voting row {count} casted: {votes.cast(EVENT_ID1, E1['votes'][email], 'Five Guys', 'Supercharged')}")
    x = input("Proceed (Y/N)?: ")
    if x.lower() == 'n': break
    count += 1



os.remove(PATH_FILE_DB)


"""

"""

# people class function calls
people_exists_email = people.exists.email(email="placeholder_email")
people_exists_username = people.exists.username(username="placeholder_username")
username = people.get.username(s="placeholder_email_or_username")
email = people.get.email(s="placeholder_email_or_username")
name = people.get.name(s="placeholder_email_or_username")
set_username_result = people.set.username(s="placeholder_email_or_username", new="new_placeholder_username")
set_email_result = people.set.email(s="placeholder_email_or_username", new="new_placeholder_email")
set_name_result = people.set.name(s="placeholder_email_or_username", new="new_placeholder_name")
create_person_result = people.create(email="placeholder_email", username="placeholder_username", name="placeholder_name")
"""
