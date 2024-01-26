# ProjectSchmooze
### Platform for coordinating entertainment reservations between users and clients


## Installation

Open a terminal and run:

```bash
$ pip3 install streamlit
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
- [ ] login page for the user
- [ ] check if a restaunt is avaliable at a given time
- [ ] Notify user if all clients have voted to finalize the reservation
- [ ] Notify clients of confirmed reservation
- [ ] Host it publically for demos
- [ ] Do calendar invites in email
- [ ] Setup api to allow automatic booking once a vote is finalized
- [ ] Show final result
- [ ] Fix any bugs in email system
- [ ] Fix any bugs in voting page


## Phase 3 ToDo
- Distance radius (tentative)
- Radius to search for entertainment options/restaurants
- Automatic selection of locations based upon budgets
