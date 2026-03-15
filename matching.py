import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RoommateMatcher:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RoommateMatcher, cls).__new__(cls)
            try:
                # Load sentence transformer model
                cls._instance.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Sentence transformer model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer model: {e}")
                raise
        return cls._instance
    
    def combine_answers(self, answers):
        """Combine all answers into a single text"""
        if not answers or not isinstance(answers, list):
            return ""
        
        return " ".join([str(answer) for answer in answers if answer])
    
    def get_embedding(self, text):
        """Get embedding for a text"""
        if not text:
            return np.zeros((384,))  # Return zero vector if text is empty
        
        return self.model.encode(text)
    
    def find_matches(self, user_answers, potential_matches):
        """Find top matches based on questionnaire answers"""
        if not user_answers or not potential_matches:
            return []
        
        # Get embedding for the user's answers
        user_text = self.combine_answers(user_answers)
        user_embedding = self.get_embedding(user_text)
        
        matches = []
        
        for match in potential_matches:
            match_answers = match.get("questionnaire_answers", [])
            match_text = self.combine_answers(match_answers)
            match_embedding = self.get_embedding(match_text)
            
            # Calculate similarity score
            similarity = cosine_similarity([user_embedding], [match_embedding])[0][0]
            
            # Add to matches if above threshold
            if similarity > config.SIMILARITY_THRESHOLD:
                match_info = {
                    "username": match["username"],
                    "similarity_score": similarity,
                    "profile": match.get("profile", {}),
                }
                matches.append(match_info)
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return top N matches
        return matches[:config.TOP_MATCHES]