# english_tutor_module.py
# Additional utilities and modules for the English Learning Assistant

import os
import re
import json
from typing import Dict, Any, List
from IPython.display import display, HTML, Markdown
import google.generativeai as genai

# Set up API key for Google Generative AI (Gemini)
# In Kaggle, you'll want to add your API key as a secret
api_key = os.environ.get("GOOGLE_API_KEY")  # This will fetch from Kaggle secrets
genai.configure(api_key=api_key)

def generate_text(prompt: str, 
                  system_prompt: str = "You are an AI English tutor for non-native speakers.",
                  model: str = "gemini-2.0-flash", 
                  temperature: float = 0.7,
                  max_tokens: int = 1000) -> str:
    """
    Generate text using the Google Gemini API.
    
    Args:
        prompt: The user prompt
        system_prompt: Instructions for the AI
        model: Model to use
        temperature: Controls randomness (0-1)
        max_tokens: Maximum length of response
        
    Returns:
        Generated text
    """
    try:
        # Configure the model
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 64,
        }
        
        # Create the model instance
        model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        
        # Combine system prompt and user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        return response.text
    
    except Exception as e:
        print(f"Error in API call: {e}")
        return f"An error occurred: {e}"

def generate_lesson(topic: str, level: str) -> str:
    """
    Generate an English lesson on a specific topic tailored to the student's level.
    
    Args:
        topic: Subject of the lesson (e.g., "Past tense", "Business vocabulary")
        level: English proficiency level (e.g., "Beginner", "Intermediate", "Advanced")
        
    Returns:
        A structured lesson on the topic
    """
    system_prompt = """
    You are an expert English language teacher. Create a well-structured lesson with the following components:
    1. Brief introduction to the topic
    2. Key concepts and rules
    3. Examples showing correct usage
    4. Common mistakes to avoid
    5. Practice exercises (3-5 items)
    
    Format the lesson clearly with Markdown headings and bullet points for easy readability.
    """
    
    user_prompt = f"Create an English lesson about '{topic}' for {level}-level learners."
    
    return generate_text(user_prompt, system_prompt, temperature=0.5)

def assess_writing(text: str, level: str) -> Dict[str, Any]:
    """
    Assess a piece of writing from an English learner and provide feedback.
    
    Args:
        text: The student's writing sample
        level: English proficiency level
        
    Returns:
        Dictionary with assessment results and feedback
    """
    system_prompt = """
    You are an English writing instructor for non-native speakers. Analyze the provided text and create a detailed assessment with the following:
    
    1. Overall evaluation of writing level
    2. Grammar issues (list specific examples and corrections)
    3. Vocabulary suggestions (recommend better word choices)
    4. Structure and coherence feedback
    5. Three specific suggestions for improvement
    
    Return your response as JSON with these keys: 
    "overall_score" (1-10), 
    "grammar_issues" (list of dicts with "issue" and "correction"), 
    "vocabulary_suggestions" (list of dicts with "original" and "suggestion"),
    "structure_feedback" (string),
    "improvement_suggestions" (list of strings)
    
    Make sure your response is valid JSON with proper formatting and escape characters.
    """
    
    user_prompt = f"""Please assess this {level}-level English learner's writing:
    
    {text}
    
    Provide feedback in JSON format as specified. Your response should be parseable by json.loads() in Python."""
    
    result = generate_text(user_prompt, system_prompt, temperature=0.3)
    
    # Try to parse JSON response
    try:
        # Sometimes the model might include markdown code block markers, so try to extract the JSON
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        else:
            # Try another common pattern
            json_match = re.search(r'```\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
        
        return json.loads(result)
    except json.JSONDecodeError:
        # If AI didn't return valid JSON, return the raw text
        return {"raw_feedback": result}

def generate_quiz(topic: str, level: str, num_questions: int = 5) -> Dict[str, Any]:
    """
    Generate a quiz on an English topic appropriate for the student's level.
    
    Args:
        topic: Subject of the quiz
        level: English proficiency level
        num_questions: Number of questions to generate
        
    Returns:
        Dictionary with quiz questions, options, answers and explanations
    """
    system_prompt = """
    You are an English language assessment expert. Create a multiple-choice quiz on the specified topic.
    
    For each question:
    1. Write a clear question
    2. Provide 4 options (A, B, C, D)
    3. Indicate the correct answer
    4. Include a brief explanation of why the answer is correct
    
    Return your response as JSON with a "questions" key containing a list of question objects.
    Each question object should have: "question", "options" (list), "correct_answer", and "explanation".
    
    Make sure your response is valid JSON with proper formatting and escape characters.
    """
    
    user_prompt = f"""Create a {num_questions}-question quiz about '{topic}' for {level}-level English learners.
    Return the quiz in JSON format as specified. Your response should be parseable by json.loads() in Python."""
    
    result = generate_text(user_prompt, system_prompt, temperature=0.7)
    # You may want to add more robust parsing/validation here
    try:
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        else:
            json_match = re.search(r'```\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
        return json.loads(result)
    except json.JSONDecodeError:
        return {"raw_quiz": result}

def simulate_conversation(scenario: str, level: str) -> List[Dict[str, str]]:
    """
    Generate a simulated conversation for conversation practice.
    
    Args:
        scenario: Context for the conversation (e.g., "At a restaurant", "Job interview")
        level: English proficiency level
        
    Returns:
        List of conversation turns with speaker and text
    """
    system_prompt = """
    You are an English conversation practice assistant. Create a natural dialogue between two people based 
    on the given scenario. The conversation should be appropriate for the learner's level, 
    introducing useful phrases and vocabulary. Include 6-10 turns in the conversation.
    
    Return your response as JSON with a "conversation" key containing a list of conversation turns.
    Each turn should have a "speaker" (either "Person A" or "Person B") and "text".
    
    Make sure your response is valid JSON with proper formatting and escape characters.
    """
    
    user_prompt = f"""Create a conversation practice dialogue for a {level}-level English learner 
    in this scenario: '{scenario}'. Return the conversation in JSON format as specified. 
    Your response should be parseable by json.loads() in Python."""
    
    result = generate_text(user_prompt, system_prompt, temperature=0.7)
    
    # Try to parse JSON response
    try:
        # Sometimes the model might include markdown code block markers, so try to extract the JSON
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        else:
            # Try another common pattern
            json_match = re.search(r'```\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
        
        data = json.loads(result)
        return data.get("conversation", [])
    except json.JSONDecodeError:
        # If AI didn't return valid JSON, structure the response manually
        return [{"speaker": "System", "text": "Could not generate structured conversation. Raw output: " + result}]

def display_tutor_output(output, output_type):
    """
    Display the tutors output in a visually appealing way.
    
    Args:
        output: The output from one of the tutor functions
        output_type: The type of output (lesson, assessment, quiz, conversation)
    """
    if output_type == "lesson":
        display(Markdown(output))
    
    elif output_type == "assessment":
        if "raw_feedback" in output:
            display(Markdown(output["raw_feedback"]))
        else:
            html = f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:10px;">
                <h3>Writing Assessment</h3>
                <h4>Overall Score: {output.get('overall_score', 'N/A')}/10</h4>
                
                <h4>Grammar Issues:</h4>
                <ul>
            """
            for issue in output.get('grammar_issues', []):
                html += f"<li><b>Issue:</b> {issue.get('issue', '')}<br><b>Correction:</b> {issue.get('correction', '')}</li>"
            
            html += """</ul>
                <h4>Vocabulary Suggestions:</h4>
                <ul>
            """
            
            for suggestion in output.get('vocabulary_suggestions', []):
                html += f"<li><b>Original:</b> {suggestion.get('original', '')}<br><b>Suggestion:</b> {suggestion.get('suggestion', '')}</li>"
            
            html += f"""</ul>
                <h4>Structure Feedback:</h4>
                <p>{output.get('structure_feedback', 'N/A')}</p>
                
                <h4>Improvement Suggestions:</h4>
                <ol>
            """
            
            for suggestion in output.get('improvement_suggestions', []):
                html += f"<li>{suggestion}</li>"
            
            html += """</ol>
            </div>
            """
            display(HTML(html))
    
    elif output_type == "quiz":
        if "raw_quiz" in output:
            display(Markdown(output["raw_quiz"]))
        else:
            html = """
            <div style="border:1px solid #ddd; padding:15px; border-radius:10px;">
                <h3>Quiz</h3>
            """
            
            for i, q in enumerate(output.get('questions', [])):
                html += f"""
                <div style="margin-bottom:20px;">
                    <p><b>Question {i+1}:</b> {q.get('question', '')}</p>
                    <ul style="list-style-type:upper-alpha;">
                """
                
                for option in q.get('options', []):
                    html += f"<li>{option}</li>"
                
                html += f"""
                    </ul>
                    <p><b>Correct Answer:</b> {q.get('correct_answer', '')}</p>
                    <p><b>Explanation:</b> {q.get('explanation', '')}</p>
                </div>
                """
            
            html += "</div>"
            display(HTML(html))
    
    elif output_type == "conversation":
        html = """
        <div style="border:1px solid #ddd; padding:15px; border-radius:10px;">
            <h3>Conversation Practice</h3>
        """
        
        for turn in output:
            speaker_color = "#e6f7ff" if turn.get('speaker') == "Person A" else "#f0f0f0"
            html += f"""
            <div style="background-color:{speaker_color}; margin:5px; padding:10px; border-radius:5px;">
                <b>{turn.get('speaker', 'Unknown')}:</b> {turn.get('text', '')}
            </div>
            """
        
        html += "</div>"
        display(HTML(html))

# Main function to handle different types of requests
def english_tutor(request_type: str, **kwargs) -> Any:
    """
    Main function to interact with the English tutor system.
    
    Args:
        request_type: Type of tutoring request 
                     ("lesson", "assessment", "quiz", "conversation")
        **kwargs: Arguments specific to the request type
        
    Returns:
        The output from the requested tutoring function
    """
    if request_type == "lesson":
        required = ["topic", "level"]
        if not all(k in kwargs for k in required):
            return "Error: Please provide topic and level for lesson generation."
        return generate_lesson(kwargs["topic"], kwargs["level"])
    
    elif request_type == "assessment":
        required = ["text", "level"]
        if not all(k in kwargs for k in required):
            return "Error: Please provide text and level for writing assessment."
        return assess_writing(kwargs["text"], kwargs["level"])
    
    elif request_type == "quiz":
        required = ["topic", "level"]
        if not all(k in kwargs for k in required):
            return "Error: Please provide topic and level for quiz generation."
        num_questions = kwargs.get("num_questions", 5)
        return generate_quiz(kwargs["topic"], kwargs["level"], num_questions)
    
    elif request_type == "conversation":
        required = ["scenario", "level"]
        if not all(k in kwargs for k in required):
            return "Error: Please provide scenario and level for conversation practice."
        return simulate_conversation(kwargs["scenario"], kwargs["level"])
    
    else:
        return f"Error: Unknown request type '{request_type}'. Supported types: lesson, assessment, quiz, conversation."

# Example usage
def run_demonstration():
    print("===== English Tutor Bot Demonstration =====")
    
    # Example 1: Generate a lesson
    print("\n1. Generating a lesson on Past Continuous tense for intermediate learners...")
    lesson = generate_lesson("Past Continuous tense", "Intermediate")
    display_tutor_output(lesson, "lesson")
    
    # Example 2: Assess a writing sample
    print("\n2. Assessing a writing sample...")
    sample_text = """
    Yesterday I go to the store and buyed some food. The weather was very nice and I enjoy 
    my walk. I think English is difficult but I trying to improve everyday. Sometimes I watch 
    movies without subtitles for practice my listening.
    """
    assessment = assess_writing(sample_text, "Intermediate")
    display_tutor_output(assessment, "assessment")
    
    # Example 3: Generate a quiz
    print("\n3. Generating a quiz on prepositions...")
    quiz = generate_quiz("Prepositions of place", "Beginner", 3)
    display_tutor_output(quiz, "quiz")
    
    # Example 4: Generate a conversation practice
    print("\n4. Generating a conversation practice for ordering at a restaurant...")
    conversation = simulate_conversation("Ordering food at a restaurant", "Beginner")
    display_tutor_output(conversation, "conversation")

if __name__ == "__main__":
    run_demonstration()
    