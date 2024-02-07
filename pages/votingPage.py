import datetime
import time
import streamlit as st
import re
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import events_database as edb
import streamlit_authenticator as stauth
import yaml
        




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


def renderVotingPage(allow_revote=False):
    # Retrieve UUID and validate it
    uuid = st.query_params.get("uuid")
    event_dict = edb.event.details.unserialize(uuid)
    if event_dict is None:
        st.error("Invalid UUID")
        return

    # Check for existing cookies
    cookies = cookie_manager.get("results")

    # Initial loading or condition check for revoting
    if cookies is None or (allow_revote and cookies['votedStatus']):
        if cookies is None:
            # Generate a new voting_id for new voters
            voting_id = edb.generate_UUID()
            cookies = {
                "votedStatus": False,
                "voting_id": voting_id,
                "uuid": uuid,
                "selected_location": None,
                "selected_time": None
            }
            # Set initial cookies for new users
            cookie_manager.set("results", cookies)
        elif allow_revote:
            # Load for revoting with existing cookies
            voting_id = cookies['voting_id']
        
        # Common UI elements for voting
        renderVotingUI(event_dict, uuid, voting_id, cookies, allow_revote)
    else:
        st.error("You have already voted. Revoting is not enabled.")





def renderVotingUI(event_dict, uuid, voting_id, cookies, allow_revote):
    # Display Header
    if allow_revote:
        st.subheader("Change your vote:")
    else:
        st.markdown("<h1 style='text-align: center;'>Voting Page</h1>", unsafe_allow_html=True)

    # Voting logic (locations and times) goes here...
    # Similar to the shared parts of the original functions

    # Final Vote Submission
    if st.button("Cast Final Vote"):
        # Check for changes in revote or proceed with initial vote submission
        processFinalVote(cookies, uuid, voting_id)

def processFinalVote(cookies, uuid, voting_id):
    # Process the final vote here, including checks for revoting and setting cookies
    pass

renderVotingPage(allow_revote=True)
