import streamlit as st
import database as db
import _mail as notify

# Set up the Streamlit page configuration
st.set_page_config(page_title="Approve Page", initial_sidebar_state="collapsed")

# Hide the hamburger menu and footer by injecting custom CSS
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] { display: none; }
        .css-18e3th9 { display: none; }  /* This hides the bottom 'Made with Streamlit' footer */
        /* Additional custom CSS can be added here */
    </style>
    """,
    unsafe_allow_html=True,
)

# Define a function to be called when the "APPROVE" button is clicked
def on_approve_click():
    # Placeholder for the function logic; replace with your actual code
    notify.send.approve(st.query_params.get('uuid'), True)
    

# Main function to render the Streamlit page
def main():
    # Title
    st.markdown("<h1 style='text-align: center;'>Approval Page</h1>", unsafe_allow_html=True)
    
    # Create three columns
    col1, col2, col3 = st.columns([1,2,1])  # The middle column is twice as wide as the side columns

    # Place the button in the middle column
    with col2:
        if st.button("APPROVE"):
            on_approve_click()

if __name__ == "__main__":    
    main()
else:
    st.error("Error: invalid login")
    st.switch_page("schmooze.py")
