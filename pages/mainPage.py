import datetime
import time
import streamlit as st
import re
import _mail as notify
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import database as db
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit_js_eval as js
import uuid

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

def generate_uuid():
    return uuid.uuid4()


def is_valid_12_hour_format(time_str):
    # Adjust regex to allow a single digit for hours less than 10
    if re.match(r'^(0?[1-9]|1[0-2]):([0-5][0-9])$', time_str):
        return True
    else:
        return False


def get_logged_in_user_email():
    # Check if the user is authenticated and the authenticator object exists in the session state
    if 'authObject' in st.session_state:
        # Retrieve the authenticator object
        authenticator = st.session_state['authObject']
        
        # Get the username of the currently logged-in user
        username = authenticator.username
        
        # Retrieve user details from the authenticator object
        user_details = authenticator.credentials['usernames'].get(username, {})
        
        # Extract the email address from user details
        user_email = user_details.get('email', 'Email not found')
        
        return user_email
    else:
        # Return None or an appropriate message if the user is not logged in or if the authenticator object is not found
        return None



#checks if the email given to it is valid or not, returns a boolean
def is_valid_email(email):

    # Define the regular expression for a valid email
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    
    # Use the fullmatch method from the re module to check if the email matches the pattern
    if re.fullmatch(regex, email):
        return True
    else:
        return False
    
def convert_to_24_hour_format(time_str, am_pm):
    # Split the time string into hours and minutes
    hours, minutes = map(int, time_str.split(':'))
    am_pm = am_pm.upper()

    # Convert hours in case of PM
    if am_pm == "PM" and hours < 12:
        hours += 12
    elif am_pm == "AM" and hours == 12:
        # Convert 12 AM to 00 hours
        hours = 0

    # Format the hours and minutes to ensure two digits
    time_24_hour_format = "{:02d}:{:02d}".format(hours, minutes)
    return time_24_hour_format



def mainPage():
    
    
    cols = st.columns([0.85, 0.15])
    with cols[1]:
        authenticator = st.session_state['authObject']
        authenticator.logout()

    location = js.get_geolocation()

    # Title so that it can be centered
    st.markdown("<h1 style='text-align: center;'>Project Schmooze</h1>", unsafe_allow_html=True)

    # Select a date using streamlit date input
    st.subheader("Enter Company Name")
    company = st.text_input(label="companyNameEntry", label_visibility="hidden")
    st.subheader("Select Reservation Date")
    selected_date = st.date_input(label="Select Reservation Date", value = datetime.date.today(), label_visibility="hidden")

    st.subheader("Select Deadline for Voting")
    deadline = st.date_input(label="Select Deadline Date", value = datetime.date.today(), label_visibility="hidden")


    if 'current_time' not in st.session_state:
        st.session_state.current_time = ""

    if 'times' not in st.session_state:
        st.session_state.times = []

    col1_start, col2_start = st.columns([0.8, 0.2])

    # Start Time Selection
    with col2_start:
        amOrPm_start = st.selectbox("AM or PM", options=['AM', 'PM'], key='amOrPm_start', label_visibility="hidden")

    with col1_start:
        inputTime_start = st.text_input("Enter the start time", key="time_input_start")

    col1_end, col2_end = st.columns([0.8, 0.2])

    # End Time Selection
    with col2_end:
        amOrPm_end = st.selectbox("AM or PM", options=['AM', 'PM'], key='amOrPm_end', label_visibility="hidden")

    with col1_end:
        inputTime_end = st.text_input("Enter the end time", key="time_input_end")

    if st.button('Add Time'):
        # Validate and add start time
        if is_valid_12_hour_format(inputTime_start) and is_valid_12_hour_format(inputTime_end) and len(st.session_state.times) < 3:
            start_time_24 = convert_to_24_hour_format(inputTime_start, amOrPm_start)
            end_time_24 = convert_to_24_hour_format(inputTime_end, amOrPm_end)
            time_slot = (start_time_24, end_time_24)
            
            if time_slot in st.session_state.times:
                st.toast('Time slot already added')
            else:
                st.session_state.times.append(time_slot)
                st.toast("Time slot Added!")
        elif len(st.session_state.times) == 3:
            st.toast("Max time slots reached")
        else:
            st.error('Please enter valid times.')

    st.divider()
    # Allowing to choose the places you want to go

    #This creates a stateful locations array that we can use to store the locations dynamically
    if 'locations' not in st.session_state:
        st.session_state['locations'] = [0, 0 ,0]

    if 'emails' not in st.session_state:
        st.session_state['emails'] = []

    # Initialize an empty string to store the current email input
    if 'current_email' not in st.session_state:
        st.session_state.current_email = ""


    st.subheader("Enter the locations you would like to reserve")
    firstLocation = st.text_input(label="firstLocation", placeholder="Input your first location here", key="firstLocation", label_visibility="hidden")
    secondLocation = st.text_input(label="secondLocation", placeholder="Input your second location here", key="secondLocation", label_visibility="hidden")
    thirdLocation = st.text_input(label="thirdLocation", placeholder="Input your third location here", key="thirdLocation", label_visibility="hidden")

    # Update the first three locations if they are not empty
    if firstLocation:
        st.session_state['locations'][0] = firstLocation
    if secondLocation:
        st.session_state['locations'][1] = secondLocation
    if thirdLocation:
        st.session_state['locations'][2] = thirdLocation

    if button('➕ Add additional locations', type = "primary", key="addLocationToggle"):
        numAdditionalLocations = st.number_input(label = "Enter Number of Additional Locations", value = 1, format = "%d", step = 1, max_value = 10)

        for i in range(numAdditionalLocations):
            additional_location = st.text_input(label="additionalLocation", placeholder="Input your additional location here", key=f"additionalLocation{i}", label_visibility="hidden")
            # Update the session state list with the additional locations
            if additional_location:
                # Ensure unique keys for each location
                while len(st.session_state['locations']) <= i + 3:
                    st.session_state['locations'].append('')
                st.session_state['locations'][i + 3] = additional_location
            

    st.subheader("Enter a budget per person")
    budget = st.number_input(label="Enter the budget per person", label_visibility="hidden")
    st.subheader("Enter the email addresses of the people you would like to invite")

    new_email = st.text_input('Enter email address', value=st.session_state.current_email, key='email_input')

    if st.button('Add Email'):
        if is_valid_email(new_email):
            if new_email in st.session_state.emails:
                st.toast('Email already added')
            else:
                # Add the new email to the list of emails
                st.session_state.emails.append(new_email)
                # Clear the current email input
                st.session_state.current_email = ""
                st.toast("Email Added!")
        else:
            st.error('Please enter a valid email address.')

    # Update the current email input in the state
    st.session_state.current_email = new_email

    st.multiselect('Edit Emails',options=st.session_state.emails, default = st.session_state.emails, key='emails') 

    st.header("Enter a comment for the reservation")
    comment = st.text_area(label = "commentEntry", label_visibility="hidden")
    st.divider()





    # Display the chosen date and time slots, this would need to go 
    # into whatever database or whatever we are using
    if st.button('Confirm Reservation', use_container_width=True, type = "primary"):
        
        if (len(st.session_state.times) == 0):
            st.error("You must select at least one time slot")
        elif len(st.session_state['emails']) == 0:
            st.error("You must enter at least one email to invite")
        else:
            uuid = db.UUID()

            #location_images = ["placeholder_link.com" for _ in range(len(st.session_state.get(locations)))]
            #locations_dict = {key: value for key, value in zip(st.session_state.get(locations), location_images)}

            # Proceed with serialization and emailing

            events = {
                'uuid': str(uuid),
                'date': selected_date.strftime('%Y-%m-%d'),  # Convert to string in YYYY-MM-DD format
                'times': [str(e) for e in st.session_state.times],
                'locations': [str(l) for l in st.session_state['locations']],
                'budget': int(budget),  # Convert to string if necessary
                'sender': str(st.session_state["email"]),
                'recipients': [str(e) for e in st.session_state['emails']],
                'votes': {e: db.UUID() for e in st.session_state['emails']},
                'name' : str(st.session_state['name']),
                'location' : location,   # The users location as a json, it will be null if they didn't accept the location thing
                'company' : company,
                'timezone': 'America/New_York',
                'comment' : comment,
                'deadline': deadline.strftime('%Y-%m-%d') #deadline.strftime('%Y-%m-%d')
            }


            print(events)
            db.events.create(
                event_id=events['uuid'],
                company=events['company'],
                organizer_email=events['sender'],
                organizer_loc=events['location'],
                date=events['date'],
                comment=events['comment'],
                deadline=events['deadline'],
                budget=str(events['budget']),
                timezone=events['timezone'],
                times=events['times'],
                locations=events['locations'],
                votes=events['votes']
            )

            db.votes.cast(uuid,uuid,"","")
            for x in events['votes'].keys():
                val = events['votes'][x]
                db.votes.cast(uuid, val, "", "")
                
            st.write(events)
            
            st.toast("Invite sent successfully!")

            notify.send.invite(uuid, f"http://schmooze.us.to/", True) # temporary placeholder link for the voting page


if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
    #st.write(st.session_state)
    mainPage()
else:
    st.error("Error: invalid login")
    st.switch_page("schmooze.py")
            
