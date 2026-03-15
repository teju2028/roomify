import streamlit as st
import json
import base64
from PIL import Image
import io
import config

def inject_custom_css():
    """Inject custom CSS into the Streamlit app"""
    st.markdown(config.CSS, unsafe_allow_html=True)

def display_profile_summary(profile_data):
    """Display a summary of user profile"""
    if not profile_data:
        st.warning("Profile data not available")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display profile picture (placeholder for now)
        if profile_data.get("profile_image"):
            st.image(profile_data.get("profile_image"), width=150, caption="Profile Picture")
        else:
            st.image('no_profile.jpg', width=150, caption="No Profile Picture")
    
    with col2:
        st.subheader(profile_data.get("full_name", "Name not provided"))
        st.write(f"Age: {profile_data.get('age', 'Not provided')}")
        st.write(f"Gender: {profile_data.get('gender', 'Not provided')}")
        st.write(f"Occupation: {profile_data.get('occupation', 'Not provided')}")
        st.write(f"Budget: ${profile_data.get('max_budget', 0)}/month")
        
        if profile_data.get("move_in_date"):
            st.write(f"Preferred Move-in Date: {profile_data.get('move_in_date')}")
    
    st.subheader("About Me")
    st.write(profile_data.get("bio", "No bio provided"))

def display_match_card(match_info, index, on_request_click,sender_note):
    """Display a card for a potential roommate match"""
    similarity = match_info["similarity_score"] * 100
    profile = match_info.get("profile", {})
    
    with st.container():
        # st.markdown(f"<div class='match-card'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.image(profile.get("profile_image"), width=100)
            st.markdown(f"<p style='text-align: center; font-weight: bold;'>{similarity:.1f}% Match</p>", unsafe_allow_html=True)
        
        with col2:
            st.subheader(profile.get("full_name", match_info["username"]))
            st.write(f"Age: {profile.get('age', 'Not provided')} | Gender: {profile.get('gender', 'Not provided')}")
            st.write(f"Occupation: {profile.get('occupation', 'Not provided')}")
            st.write(f"Budget: ${profile.get('max_budget', 0)}/month")
            
            # Show a preview of bio
            bio = profile.get("bio", "")
            if bio:
                if len(bio) > 100:
                    st.write(f"{bio[:100]}...")
                else:
                    st.write(bio)
        
        with col3:
            if st.button(f"Send Request", key=f"request_{index}"):
                with st.spinner("Sending Request..."):
                    on_request_click(match_info["username"], sender_note)
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_request_card(request, index, on_approve, on_reject, receiver_note):
    """Display a card for a roommate request"""
    # st.markdown(f"<div class='request-card'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    
    with col1:
        st.write(f"**From:** {request.get('sender')}")
        st.write(f"**Date:** {request.get('created_at').strftime('%Y-%m-%d')}")
    
    with col2:
        st.write(f"**Status:** {request.get('status').capitalize()}")
    
    with col3:
        if request.get('status') == 'pending':
            if st.button("Approve", key=f"approve_{index}"):
                on_approve(str(request.get('_id')), receiver_note)
    
    with col4:
        if request.get('status') == 'pending':
            if st.button("Reject", key=f"reject_{index}"):
                on_reject(str(request.get('_id')), receiver_note)
    
    st.markdown("</div>", unsafe_allow_html=True)

def check_profile_completeness(profile):
    """Check if user profile has all required fields"""
    if not profile:
        return False
    
    for field in config.REQUIRED_PROFILE_FIELDS:
        if field not in profile or not profile[field]:
            return False
    
    return True

def user_setup_progress(user_data):
    """Calculate and display user setup progress"""
    if not user_data:
        return 0
    
    progress = 0
    steps = 2  # Profile + Questionnaire
    
    if user_data.get("profile_completed", False):
        progress += 1
    
    if user_data.get("questionnaire_completed", False):
        progress += 1
    
    progress_percentage = (progress / steps) * 100
    
    st.progress(progress_percentage / 100)
    st.write(f"Profile Setup Progress: {progress_percentage:.0f}%")
    
    return progress_percentage

def format_request_data(request_data, user_profiles):
    """Format request data with user profile information"""
    if not request_data:
        return []
    
    formatted_requests = []
    
    for request in request_data:
        sender = request.get("sender")
        receiver = request.get("receiver")
        
        sender_profile = user_profiles.get(sender, {})
        receiver_profile = user_profiles.get(receiver, {})
        
        formatted_request = {
            **request,
            "sender_profile": sender_profile,
            "receiver_profile": receiver_profile
        }
        
        formatted_requests.append(formatted_request)
    
    return formatted_requests