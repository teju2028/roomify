from pymongo import MongoClient
import pymongo
import config
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            try:
                cls._instance.client = MongoClient(config.MONGO_URI)
                cls._instance.db = cls._instance.client[config.DB_NAME]
                # Create indexes for better query performance
                cls._instance.db[config.USERS_COLLECTION].create_index([("username", pymongo.ASCENDING)], unique=True)
                cls._instance.db[config.REQUESTS_COLLECTION].create_index([("sender", pymongo.ASCENDING), 
                                                                          ("receiver", pymongo.ASCENDING)], 
                                                                         unique=True)
                logger.info("MongoDB connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return cls._instance
    
    def get_user(self, username):
        """Get user data by username"""
        return self.db[config.USERS_COLLECTION].find_one({"username": username})
    
    def save_user(self, user_data):
        """Save or update user data"""
        username = user_data.get("username")
        if not username:
            logger.error("Cannot save user without username")
            return False
            
        user_data["updated_at"] = datetime.datetime.utcnow()
        
        if self.get_user(username):
            result = self.db[config.USERS_COLLECTION].update_one(
                {"username": username},
                {"$set": user_data}
            )
            return result.modified_count > 0
        else:
            user_data["created_at"] = datetime.datetime.utcnow()
            result = self.db[config.USERS_COLLECTION].insert_one(user_data)
            return result.inserted_id is not None
    
    def update_user_profile(self, username, profile_data):
        """Update user profile information"""
        result = self.db[config.USERS_COLLECTION].update_one(
            {"username": username},
            {"$set": {
                "profile": profile_data,
                "profile_completed": True,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    def update_user_questionnaire(self, username, answers):
        """Update user questionnaire answers"""
        result = self.db[config.USERS_COLLECTION].update_one(
            {"username": username},
            {"$set": {
                "questionnaire_answers": answers,
                "questionnaire_completed": True,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    def get_all_users_with_completed_questionnaire(self, except_username=None):
        """Get all users who have completed their questionnaire"""
        query = {
            "questionnaire_completed": True,
            "profile_completed": True,
            "matched": {"$ne": True}
        }
        
        if except_username:
            query["username"] = {"$ne": except_username}
            
        return list(self.db[config.USERS_COLLECTION].find(query))
    
    def get_pending_requests(self, username):
        """Get all pending roommate requests for a user"""
        return list(self.db[config.REQUESTS_COLLECTION].find({
            "receiver": username,
            "status": "pending"
        }))
    
    def get_sent_requests(self, username):
        """Get all sent roommate requests by a user"""
        return list(self.db[config.REQUESTS_COLLECTION].find({
            "sender": username
        }))
    
    def create_roommate_request(self, sender, receiver):
        """Create a new roommate request"""
        # Check if a request already exists
        existing = self.db[config.REQUESTS_COLLECTION].find_one({
            "sender": sender,
            "receiver": receiver
        })
        
        if existing:
            return False
            
        request_data = {
            "sender": sender,
            "receiver": receiver,
            "status": "pending",
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        result = self.db[config.REQUESTS_COLLECTION].insert_one(request_data)
        return result.inserted_id is not None
    
    def update_request_status(self, request_id, status):
        """Update the status of a roommate request"""
        from bson.objectid import ObjectId
        
        result = self.db[config.REQUESTS_COLLECTION].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "status": status,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        
        # If approved, mark both users as matched
        if status == "approved":
            request = self.db[config.REQUESTS_COLLECTION].find_one({"_id": ObjectId(request_id)})
            if request:
                self.db[config.USERS_COLLECTION].update_one(
                    {"username": request["sender"]},
                    {"$set": {"matched": True}}
                )
                self.db[config.USERS_COLLECTION].update_one(
                    {"username": request["receiver"]},
                    {"$set": {"matched": True}}
                )
        
        return result.modified_count > 0