import os
import uuid
import json
import yaml
import datetime
import sqlite3
import _mail as sender
from yaml.loader import SafeLoader

# ------------------------------  ------------------------------ #

def UUID() -> str:
    return str(uuid.uuid4())

def YAML() -> dict:
    with open('config.yaml') as file:
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

DOMAIN_NAME = "http://schmooze.us.to/"
PATH_FILE_DB = "tables.db"

if not os.path.exists(PATH_FILE_DB):
    with open(PATH_FILE_DB, 'w') as f:
        pass

conn = sqlite3.connect(PATH_FILE_DB)
cursor = conn.cursor()

# Create 'people' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS people (
    email TEXT UNIQUE PRIMARY KEY NOT NULL,
    username TEXT UNIQUE,
    name TEXT,
    company TEXT
);
''') # enforce unique usernames, and unique person name in post

# Create 'voting' table
cursor.execute('''
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
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    uuid TEXT UNIQUE PRIMARY KEY NOT NULL,
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
        try:
            cursor.execute(query, params)
            operation = query.strip().lower().split()[0]
            if operation in ["insert", "update", "delete"]:
                conn.commit()
                return (cursor.rowcount,)

            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return (cursor.fetchone(),)
            else:
                return ()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return ()

class people:

    class exists:

        @staticmethod
        def email(email:str) -> bool:
            return tables.query("SELECT 1 FROM people WHERE email = ?", (email,), "one") is not None

        @staticmethod
        def username(username:str) -> bool:
            return tables.query("SELECT 1 FROM people WHERE username = ?", (username,), "one") is not None

    class get:

        @staticmethod
        def username(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT username FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT username FROM people WHERE username = ?", (s,), "one")
            return result[0] if result else None

        @staticmethod
        def email(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT email FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT email FROM people WHERE username = ?", (s,), "one")
            return result[0] if result else None

        @staticmethod
        def name(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT name FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT name FROM people WHERE username = ?", (s,), "one")
            return result[0] if result else None

        @staticmethod
        def company(s:str) -> str:
            result = None
            if people.exists.email(s):
                result = tables.query("SELECT company FROM people WHERE email = ?", (s,), "one")
            elif people.exists.username(s):
                result = tables.query("SELECT company FROM people WHERE username = ?", (s,), "one")
            return result[0] if result else None
        
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
        def company(s:str, new:str) -> bool:
            if people.exists.email(s):
                result = tables.query("UPDATE people SET company = ? WHERE email = ?", (new, s))
                return result[0] > 0
            elif people.exists.username(s):
                result = tables.query("UPDATE people SET company = ? WHERE username = ?", (new, s))
                return result[0] > 0
            return False

    @staticmethod
    def sync():
        yalm_dict = YAML()
        yalm_accounts = yalm_dict.get('credentials', {}).get('usernames', {})
        for username in yalm_accounts.keys():
            email = yalm_accounts[username]["email"]
            name = yalm_accounts[username]["name"]
            if not people.exists.email(email) or not people.exists.username(username):
                people.create(email, username, name)

    @staticmethod
    def create(email:str = "", username:str = "", name:str = "", company:str = "")->bool:
        if email == "": return False
        result = tables.query("INSERT INTO people (email, username, name, company) VALUES (?, ?, ?, ?)", (email, username, name, company))
        return result[0] > 0

class votes:

    @staticmethod
    def cast(event_id:str = "", voting_id:str = "", chosen_location:str = "", chosen_time:str = "")->bool:
        if not events.exists(event_id): return False
        if voting_id == "": return False
        result = tables.query("INSERT INTO voting (event_id, voting_id, chosen_location, chosen_time) VALUES (?, ?, ?, ?)", (event_id, voting_id, chosen_location, chosen_time))

        max_votes_count = len(events.get.votes(event_id).keys())
        maj_votes_count = (max_votes_count/2)+1
        tally = votes.tally(event_id)
        w_time, w_location = votes.winner(event_id)

        maj_time = (tally['times'][w_time] >= maj_votes_count)
        maj_location = (tally['locations'][w_location] >= maj_votes_count)
        if maj_time and maj_location:
            events.set.complete(event_id)
            sender.send.request(event_id, f"{DOMAIN_NAME}?uuid={uuid}&apr=get", True)
    
        return result[0] > 0

    @staticmethod
    def tally(event_id: str = "") -> dict:
        if not events.exists(event_id):
            return False
        rows = tables.query("SELECT chosen_location, chosen_time FROM voting WHERE event_id = ?", (event_id,))

        location_counts = {}
        event_locations = events.get.locations(event_id)
        for l in event_locations:
            location_counts[l] = 0

        time_counts = {}
        event_times = events.get.times(event_id)
        for t in event_times:
            time_counts[l] = 0

        for chosen_location, chosen_time in rows:
            if chosen_location in location_counts.keys():
                location_counts[chosen_location] += 1
            else:
                location_counts[chosen_location] = 0
            if chosen_time in time_counts.keys():
                time_counts[chosen_time] += 1
            else:
                time_counts[chosen_time] = 0

        sorted_locations = {k: v for k, v in sorted(location_counts.items(), key=lambda item: item[1], reverse=True)}
        sorted_times = {k: v for k, v in sorted(time_counts.items(), key=lambda item: item[1], reverse=True)}

        return {
            'locations': sorted_locations,
            'times': sorted_times
        }

    @staticmethod
    def winner(event_votes: dict) -> tuple:
        locations = event_votes.get('locations', {})
        times = event_votes.get('times', {})

        winning_location = max(locations, key=locations.get, default=None)
        winning_time = max(times, key=times.get, default=None)
        return (winning_time, winning_location)
    
class events:

    @staticmethod
    def exists(event_id: str) -> bool:
        return tables.query("SELECT 1 FROM events WHERE uuid = ?", (event_id,), "one") != ()

    @staticmethod
    def create(event_id: str, organizer_email: str, organizer_loc: str, date: str, deadline: str, budget: str, timezone:str, times: list, locations: list, votes: dict) -> bool:

        if events.exists(event_id): return False

        location_str = dict_to_str(organizer_loc)
        times_str = list_to_str(times)
        locations_str = list_to_str(locations)
        votes_str = dict_to_str(votes)

        result = tables.query("INSERT INTO events (uuid, organizer, organizer_loc, date, deadline, budget, timezone, times, locations, votes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                (event_id, organizer_email, location_str, date, deadline, budget, timezone, times_str, locations_str, votes_str))
        
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
            if result and result[0]:
                deadline_str = result[0][0]
                try:
                    # Attempt to parse the deadline string into a datetime object
                    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                except ValueError:
                    # If parsing fails, the string is not in the correct date format
                    return False

                # Compare the parsed deadline date to the current date
                current_date = datetime.now().date()
                return deadline_date >= current_date and deadline_str not in ["COMPLETED", "CANCELLED"]
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
        def organizer_email(event_id: str) -> str:
            result = tables.query("SELECT organizer FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

        @staticmethod
        def organizer_loc(event_id: str) -> str:
            result = tables.query("SELECT organizer_loc FROM events WHERE uuid = ?", (event_id,), "one")
            return result[0][0] if result else None

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
