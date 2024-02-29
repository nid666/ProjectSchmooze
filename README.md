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
- [x] Deadline to cast vote (dean)
- [x] Reminder email one day before vote deadline (dean)
- [x] Convert pkl to SQLite database (dean)
- [x] Replace pkl calls with SQLite in front-end (dean)
- [x] Unique links for each voter (dean)
- [x] Improved email formatting for closeness to client (dean)
- [x] Add sender name (sid)
- [x] add sender company and get location (sid)
- [x] change time to be custom string input (sid)
- [x] add comment section (Sid)
- [x] verify if email section is blank before allowing sending of emails (sid)
- [x] add in forgot password and create account screens (sid)
- [x] Fix bug when hosted (dean)
- [x] Test deadline (dean)
- [x] Show final result (dean)
- [x] SQLite email formatting bugs (dean)
- [x] fix bugs (dean)
- [x] Allow for times such as "1PM" to be entered into the time input

## Phase 4 ToDo (Post API)
- Distance radius (tentative)
- Radius to search for entertainment options/restaurants
- Automatic selection of locations based upon budgets/AI reccomendations
- [ ] Setup api to allow automatic booking once a vote is finalized
- [ ] check if a restaunt is avaliable at a given time
- [ ] Better data capturing for logged in users
- [ ] Send forgotten password info in an email to user
- [ ] Add reset password screen
- [ ] Add AI integration to reccomendations
- [ ] allow removal of incorrectly entered time slots
- [ ] create and add logo to main pages
- [ ] automatically clear email input once an email is entered (sid)
- [ ] Fix copy and paste issues that occur from refreshing
- [ ] Allow users to see votes to break ties
- [ ] Rewrite front end with react + tailwind
## Phase 5
- [ ] Create webscraping for opentable
- [ ] create webscraping based api
- [ ] Integrate automatic time checking with opentable to ensure the place isn't booked
- [ ] Get user's phone number for open table reservation
- [ ] Organizer shouldn't cast vote --> confirmation email for organizer
- [ ] Combine reservation row and time rows into multiple rows of format '3/1 8pm' --> string detection
- [ ] Create account, login issue
- [ ] Delete Tommy's account so he can make one himself
- [ ] Show time+date input, email inputs.
- [ ] Beautify 'add locations' section to add row below existing rows and above 'Add Location' button with (-) removal option WITHIN the row
- [ ] Approval page formatting
- [ ] API plan
- [ ] User flow to introduce first time user
- [ ] Get selected time. Let organizer choose booking time from '30m before - 30m after'

