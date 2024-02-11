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
from streamlit_option_menu import option_menu

#Sign in system:import yaml
from yaml.loader import SafeLoader

# Ignore this, it is just page setup boilerplate
st.set_page_config(
    page_title="Project Schmooze",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed",
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
st.markdown("<style> ul {display: none;} </style>", unsafe_allow_html=True)


loginOptionMenu = option_menu(None, ["Login", "Create Account", "Forgot Password"], 
    icons=['box-arrow-in-right', 'person-plus-fill', "patch-question-fill"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if loginOptionMenu == "Create Account":
    st.switch_page("pages/createAccount.py")
elif loginOptionMenu == "Forgot Password":
    st.switch_page("pages/forgotPassword.py")

def getLoginConfig():
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

config = getLoginConfig()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login()
if 'authObject' not in st.session_state:
    st.session_state['authObject'] = authenticator







def main():
    if st.query_params.get("uuid") == None:
        #Handles logging on
        if st.session_state["authentication_status"]:
            with st.spinner("Loading Page..."):
                st.session_state["email"] = config["credentials"]["usernames"][st.session_state["username"]]["email"]
                #This sleep is here to prevent widgets from rendering out of order due to rendering quicker than others
                time.sleep(1)
                #If logged in successfully, render the main page
                st.switch_page("pages/mainPage.py")
        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
    else:
        approval_param = st.query_params.get("apr")
        if approval_param == "get":
            st.session_state['uuid'] = st.query_params.get("uuid") #
            organizer = db.events.get.organizer_email(st.query_params.get("uuid"))
            if db.event._is.active(st.query_params.get("uuid")) and (config["credentials"]["usernames"][st.session_state["username"]]["email"] == organizer):
                with st.spinner("Loading Page..."):
                    time.sleep(1)
                    st.switch_page("pages/aprPage.py")
        else:
            st.switch_page("pages/votingPage.py")


main()
