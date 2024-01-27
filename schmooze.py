import datetime
import streamlit as st
import re
import schmail as notify
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import events_database as edb


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




    #TODO - Add option to select more than one location

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
    st.subheader("Enter the email address of the primary person you would like to invite")
    email = st.text_input(label = "email", placeholder="Input your email here", label_visibility="hidden")
    # CHANGE 'email' VARIABLE TO BE LIST
    emails = [email] #TEMPORARY HANDLING OF MULTIPLE RECIPIENTS
    st.divider()






    # Display the chosen date and time slots, this would need to go 
    # into whatever database or whatever we are using
    if st.button('Confirm Reservation', use_container_width=True, type = "primary"):
        
        if (len(selected_time_slots) == 0):
            st.error("You must select at least one time slot")
        elif is_valid_email(email) == False:
            st.error("You must enter a valid email address")
        else:
            uuid = edb.generate_UUID()

            #location_images = ["placeholder_link.com" for _ in range(len(st.session_state.get(locations)))]
            #locations_dict = {key: value for key, value in zip(st.session_state.get(locations), location_images)}
            
            event = {"uuid":uuid,
                     "date":selected_date,
                     "times":selected_time_slots,
                     "locations":st.session_state['locations'],
                     "budget":budget,
                     "sender": "TEMPORARY_VALUE",
                     "email": emails}
            st.write(event)
            edb.serialize_event(event)

            st.toast("Invite sent successfully!")

            #notify.send_email(SENDER=email, DATE=selected_date, RECIPIENTS=emails, BCC=False, locations=locations_dict, times=selected_time_slots)
            
#might need to include st.cache_data() here if there are performance issues
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

def renderRevotePage():
    # Check for existing cookies
    has_voted = cookie_manager.get("voted")



    # Location Voting
    loc_cols = st.columns(len(locations))
    for c, l in zip(loc_cols, locations):
        with c:
            st.header(l)
            if current_location == l:
                st.write("Previously Selected")
                location_selected = True
            elif st.button(label="Vote for " + l, key=f"vote_{l}"):
                location_selected = True
                cookie_manager.set("current_location", l)

    # Time Selection
    tim_cols = st.columns(len(times))
    for t, time in zip(tim_cols, times):
        with t:
            st.header(time)
            if current_time == time:
                st.write("Previously Selected")
                time_selected = True
            elif st.button(label="Select time " + time, key=f"select_{time}"):
                time_selected = True
                cookie_manager.set("current_time", time)

                
    st.write('voted')

def renderVotingPage():
    uuid = st.query_params.get("uuid")
    event_dict = edb.unserialize_event(uuid)

    st.markdown("<h1 style='text-align: center;'>Voting Page</h1>", unsafe_allow_html=True)

    st.subheader("Cast Your Vote")

    #checking if the cookies exist
    cookies = cookie_manager.get("results")
    if cookies == None:
        vote_result = {
                "votedStatus": False,
                "uuid": uuid,
                "selected_location": None,
                "selected_time": None
            }
        cookie_manager.set("results", vote_result)
    cookies = cookie_manager.get_all()

    results = cookies['results']

    # CHANGE THE COOKIES

    cookie_manager.set('results', results)


    #Checking to see if they voted to render the correct page
    if results['votedStatus'] == True:
        renderRevotePage()
        
    else:
        st.write(cookies)
        # Initialize session state variables
        if 'selected_location' not in st.session_state:
            st.session_state['selected_location'] = None

        if 'selected_time' not in st.session_state:
            st.session_state['selected_time'] = None

        locations = event_dict["locations"]
        loc_cols = st.columns(len(locations))

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

        for t, l in zip(tim_cols, times):
            with t:
                st.header(l)
                if st.button(label= "Select", key=f"select_{l}"):
                    st.session_state['selected_time'] = l
                    st.write(f"Time {l} Selected")

        st.divider()

        if st.button(label = "Cast Final Vote", key="cast_final_vote", type="primary", use_container_width=True):
            # Capture the votes and uuid in a dictionary
            vote_result = {
                "votedStatus": True,
                "uuid": uuid,
                "selected_location": st.session_state['selected_location'],
                "selected_time": st.session_state['selected_time']
            }
            cookie_manager.set("results", vote_result)
            # Convert the dictionary to a JSON object
            vote_json = json.dumps(vote_result)


            
            # You can display the JSON, write it to a file, or send it somewhere
            st.json(vote_json)


        

def main():
    if st.query_params.get("uuid") == None:
        mainPage()
    else:
        renderVotingPage()
main()
