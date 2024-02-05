import datetime
import time
import streamlit as st
import re
import schmail as notify
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import events_database as edb
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.markdown("<style> ul {display: none;} </style>", unsafe_allow_html=True)
#checks if the email given to it is valid or not, returns a boolean
def is_valid_email(email):

    # Define the regular expression for a valid email
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    
    # Use the fullmatch method from the re module to check if the email matches the pattern
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def mainPage():
    

    with st.sidebar:
        authenticator = st.session_state['authObject']
        authenticator.logout()

    
    # Title so that it can be centered
    st.markdown("<h1 style='text-align: center;'>Project Schmooze</h1>", unsafe_allow_html=True)

    # Select a date using streamlit date input
    
    st.subheader("Select Reservation Date")
    selected_date = st.date_input(label="Select Reservation Date", value = datetime.date.today(), label_visibility="hidden")
    # Defining the time slots im selecting between, this can be changed to the time picker if we want any time to be selectable
    time_slots = ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM", 
                "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", 
                "03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"]

    # Select up to 3 time slots
    selected_time_slots = st.multiselect("You may choose up to 3 time slots", time_slots)




    # Limit the selection to 3
    if len(selected_time_slots) > 3:
        st.error('You can only choose up to 3 time slots.')
        selected_time_slots = selected_time_slots[:3]

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
    st.divider()






    # Display the chosen date and time slots, this would need to go 
    # into whatever database or whatever we are using
    if st.button('Confirm Reservation', use_container_width=True, type = "primary"):
        
        if (len(selected_time_slots) == 0):
            st.error("You must select at least one time slot")
        #elif is_valid_email(email) == False:
            #st.error("You must enter a valid email address")
        else:
            uuid = edb.generate_UUID()

            #location_images = ["placeholder_link.com" for _ in range(len(st.session_state.get(locations)))]
            #locations_dict = {key: value for key, value in zip(st.session_state.get(locations), location_images)}
            
            event = {}
            event['uuid'] = uuid
            event['date'] = selected_date
            event['times'] = selected_time_slots
            event['locations'] = st.session_state['locations']
            event['budget'] = budget
            event['sender'] = "TEMPORARY_VALUE" # needs organizer's email address
            event['recipients'] = st.session_state['emails']
            event['votes'] = {}

            edb.event.details.serialize(event)
            
            st.write(event)
            

            st.toast("Invite sent successfully!")

            notify.send.invite(uuid, "google.com", True) # temporary placeholder link for the voting page


if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
    #st.write(st.session_state)
    mainPage()
else:
    st.error("Error: invalid login")
    st.switch_page("schmooze.py")
            