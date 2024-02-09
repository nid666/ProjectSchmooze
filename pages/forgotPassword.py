import datetime
import time
import streamlit as st
import re
import json
from streamlit_extras.stateful_button import button 
import extra_streamlit_components as stx
import streamlit_authenticator as stauth
import yaml
from streamlit_option_menu import option_menu
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

#Makes sure that the auth object exists by forcing them to go to main page first
if st.session_state == {}:
    st.switch_page("schmooze.py")


loginOptionMenu = option_menu(None, ["Login", "Create Account", "Forgot Password"], 
    icons=['box-arrow-in-right', 'person-plus-fill', "patch-question-fill"], 
    menu_icon="cast", default_index=2, orientation="horizontal")

if loginOptionMenu == "Create Account":
    st.switch_page("pages/createAccount.py")
elif loginOptionMenu == "Login":
    st.switch_page("schmooze.py")



authenticator = st.session_state['authObject']


def getLoginConfig():
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

config = getLoginConfig()

try:

    #TODO These 3 below variables need to be emailed to user
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()


    if username_of_forgotten_password:
        st.success('New password to be sent securely')
        # The developer should securely transfer the new password to the user.

        config['credentials'] = authenticator.credentials

        with open('pages/config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    elif username_of_forgotten_password == False:
        st.error('Username not found')
except Exception as e:
    st.error(e)

st.header("WIP")