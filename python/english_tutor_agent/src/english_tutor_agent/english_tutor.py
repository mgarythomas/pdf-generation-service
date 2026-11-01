# english_tutor.py
# Core module for the GenAI-powered English Learning Assistant

import os
import google.generativeai as genai

# Configure your API key (best to use environment variables)
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

class EnglishTutor:
    """
    An English language tutoring assistant that uses Gemini AI to help students improve their English skills through conversation, grammar correction, vocabulary enrichment, and personalized lessons.
    """
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
        You are an English language tutor. Your goal is to help students improve their 
        English skills through conversation, grammar correction, vocabulary enrichment,
        and personalized lessons. Be supportive, patient, and provide clear explanations.
        The student can have a specified level of English proficiency (Beginner, Intermediate, Advanced).
        The class will be one of 4 options (Conversation, Grammar, Quiz, Lesson) that the student wants to focus on.
        """
    
    def start_session(self, user_prompt):
        """
        Start a new conversation session with the tutor.
        
        Args:
            user_prompt: Initial user input or question
            
        Returns:
            Response from the tutor
        """
        # Combine system prompt with user input
        full_prompt = self.system_prompt + "\n\nStudent: " + user_prompt
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_prompt})
        self.conversation_history.append({"role": "tutor", "content": response.text})
        
        return response.text
    
    def continue_conversation(self, user_input):
        """
        Continue an existing conversation session with the tutor.
        
        Args:
            user_input: User's input or question
            
        Returns:
            Response from the tutor
        """
        # Format the conversation history for the model
        formatted_history = self.system_prompt + "\n"
        for message in self.conversation_history:
            if message["role"] == "user":
                formatted_history += f"\nStudent: {message['content']}"
            else:
                formatted_history += f"\nTutor: {message['content']}"
        
        # Add the new user input
        formatted_history += f"\nStudent: {user_input}"
        formatted_history += "\nTutor:"
        
        # Generate response
        response = model.generate_content(formatted_history)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "tutor", "content": response.text})
        
        return response.text