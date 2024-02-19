import datetime
from datetime import datetime
import time
import streamlit as st
import re
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import database as db
import streamlit_authenticator as stauth
import yaml

#might need to include st.cache_data() here if there are performance issues
cookie_manager = stx.CookieManager(key = "cookieManagerKey")

def renderVotingPage():
    
    uuid = st.query_params.get("uuid")
    vid = st.query_params.get('vid')

    if not db.events.exists(uuid):
        st.error("Invalid UUID")
        return
    
    st.markdown("<h1 style='text-align: center;'>Voting Page</h1>", unsafe_allow_html=True)

    #checking if the cookies exist
    cookies = cookie_manager.get("results")
    with st.spinner("Loading Page..."):
        time.sleep(1)

    st.subheader("Cast Your Vote")
    # Initialize session state variables for location
    if 'selected_location' not in st.session_state:
        st.session_state['selected_location'] = None
    # Initialize session state variables for time
    if 'selected_time' not in st.session_state:
        st.session_state['selected_time'] = None

    locations = db.events.get.locations(uuid)
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

    times = db.events.get.times(uuid)
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

        db.votes.cast(uuid,vid,st.session_state['selected_location'],st.session_state['selected_time'])

renderVotingPage()

'''

This is an attempt of optimizing the code
many of the functions in edb will need to be moved into this file

this is an attempt to fix both login issue bug and the uuid = None bug
that happens during deployment



'''



