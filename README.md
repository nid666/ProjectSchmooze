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
- [ ] Hosted Publically with full userflow *
- [ ] Better data capturing for logged in users
- [x] Fix any bugs and optimize voting page
- [x] Double check API progress
- [ ] Show final result (Sid)

## Phase 4 ToDo (Post API)
- Distance radius (tentative)
- Radius to search for entertainment options/restaurants
- Automatic selection of locations based upon budgets
- [ ] Setup api to allow automatic booking once a vote is finalized
- [ ] check if a restaunt is avaliable at a given time

