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
    menu_icon="cast", default_index=2, orientation="horizontal")

if loginOptionMenu == "Create Account":
    st.switch_page("pages/createAccount.py")
elif loginOptionMenu == "Login":
    st.switch_page("schmooze.py")