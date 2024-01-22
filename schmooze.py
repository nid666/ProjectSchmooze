import datetime
import streamlit as st

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

# Title so that it can be centered
st.markdown("<h1 style='text-align: center;'>Project Schmooze</h1>", unsafe_allow_html=True)

# Select a date using streamlit date input
st.subheader("Select Reservation Date")
selected_date = st.date_input("Select Reservation Date", datetime.date.today(), label_visibility="hidden")

# Defining the time slots im selecting between, this can be changed to the time picker if we want any time to be selectable
time_slots = ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM", 
              "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", 
              "03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"]


st.subheader("Select Reservation Date")
# Select up to 3 time slots
selected_time_slots = st.multiselect("You may choose up to 3 time slots", time_slots)

# Limit the selection to 3
if len(selected_time_slots) > 3:
    st.error('You can only choose up to 3 time slots.')
    selected_time_slots = selected_time_slots[:3]

st.divider()
# Allowing to choose the places you want to go
st.subheader("Please enter the locations you would like to reserve")
firstLocation = st.text_input(label = "firstLocation", placeholder="Input your first location here", label_visibility="hidden")
secondLocation = st.text_input(label = "secondLocation", placeholder="Input your second location here", label_visibility="hidden")
thirdLocation = st.text_input(label = "thirdLocation", placeholder="Input your third location here", label_visibility="hidden")
locations = [firstLocation, secondLocation, thirdLocation]

st.subheader("Please enter a budget per person")
budget = st.number_input(label="Enter the budget per person", label_visibility="hidden")
st.divider()






# Display the chosen date and time slots, this would need to go 
# into whatever database or whatever we are using
if st.button('Confirm Reservation'):
    
    if (len(selected_time_slots) == 0):
        st.error("You must select at least one time slot")
    else:
        st.write("Reservation Date: ", selected_date)
        st.write("Time Slots: ", selected_time_slots)
        st.write("Locations: ", locations)
        st.write("Budget: ", budget)
        st.toast("Your invitations have been sent out!")
