import datetime
import streamlit as st
import re
import schmail as notify
import json
import uuid
import pickle
import os

PKL_PATH_DIR = "events"

def generate_UUID() -> str:
    # Generate a unique UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def PKL_PATH_FILE(uuid:str) -> str:
    return os.path.join(PKL_PATH_DIR, f"{uuid}.pkl")

def serialize_event(event_dict: dict) -> None:
    file_path = PKL_PATH_FILE(event_dict["uuid"])
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(event_dict, file)
        #print(f"Dictionary successfully serialized to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def unserialize_events() -> dict:
    aggregated_dict = {}
    try:
        # Iterate over all files in the directory
        for filename in os.listdir(PKL_PATH_DIR):
            if filename.endswith('.pkl'):
                file_path = os.path.join(PKL_PATH_DIR, filename)
                with open(file_path, 'rb') as file:
                    # Deserialize the contents of the pickle file
                    data = pickle.load(file)
                    # Use the filename without extension as the key
                    key = os.path.splitext(filename)[0]
                    aggregated_dict[key] = data
        return aggregated_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


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

    #TODO - Add option to select more than one location

    st.subheader("Enter the locations you would like to reserve")
    firstLocation = st.text_input(label = "firstLocation", placeholder="Input your first location here", label_visibility="hidden")
    secondLocation = st.text_input(label = "secondLocation", placeholder="Input your second location here", label_visibility="hidden")
    thirdLocation = st.text_input(label = "thirdLocation", placeholder="Input your third location here", label_visibility="hidden")
    locations = [firstLocation, secondLocation, thirdLocation]

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
            uuid = generate_UUID()

            location_images = ["placeholder_link.com" for _ in range(len(locations))]
            locations_dict = {key: value for key, value in zip(locations, location_images)}
            
            event = {"uuid":uuid,
                     "date":selected_date,
                     "times":selected_time_slots,
                     "locations":locations_dict,
                     "budget":budget,
                     "email": emails}
            
            serialize_event(event)
            notify.send_email(SENDER=email, DATE=selected_date, RECIPIENTS=emails, BCC=False, locations=locations_dict, times=selected_time_slots)
            

def renderVotingPage():
    st.title("Voting Page")
    st.subheader("Cast Your Vote")

    st.subheader("Select Reservation Time")

    st.subheader("Select Option")
    st.selectbox("Option 1", ["Option 1", "Option 2", "Option 3"])

def main():
    if st.query_params.get("uuid") == None:
        mainPage()
    else:
        renderVotingPage()
main()
