import streamlit as st
import json
import os
from database import MongoDB
import config
import logging
import uuid
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.db = MongoDB()
    
    def get_userdata_by_username(self, username):
        """Get user data from database by username"""
        # First try to get from MongoDB
        user_data = self.db.get_user(username)
        
        if user_data:
            return user_data
            
        # If not found in MongoDB, try to get from auth file
        try:
            if os.path.exists(config.SECRET_AUTH_PATH):
                with open(config.SECRET_AUTH_PATH, 'r') as f:
                    json_data = json.load(f)
                    
                for user in json_data:
                    if user.get("username") == username:
                        user_data = user.copy()
                        if 'password' in user_data:
                            del user_data['password']
                        return user_data
        except Exception as e:
            logger.error(f"Error reading auth file: {e}")
            
        return None
    
    def save_user_to_mongodb(self, username):
        """Save user from auth file to MongoDB if not exists"""
        # Check if user already exists in MongoDB
        if self.db.get_user(username):
            return True
            
        # Get user from auth file
        user_data = None
        try:
            if os.path.exists(config.SECRET_AUTH_PATH):
                with open(config.SECRET_AUTH_PATH, 'r') as f:
                    json_data = json.load(f)
                    
                for user in json_data:
                    if user.get("username") == username:
                        user_data = user.copy()
                        if 'password' in user_data:
                            del user_data['password']
                        break
        except Exception as e:
            logger.error(f"Error reading auth file: {e}")
            return False
            
        if not user_data:
            return False
        
        # Add additional fields for roommate finder app
        user_data["profile_completed"] = False
        user_data["questionnaire_completed"] = False
        user_data["matched"] = False
        
        # Save to MongoDB
        return self.db.save_user(user_data)
    
    def create_profile_form(self, username):
        """Create and handle user profile form"""
        st.markdown("<div class='section-header'>Complete Your Profile</div>", unsafe_allow_html=True)
        st.write("Please fill in your personal details to help find a compatible roommate.")
        
        # Get existing user data
        user_data = self.db.get_user(username)
        profile = user_data.get("profile", {}) if user_data else {}
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
                age = st.number_input("Age", min_value=18, max_value=100, value=profile.get("age", 25))
                gender = st.selectbox("Gender", 
                                    ["Male", "Female", "Non-binary", "Prefer not to say"],
                                    index=["Male", "Female", "Non-binary", "Prefer not to say"].index(profile.get("gender", "Prefer not to say")) if profile.get("gender") else 0)
                occupation = st.text_input("Occupation", value=profile.get("occupation", ""))
            
            with col2:
                contact_email = st.text_input("Contact Email", value=profile.get("contact_email", ""))
                phone_number = st.text_input("Phone Number", value=profile.get("phone_number", ""))
                max_budget = st.number_input("Maximum Monthly Budget ($)", min_value=0, value=profile.get("max_budget", 1000))
                move_in_date = st.date_input("Preferred Move-in Date", value=None)
            
            bio = st.text_area("Bio (Tell us about yourself)", value=profile.get("bio", ""), height=150)
            
            uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            
            submit_btn = st.form_submit_button("Save Profile")
            
            if submit_btn:
                # Validate required fields
                if not full_name or not contact_email or not bio or not uploaded_file:
                    st.error("Please fill in all required fields (Name, Email, Bio, profile image, etc)")
                    return False
                
                profile_data = {
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "contact_email": contact_email,
                    "phone_number": phone_number,
                    "max_budget": max_budget,
                    "bio": bio
                }

                if move_in_date:
                    profile_data["move_in_date"] = move_in_date.isoformat()

                if uploaded_file:
                    ext = Path(uploaded_file.name).suffix
                    image_id = str(uuid.uuid4()) + ext
                    image_path = os.path.join("profile_images", image_id)
                    
                    # Ensure the directory exists
                    os.makedirs("profile_images", exist_ok=True)
                    
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.read())
                    
                    profile_data["profile_image"] = image_path

                if self.db.update_user_profile(username, profile_data):
                    st.success("Profile saved successfully!")
                    return True
                else:
                    st.error("Failed to save profile. Please try again.")
                    return False

        return False
    
    def create_questionnaire_form(self, username):
        """Create and handle questionnaire form"""
        st.markdown("<div class='section-header'>Roommate Preferences Questionnaire</div>", unsafe_allow_html=True)
        st.write("Please answer the following questions to help us find your ideal roommate match.")
        
        # Get existing answers if any
        user_data = self.db.get_user(username)
        existing_answers = user_data.get("questionnaire_answers", []) if user_data else []
        
        with st.form("questionnaire_form"):
            answers = []
            
            for i, question in enumerate(config.ROOMMATE_QUESTIONS):
                existing_answer = existing_answers[i] if i < len(existing_answers) else ""
                answer = st.text_area(f"{i+1}. {question}", value=existing_answer, height=100)
                answers.append(answer)
            
            submit_btn = st.form_submit_button("Submit Answers")
            
            if submit_btn:
                # Check if all questions are answered
                if all(answers):
                    # Save answers to database
                    if self.db.update_user_questionnaire(username, answers):
                        st.success("Your answers have been saved successfully!")
                        return True
                    else:
                        st.error("Failed to save your answers. Please try again.")
                        return False
                else:
                    st.error("Please answer all questions before submitting.")
                    return False
        
        return False