import schmail as eml
import events_database as edb
import datetime
import os

REQUEST_LINK = "google.com"
VOTING_LINK = "youtube.com"

def print_dict(event:dict):
    ret = ""
    ret += f"\n\t'uuid': '{event['uuid']}' ({type(event['uuid'])}),"
    ret += f"\n\t'date': '{event['date']}' ({type(event['date'])}),"
    ret += "\n\t'times': [\n"
    for s in event['times']:
        ret += f"\t\t'{s}' ({type(s)}),\n"
    ret += "\t]"
    ret += "\n\t'locations': [\n"
    for s in event['locations']:
        ret += f"\t\t'{s}' ({type(s)}),\n"
    ret += "\t]"
    ret += f"\n\t'budget': '{event['budget']}' ({type(event['budget'])}),"
    ret += f"\n\t'sender': '{event['sender']}' ({type(event['sender'])}),"
    ret += "\n\t'recipients': [\n"
    for s in event['recipients']:
        ret += f"\t\t'{s}' ({type(s)}),\n"
    ret += "\t]"
    #ret += "\n\t'votes': {\n"
    #for s in event['votes'].keys():
    #    ret += f"\t\t{s}: {event['votes'][s]} ({type(event['votes'][s])}),\n"
    #ret += "\n\t}"
    
    print('{\n' + ret + '\n}')

def add_vote(votedStatus, uuid, voting_id, selected_location, selected_time):
    return {
        "votedStatus": votedStatus,
        "uuid": uuid,
        "voting_id": voting_id,
        "selected_location": selected_location,
        "selected_time": selected_time
    }

def get_test_event(uuid="", date="", times=[], locations=[], budget=400, sender="", recipients=[], votes={}):
    
    if date == "": date = str(datetime.date.today())
    if times == []: times = ["12:00 PM - 01:00 PM", "03:00 PM - 04:00 PM", "11:13 AM - 03:35 PM"]
    if locations == []: locations = ["KuKo","Subway","McDonalds"]
    if sender == "": sender = "dnnbaq@gmail.com"
    if recipients == []: recipients = ["dnnbaq@gmail.com"]
    if votes == {}:
        v1 = edb.generate_UUID()
        votes[v1] = add_vote(True, uuid, v1, locations[1], times[2])
        v2 = edb.generate_UUID()
        votes[v2] = add_vote(True, uuid, v2, locations[1], times[2])
        v3 = edb.generate_UUID()
        votes[v3] = add_vote(True, uuid, v3, locations[1], times[2])
        v4 = edb.generate_UUID()
        votes[v4] = add_vote(True, uuid, v4, locations[0], times[1])
    
    event = {}
    event['uuid'] = uuid
    event['date'] = date
    event['times'] = times
    event['locations'] = locations
    event['budget'] = budget
    event['sender'] = sender
    event['recipients'] = recipients
    event['votes'] = votes

    return event

uuid2 = "99084584-4466-4f46-bb3b-065a1901f720"
problem_event = edb.event.details.unserialize(uuid2)

test_event = get_test_event()
uuid = edb.generate_UUID()
test_event['uuid'] = uuid
edb.event.details.serialize(test_event)

print("\n\n\n")
print_dict(test_event)
print("\n\n\n")
print_dict(edb.event.details.unserialize(uuid2))
print("\n\n\n")

"""
uuid = "fdc9a78b-35c9-46e6-90b3-d5cebb3cf861"
test_event = edb.event.details.unserialize(uuid)

print("{")
for k in test_event.keys():
    if(type({}) == type(test_event[k])):
        print(f"\t{k} :: "+'{')
        for s in test_event[k].keys():
            print(f"\t\t{s} : {test_event[k][s]}")
        print("\t}")
        continue
    print(f"\t{k} :: {test_event[k]}")
print("}")
"""

test_1 = True
while(test_1):
    inp = input("Run 'send.invite()' test? (Y/N): ")
    inp = inp.lower()
    if(inp == 'y' or inp == 'n'):
        if inp == 'y':
            eml.send.invite(uuid, VOTING_LINK, True)
            eml.send.invite(uuid2, VOTING_LINK, True)
        test_1 = False
    else:
        continue

test_2 = True
while(test_2):
    inp = input("Run 'send.request()' test? (Y/N): ")
    inp = inp.lower()
    if(inp == 'y' or inp == 'n'):
        if inp == 'y':
            eml.send.request(uuid, REQUEST_LINK, True)
            eml.send.invite(uuid2, VOTING_LINK, True)
        test_2 = False
    else:
        continue

test_3 = True
while(test_3):
    inp = input("Run 'send.approve()' test? (Y/N): ")
    inp = inp.lower()
    if(inp == 'y' or inp == 'n'):
        if inp == 'y':
            eml.send.approve(uuid, True)
            eml.send.invite(uuid2, VOTING_LINK, True)
        test_3 = False
    else:
        continue

"""
file_path = edb.PATH_FILE_EVENT(uuid)
if os.path.exists(file_path):
    os.remove(file_path)
"""


