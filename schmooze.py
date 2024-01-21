import datetime
import streamlit as st

# Title
st.title('Reservation System')

# Select a date using streamlit date input
selected_date = st.date_input("Input Reservation Date", datetime.date.today())

# Defining the time slots im selecting between
time_slots = ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM", 
              "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", 
              "03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"]

# Select up to 3 time slots
selected_time_slots = st.multiselect("Choose up to 3 time slots", time_slots)

# Limit the selection to 3
if len(selected_time_slots) > 3:
    st.error('You can only choose up to 3 time slots.')
    selected_time_slots = selected_time_slots[:3]

# Display the chosen date and time slots, this would need to go 
# into whatever database or whatever we are using
if st.button('Confirm Reservation'):
    st.write(f'Reservation Date: {selected_date}')
    for i, time_slot in enumerate(selected_time_slots, start=1):
        st.write(f'Time Slot {i}: {time_slot}')
