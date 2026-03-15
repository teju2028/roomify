import streamlit as st
import pandas as pd
from streamlit_login_auth_ui.widgets import __login__
import warnings
import json
from bson.objectid import ObjectId

# Import custom modules
from database import MongoDB
from user_management import UserManager
from matching import RoommateMatcher
from notification import send_roommate_request_notification, send_request_status_notification
import utils
import config

# Ignore warnings
warnings.filterwarnings("ignore")

# Initialize MongoDB connection
db = MongoDB()

# Initialize user manager
user_manager = UserManager()

# Initialize roommate matcher
matcher = RoommateMatcher()

# Inject custom CSS
utils.inject_custom_css()

# Initialize login object
loginobj = __login__(
    auth_token=config.AUTH_TOKEN,
    company_name=config.APP_NAME,
    width=200, height=250,
    logout_button_name=config.LOGOUT_BUTTON_NAME,
    hide_menu_bool=False,
    hide_footer_bool=False,
    lottie_url=config.LOTTIE_URL
)

# Build login UI
LOGGED_IN = loginobj.build_login_ui()

if "update_answers_button_clicked" not in st.session_state:    
    st.session_state.update_answers_button_clicked = False

if "update_profile_button_clicked" not in st.session_state:    
    st.session_state.update_profile_button_clicked = False

def update_profile_button_clicked():
    if st.session_state.update_profile_button_clicked:
        st.session_state.update_profile_button_clicked = False
    else:
        st.session_state.update_profile_button_clicked = True

def update_answers_button_clicked():
    if st.session_state.update_answers_button_clicked:
        st.session_state.update_answers_button_clicked = False
    else:
        st.session_state.update_answers_button_clicked = True

if LOGGED_IN:
    # Get user information
    fetched_cookies = loginobj.cookies
    if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
        username = fetched_cookies['__streamlit_login_signup_ui_username__']
        
        # Ensure user exists in MongoDB
        user_manager.save_user_to_mongodb(username)
        
        # Get user data
        user_data = db.get_user(username)
        
        # Display welcome message
        st.markdown(f"<div class='welcome-box'><h2>Welcome to {config.APP_NAME}, {username}! 👋</h2></div>", unsafe_allow_html=True)
        
        # Create sidebar navigation
        st.sidebar.title(config.APP_NAME)
        
        # Display profile setup progress
        progress = utils.user_setup_progress(user_data)
        
        # Navigation options
        nav_options = ["Profile", "Questionnaire", "Find Roommates", "Requests"]
        nav_selection = st.sidebar.radio("Navigation", nav_options)
        
        # Profile page
        if nav_selection == "Profile":
            st.header("Your Profile")
            
            profile_completed = user_data.get("profile_completed", False) if user_data else False
            
            if profile_completed:
                profile_data = user_data.get("profile", {})
                
                st.markdown("<div class='section-header'>Your Profile Information</div>", unsafe_allow_html=True)
                utils.display_profile_summary(profile_data)
                if st.button("Edit Profile", on_click=update_profile_button_clicked) or st.session_state.update_profile_button_clicked:
                    user_manager.create_profile_form(username)
            else:
                user_manager.create_profile_form(username)
        
        # Questionnaire page
        elif nav_selection == "Questionnaire":
            st.header("Roommate Preferences")
            
            # Check if profile is completed first
            profile_completed = user_data.get("profile_completed", False) if user_data else False
            if not profile_completed:
                st.warning("Please complete your profile before filling out the questionnaire.")
            else:
                questionnaire_completed = user_data.get("questionnaire_completed", False) if user_data else False
                
                if questionnaire_completed:
                    st.markdown("<div class='section-header'>Your Answers</div>", unsafe_allow_html=True)
                    
                    answers = user_data.get("questionnaire_answers", [])
                    
                    for i, question in enumerate(config.ROOMMATE_QUESTIONS):
                        if i < len(answers):
                            st.write(f"**{i+1}. {question}**")
                            st.write(answers[i])
                            st.write("---")
                    
                    if st.button("Edit Answers", on_click=update_answers_button_clicked) or st.session_state.update_answers_button_clicked:
                        user_manager.create_questionnaire_form(username)
                else:
                    user_manager.create_questionnaire_form(username)
        
        # Find Roommates page
        elif nav_selection == "Find Roommates":
            st.header("Find Roommates")
            
            # Check if questionnaire is completed
            profile_completed = user_data.get("profile_completed", False) if user_data else False
            questionnaire_completed = user_data.get("questionnaire_completed", False) if user_data else False
            
            if not profile_completed or not questionnaire_completed:
                st.warning("Please complete your profile and questionnaire before finding roommates.")
                
            else:
                # Check if already matched
                if user_data.get("matched", False):
                    st.success("You have already been matched with a roommate! Check your requests tab for details.")
                else:
                    # Get potential matches
                    potential_matches = db.get_all_users_with_completed_questionnaire(except_username=username)
                    
                    if not potential_matches:
                        st.info("No potential roommates found at the moment. Please check back later.")
                    else:
                        # Get user answers
                        user_answers = user_data.get("questionnaire_answers", [])
                        
                        # Find matches
                        matches = matcher.find_matches(user_answers, potential_matches)
                        
                        if not matches:
                            st.info("No compatible roommates found based on your preferences. Please check back later.")
                        else:
                            st.markdown("<div class='section-header'>Your Top Matches</div>", unsafe_allow_html=True)
                            st.write(f"Found {len(matches)} potential roommates that match your preferences.")
                            
                            # Function to handle roommate request
                            def send_request(receiver_username, sender_note):
                                # Get receiver data for email notification
                                receiver_data = db.get_user(receiver_username)
                                
                                if not receiver_data:
                                    st.error(f"User {receiver_username} not found.")
                                    return
                                
                                # Create request
                                if db.create_roommate_request(username, receiver_username):
                                    st.success(f"Request sent to {receiver_username}!")
                                    
                                    # Send email notification
                                    receiver_profile = receiver_data.get("profile", {})
                                    receiver_email = receiver_profile.get("contact_email", "")
                                    receiver_name = receiver_profile.get("full_name", receiver_username)
                                    if receiver_email:
                                        send_roommate_request_notification(username, receiver_email, receiver_name, sender_note)
                                else:
                                    st.error("You have already sent a request to this user.")
                            
                            # Display matches
                            for i, match in enumerate(matches):
                                sender_note = st.text_input(label = "Add a note for receiver", value="")
                                utils.display_match_card(match, i, send_request,sender_note)
        
        # Requests page
        elif nav_selection == "Requests":
            st.header("Roommate Requests")
            
            # Create tabs for received and sent requests
            tab1, tab2 = st.tabs(["Received Requests", "Sent Requests"])
            
            with tab1:
                # Get pending requests
                pending_requests = db.get_pending_requests(username)
                
                if not pending_requests:
                    st.info("No pending requests received.")
                else:
                    st.markdown("<div class='section-header'>Pending Requests</div>", unsafe_allow_html=True)
                    
                    # Functions to handle approving/rejecting requests
                    def approve_request(request_id, receiver_note):
                        if db.update_request_status(request_id, "approved"):
                            st.success("Request approved!")
                            
                            # Get request details for notification
                            request_data = db.db[config.REQUESTS_COLLECTION].find_one({"_id": ObjectId(request_id)})
                            sender_username = request_data.get("sender")
                            sender_data = db.get_user(sender_username)
                            
                            if sender_data:
                                sender_profile = sender_data.get("profile", {})
                                sender_email = sender_profile.get("contact_email", "")
                                sender_name = sender_profile.get("full_name", sender_username)
                                
                                if sender_email:
                                    send_request_status_notification("approved", sender_email, sender_name, username, receiver_note)
                            
                            # Reload page
                            st.experimental_rerun()
                    
                    def reject_request(request_id, receiver_note):
                        if db.update_request_status(request_id, "rejected"):
                            st.success("Request rejected.")
                            
                            # Get request details for notification
                            request_data = db.db[config.REQUESTS_COLLECTION].find_one({"_id": ObjectId(request_id)})
                            sender_username = request_data.get("sender")
                            sender_data = db.get_user(sender_username)
                            
                            if sender_data:
                                sender_profile = sender_data.get("profile", {})
                                sender_email = sender_profile.get("contact_email", "")
                                sender_name = sender_profile.get("full_name", sender_username)
                                
                                if sender_email:
                                    send_request_status_notification("rejected", sender_email, sender_name, username, receiver_note)
                            
                            # Reload page
                            st.experimental_rerun()
                    
                    # Display requests
                    for i, request in enumerate(pending_requests):
                        receiver_note = st.text_input(label = "Add a note for sender", value="")
                        utils.display_request_card(request, i, approve_request, reject_request, receiver_note)
            
            with tab2:
                # Get sent requests
                sent_requests = db.get_sent_requests(username)
                
                if not sent_requests:
                    st.info("You haven't sent any requests yet.")
                else:
                    st.markdown("<div class='section-header'>Your Sent Requests</div>", unsafe_allow_html=True)
                    
                    # Display sent requests with status
                    for request in sent_requests:
                        receiver = request.get("receiver")
                        status = request.get("status").capitalize()
                        date = request.get("created_at").strftime("%Y-%m-%d")
                        
                        status_color = {
                            "Pending": "blue",
                            "Approved": "green",
                            "Rejected": "red"
                        }.get(status, "gray")
                        
                        st.markdown(f"""
                        <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;'>
                            <p><strong>To:</strong> {receiver}</p>
                            <p><strong>Date:</strong> {date}</p>
                            <p><strong>Status:</strong> <span style='color: {status_color};'>{status}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if status == "Approved":
                            # Get receiver contact info
                            receiver_data = db.get_user(receiver)
                            if receiver_data:
                                receiver_profile = receiver_data.get("profile", {})
                                
                                st.markdown("""
                                <div style='padding: 10px; background-color: #000000; border-radius: 5px; margin-bottom: 20px;'>
                                    <h4>Contact Information</h4>
                                """, unsafe_allow_html=True)
                                
                                st.write(f"**Email:** {receiver_profile.get('contact_email', 'Not provided')}")
                                st.write(f"**Phone:** {receiver_profile.get('phone_number', 'Not provided')}")
                                
                                st.markdown("</div>", unsafe_allow_html=True)

# Run app
if __name__ == "__main__":
    pass  # Streamlit automatically runs the script