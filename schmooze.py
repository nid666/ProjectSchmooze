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

# Ignore this, it is just page setup boilerplate
st.set_page_config(
    page_title="Project Schmooze",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#Sign in system:import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login()



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
            
#might need to include st.cache_data() here if there are performance issues
cookie_manager = stx.CookieManager(key = "cookieManagerKey")

def renderRevotePage():
    # Check for existing cookies
    cookies = cookie_manager.get("results")

    uuid = st.query_params.get("uuid")
    event_dict = edb.event.details.unserialize(uuid)
    if event_dict == None:
        st.error("Invalid UUID")
        return
    
    # getting the time and location values
    locations = event_dict["locations"]
    times = event_dict["times"]

    st.subheader("Change your vote: ")
    # Location Voting
    loc_cols = st.columns(len(locations))
    for c, l in zip(loc_cols, locations):
            with c:
                st.header(l)
                if st.button(label = "Select location " + l, key=f"vote_{l}"):
                    st.session_state['selected_location'] = l
                    st.write(f"Location {l} Selected")
    # Time Selection
    tim_cols = st.columns(len(times))

    for t, l in zip(tim_cols, times):
            with t:
                st.header(l)
                if st.button(label= "Select", key=f"select_{l}"):
                    st.session_state['selected_time'] = l
                    st.write(f"Time {l} Selected")
                
    

    if st.button(label = "Cast Final Vote", key="cast_final_vote", type="primary", use_container_width=True):

            # Initialize session state variables for location
            if 'selected_location' not in st.session_state:
                st.session_state['selected_location'] = None
            # Initialize session state variables for time
            if 'selected_time' not in st.session_state:
                st.session_state['selected_time'] = None
            
            if cookies['selected_location'] == st.session_state['selected_location'] and cookies['selected_time'] == st.session_state['selected_time']:
                st.error("You have already voted for this location and time")
                return
            # Capture the votes and uuid in a dictionary
            else:

                voting_id = cookie_manager.get("results")['voting_id']

                vote_result = {
                    "votedStatus": True,
                    "uuid": uuid,
                    "voting_id": voting_id,
                    "selected_location": st.session_state['selected_location'],
                    "selected_time": st.session_state['selected_time']
                }
                cookie_manager.set("results", vote_result)

                edb.event.voting.vote(uuid, vote_result)

    st.write('voted')

def renderVotingPage():
    
    uuid = st.query_params.get("uuid")

    event_dict = edb.event.details.unserialize(uuid)
    if event_dict == None:
        st.error("Invalid UUID")
        return
    

    st.markdown("<h1 style='text-align: center;'>Voting Page</h1>", unsafe_allow_html=True)

    #checking if the cookies exist
    cookies = cookie_manager.get("results")
    with st.spinner("Loading Page..."):
        time.sleep(1)

    voting_id = edb.generate_UUID()
    st.write(voting_id)
    # If the cookies do not exist, create temp cookies
    if cookies == None:
        vote_result = {
                "votedStatus": False,
                "voting_id": voting_id,
                "uuid": uuid,
                "selected_location": None,
                "selected_time": None
            }
        cookie_manager.set("results", vote_result)
    
    st.write(cookies)
    # CHANGE THE COOKIES
    
    if cookies == None:
        with st.spinner("Loading Data..."):
            time.sleep(1)
    #Checking to see if they voted to render the correct page
    if cookies['votedStatus'] == True:
        renderRevotePage()
        
    else:

        st.subheader("Cast Your Vote")
        # Initialize session state variables for location
        if 'selected_location' not in st.session_state:
            st.session_state['selected_location'] = None
        # Initialize session state variables for time
        if 'selected_time' not in st.session_state:
            st.session_state['selected_time'] = None


        locations = event_dict["locations"]
        loc_cols = st.columns(len(locations))

        #Generates the buttons for locations, with c being the columns and l being the location
        for c, l in zip(loc_cols, locations):
            with c:
                st.header(l)
                if st.button(label = "Select location " + l, key=f"vote_{l}"):
                    st.session_state['selected_location'] = l
                    st.write(f"Location {l} Selected")

        st.divider()

        st.subheader("Select Reservation Time")

        times = event_dict["times"]
        tim_cols = st.columns(len(times))

        # Generates the buttons for times, with t being the columns and l being the time
        for t, l in zip(tim_cols, times):
            with t:
                st.header(l)
                if st.button(label= "Select", key=f"select_{l}"):
                    st.session_state['selected_time'] = l
                    st.write(f"Time {l} Selected")

        st.divider()

        # Renders the final voting button to cast the final vote
        if st.button(label = "Cast Final Vote", key="cast_final_vote", type="primary", use_container_width=True):

            #results_cookie = cookie_manager.get("results")
            #results_dict = json.loads(results_cookie)
            #voting_id = results_dict['voting_id']
            #voting_id = results_cookie['voting_id']

            # Capture the votes and uuid in a dictionary
            vote_result = {
                "votedStatus": True,
                "voting_id": voting_id,
                "uuid": uuid,
                "selected_location": st.session_state['selected_location'],
                "selected_time": st.session_state['selected_time']
            }
            #sets the cookie to the new value
            cookie_manager.set("results", vote_result)




            # Convert the dictionary to a JSON object
            vote_json = json.dumps(vote_result)

            
            # You can display the JSON, write it to a file, or send it somewhere
            st.json(vote_json)

            # DATABASE: saved to pickle
            edb.event.voting.vote(uuid, vote_result)

        

def main():
    if st.query_params.get("uuid") == None:
        
        #Handles logging on
        if st.session_state["authentication_status"]:
            with st.spinner("Loading Page..."):
                #This sleep is here to prevent widgets from rendering out of order due to rendering quicker than others
                time.sleep(1)
                authenticator.logout()
                #If logged in successfully, render the main page
                mainPage()
        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
    else:
        renderVotingPage()
main()
