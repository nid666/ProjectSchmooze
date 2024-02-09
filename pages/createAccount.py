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
    menu_icon="cast", default_index=1, orientation="horizontal")

if loginOptionMenu == "Login":
    st.switch_page("schmooze.py")
elif loginOptionMenu == "Forgot Password":
    st.switch_page("pages/forgotPassword.py")

def getLoginConfig():
    with open('../config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

#This is the creating account widget:
    
         
authenticator = st.session_state['authObject']
try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(preauthorization=False)

    with open('../config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    if email_of_registered_user:
        st.toast('User Registered Successfully')
    
except Exception as e:
    print(e)
    st.error(e)