# ProjectSchmooze
### Platform for coordinating entertainment reservations between users and clients


## Installation

Open a terminal and run:

```bash
$ git clone https://github.com/nid666/ProjectSchmooze.git
$ pip3 install requirements.txt
$ streamlit run schmooze.py
```

This will open a new tab in your default browser with the webapp running.

## Phase 1 ToDo:
- [x] Allow to select/input/choose restaurants
- [x] Budget constraints per person 
- [x] Select Entertainment Options 
- [x] Voting System in email link 
- [x] Send out emails with voting links
- [x] Check voting status through cookies and allow for recasting of votes
- [x] Setup database system to keep track of a uuid's voting status/results

## Phase 2 ToDo:
- [x] login page for the user (Sid)
- [x] Notify user if all clients have voted to finalize the reservation (Dean)
- [x] Notify clients of confirmed reservation (Dean)
- [x] Do calendar invites in email (Dean)
- [x] Fix any bugs in email system (Dean)
- [x] Allow for multi email selection (Sid)

## Phase 3 ToDo
- [x] Hosted Publically with full userflow 
- [x] Fix any bugs and optimize voting page
- [x] Double check API progress

## Phase 4 ToDo
- [ ] Fix bug when hosted
- [ ] Deadline to cast vote
- [ ] Reminder email one day before vote deadline 
- [ ] Show final result
- [ ] Add sender name (sid)
- [ ] add sender company and location (sid)
- [ ] change time to be custom string input (sid)
- [ ] add comment section
- [ ] verify if email section is blank before allowing sending of emails (sid)
- [ ] automatically clear email input once an email is entered (sid)
- [ ] add in forgot password and create account screens (sid)
- [ ] fix bugs


## Phase 5 ToDo (Post API)
- Distance radius (tentative)
- Radius to search for entertainment options/restaurants
- Automatic selection of locations based upon budgets
- [ ] Setup api to allow automatic booking once a vote is finalized
- [ ] check if a restaunt is avaliable at a given time
- [ ] Better data capturing for logged in users
