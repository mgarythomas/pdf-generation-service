# GenAI-Powered English Learning Assistant - Demo Notebook
# =====================================================

# This notebook demonstrates a GenAI-powered Learning Management System (LMS) and Tutor Bot
# designed specifically for English language learners.

# Import necessary libraries
import os
import sys
import time
import google.generativeai as genai
import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
from IPython.display import display, HTML, Markdown, clear_output
import ipywidgets as widgets
from IPython.display import display

# Check if we're running in Kaggle environment
IN_KAGGLE = 'KAGGLE_KERNEL_RUN_TYPE' in os.environ

if IN_KAGGLE:
    # Use Kaggle secret for API key if available
    try:
        from kaggle_secrets import UserSecretsClient
        user_secrets = UserSecretsClient()
        api_key = user_secrets.get_secret("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        print("✅ API key loaded from Kaggle secrets")
    except:
        print("❌ Could not load API key from Kaggle secrets. Please add your Google API key.")
        print("   Go to 'Add-ons' -> 'Secrets' and add GOOGLE_API_KEY with your key.")
        api_key = None
else:
    # For local development
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ API key loaded from environment variable")
    else:
        print("❌ API key not found. Please set the GOOGLE_API_KEY environment variable.")

# Import our English Tutor module
# NOTE: In a real Kaggle notebook, you would need to include this code directly or as a separate file
from english_tutor import (
    generate_lesson, 
    assess_writing, 
    generate_quiz, 
    simulate_conversation, 
    display_tutor_output, 
    english_tutor
)

# Function to display notebook sections more cleanly
def display_section(title, description=""):
    """Display a nicely formatted section header"""
    display(HTML(f"""
    <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin-top:30px; margin-bottom:20px;">
        <h2 style="margin-top:0px">{title}</h2>
        <p>{description}</p>
    </div>
    """))

# Introduction to the Project
display_section("GenAI-Powered English Learning Assistant", 
                "A demonstration of how generative AI can help non-native English speakers improve their language skills")

display(Markdown("""
This notebook demonstrates a prototype of an AI-powered English learning assistant designed specifically for language learners. 
The system can:

1. **Generate custom English lessons** on various topics and tailored to different proficiency levels
2. **Assess writing samples** and provide detailed feedback on grammar, vocabulary, and structure
3. **Create interactive quizzes** to test knowledge and reinforce learning
4. **Simulate authentic conversations** for practice in real-world scenarios

This technology has the potential to make personalized language learning more accessible and effective by providing immediate,
specific feedback and unlimited practice opportunities.

Let's explore each functionality with examples!
"""))

# 1. Lesson Generation
display_section("1. Lesson Generation", 
                "Creating custom English lessons on specific topics tailored to the student's level")

display(Markdown("""
Our system can generate complete English lessons on demand, customized for the learner's proficiency level. 
This allows for personalized learning paths that target specific needs.

Let's try generating some sample lessons:
"""))

# Examples of lesson generation
lesson_examples = [
    {"topic": "Present Perfect Tense", "level": "Intermediate"},
    {"topic": "Business Email Writing", "level": "Advanced"},
    {"topic": "Common Phrasal Verbs", "level": "Beginner"}
]

# Create a lesson selection widget
lesson_topic = widgets.Dropdown(
    options=[f"{ex['topic']} ({ex['level']})" for ex in lesson_examples],
    description='Select Lesson:',
    disabled=False,
)

generate_btn = widgets.Button(
    description='Generate Lesson',
    button_style='primary',
    icon='check'
)

output_lesson = widgets.Output()

def on_generate_lesson_click(b):
    with output_lesson:
        clear_output()
        print("Generating lesson... (This may take a moment)")
        
        # Get the selected example
        selected_idx = lesson_topic.index
        selected_example = lesson_examples[selected_idx]
        
        # Generate the lesson
        lesson = generate_lesson(selected_example["topic"], selected_example["level"])
        
        # Display results
        clear_output()
        print(f"📚 Lesson on {selected_example['topic']} for {selected_example['level']} level:")
        display_tutor_output(lesson, "lesson")

generate_btn.on_click(on_generate_lesson_click)

# Display the lesson generation widgets
display(widgets.VBox([lesson_topic, generate_btn, output_lesson]))

# 2. Writing Assessment
display_section("2. Writing Assessment", 
                "Analyzing student writing to provide feedback and suggestions for improvement")

display(Markdown("""
Our system can analyze writing samples from English learners and provide detailed, constructive feedback.
The assessment covers grammar issues, vocabulary suggestions, structural feedback, and specific improvement ideas.

Try with these example writing samples or enter your own text:
"""))

# Sample texts for assessment
sample_texts = {
    "Beginner": """
    Yesterday I go to the store and buyed some food. The weather was very nice and I enjoy 
    my walk. I think English is difficult but I trying to improve everyday. Sometimes I watch 
    movies without subtitles for practice my listening.
    """,
    
    "Intermediate": """
    Last summer, I had the opportunity to visited London for two weeks. It was my first time 
    traveling to Europe and I was very exciting. The city has many beautiful buildings and parks.
    Despite the weather wasn't good, I enjoyed my trip very much. I think that traveling is the 
    best way for learning about different cultures and improving language skills.
    """,
    
    "Advanced": """
    The implementation of artificial intelligence in educational settings has garnered significant 
    attention in recent years. While proponents argue that AI technologies can personalize learning 
    experiences and address individual student needs, critics are concerned about potential privacy 
    implications and the reduction of human interaction in the classroom. Based on my research, I 
    believe a balanced approach which integrates AI tools while maintaining the crucial role of 
    teachers would be the most beneficial strategy for educational institutions moving forward.
    """
}

# Create widgets for writing assessment
text_level = widgets.RadioButtons(
    options=['Beginner', 'Intermediate', 'Advanced'],
    description='Level:',
    disabled=False
)

text_area = widgets.Textarea(
    value=sample_texts["Beginner"],
    placeholder='Enter text to assess',
    description='Writing:',
    disabled=False,
    rows=10,
    style={'description_width': 'initial'}
)

assess_btn = widgets.Button(
    description='Assess Writing',
    button_style='primary',
    icon='check'
)

output_assessment = widgets.Output()

def on_level_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        text_area.value = sample_texts[change['new']]

text_level.observe(on_level_change)

def on_assess_writing_click(b):
    with output_assessment:
        clear_output()
        print("Analyzing writing... (This may take a moment)")
        
        # Get the input text and level
        text = text_area.value
        level = text_level.value
        
        # Generate the assessment
        assessment = assess_writing(text, level)
        
        # Display results
        clear_output()
        print(f"✏️ Writing Assessment for {level} level:")
        display_tutor_output(assessment, "assessment")

assess_btn.on_click(on_assess_writing_click)

# Display writing assessment widgets
display(widgets.VBox([text_level, text_area, assess_btn, output_assessment]))

# 3. Quiz Generation
display_section("3. Quiz Generation", 
                "Creating interactive quizzes to test knowledge and reinforce learning")

display(Markdown("""
Our system can generate customized quizzes on specific English language topics. Each quiz includes
questions with multiple-choice options, correct answers, and explanations to help learners understand
why certain answers are correct.

Let's generate some example quizzes:
"""))

# Examples of quiz topics
quiz_examples = [
    {"topic": "Irregular Verbs", "level": "Beginner", "num_questions": 3},
    {"topic": "Conditionals", "level": "Intermediate", "num_questions": 3},
    {"topic": "Collocations", "level": "Advanced", "num_questions": 3}
]

# Create quiz selection widgets
quiz_topic = widgets.Dropdown(
    options=[f"{ex['topic']} ({ex['level']})" for ex in quiz_examples],
    description='Select Quiz:',
    disabled=False,
)

quiz_btn = widgets.Button(
    description='Generate Quiz',
    button_style='primary',
    icon='check'
)

output_quiz = widgets.Output()

def on_generate_quiz_click(b):
    with output_quiz:
        clear_output()
        print("Generating quiz... (This may take a moment)")
        
        # Get the selected example
        selected_idx = quiz_topic.index
        selected_example = quiz_examples[selected_idx]
        
        # Generate the quiz
        quiz = generate_quiz(
            selected_example["topic"], 
            selected_example["level"], 
            selected_example["num_questions"]
        )
        
        # Display results
        clear_output()
        print(f"🧠 Quiz on {selected_example['topic']} for {selected_example['level']} level:")
        display_tutor_output(quiz, "quiz")

quiz_btn.on_click(on_generate_quiz_click)

# Display quiz generation widgets
display(widgets.VBox([quiz_topic, quiz_btn, output_quiz]))

# 4. Conversation Practice
display_section("4. Conversation Practice", 
                "Simulating authentic conversations for real-world language practice")

display(Markdown("""
Our system can generate realistic conversation scenarios to help learners practice their speaking and listening skills.
These conversations introduce useful phrases and vocabulary in context, helping students prepare for real-world interactions.

Let's explore some conversation scenarios:
"""))

# Examples of conversation scenarios
conversation_examples = [
    {"scenario": "Ordering food at a restaurant", "level": "Beginner"},
    {"scenario": "Job interview for an office position", "level": "Intermediate"},
    {"scenario": "Discussing climate change solutions", "level": "Advanced"}
]

# Create conversation selection widgets
conversation_scenario = widgets.Dropdown(
    options=[f"{ex['scenario']} ({ex['level']})" for ex in conversation_examples],
    description='Select Scenario:',
    disabled=False,
)

conversation_btn = widgets.Button(
    description='Generate Conversation',
    button_style='primary',
    icon='check'
)

output_conversation = widgets.Output()

def on_generate_conversation_click(b):
    with output_conversation:
        clear_output()
        print("Generating conversation... (This may take a moment)")
        
        # Get the selected example
        selected_idx = conversation_scenario.index
        selected_example = conversation_examples[selected_idx]
        
        # Generate the conversation
        conversation = simulate_conversation(
            selected_example["scenario"], 
            selected_example["level"]
        )
        
        # Display results
        clear_output()
        print(f"💬 Conversation about {selected_example['scenario']} for {selected_example['level']} level:")
        display_tutor_output(conversation, "conversation")

conversation_btn.on_click(on_generate_conversation_click)

# Display conversation generation widgets
display(widgets.VBox([conversation_scenario, conversation_btn, output_conversation]))

# 5. Combined Learning Experience
display_section("5. Combined Learning Experience", 
                "Showcasing how all components work together for a complete learning journey")

display(Markdown("""
In a real application, these components would work together to create a comprehensive learning experience.
Here's a demonstration of a complete learning session focusing on a single topic:
"""))

# Topic selection for combined experience
topic_options = [
    "Modal Verbs (Intermediate)",
    "Email Writing (Advanced)",
    "Food Vocabulary (Beginner)"
]

combined_topic = widgets.Dropdown(
    options=topic_options,
    description='Learning Topic:',
    disabled=False,
)

combined_btn = widgets.Button(
    description='Start Learning Journey',
    button_style='primary',
    icon='play'
)

output_combined = widgets.Output()

def on_start_journey_click(b):
    with output_combined:
        clear_output()
        
        # Parse selected topic
        selected = combined_topic.value
        topic, level = selected.split(" (")
        level = level.rstrip(")")
        
        print(f"📝 Starting a learning journey on {topic} for {level} level...")
        print("This will generate a lesson, quiz, and conversation practice. (This may take a few moments)")
        
        # Step 1: Generate lesson
        print("\n📚 STEP 1: Learning the material")
        lesson = generate_lesson(topic, level)
        display_tutor_output(lesson, "lesson")
        
        # Step 2: Generate a quiz
        print("\n🧠 STEP 2: Testing knowledge with a quiz")
        quiz = generate_quiz(topic, level, 3)
        display_tutor_output(quiz, "quiz")
        
        # Step 3: Generate conversation practice
        print("\n💬 STEP 3: Practicing in conversation")
        conversation = simulate_conversation(f"Using {topic} in everyday situations", level)
        display_tutor_output(conversation, "conversation")
        
        # Step 4: Practice writing assessment
        print("\n✏️ STEP 4: Writing practice and feedback")
        print("In a real application, the user would write their own text here.")
        print("For demonstration purposes, we'll use a sample text:")
        
        # Sample texts based on the topic
        if "Modal" in topic:
            sample_text = """
            I think that I must to study more to improve my English. 
            Sometimes I can understanding when people speak fast, but I can't response quickly.
            I should studying modal verbs because they are very important, 
            and I would to use them correctly in the future.
            """
        elif "Email" in topic:
            sample_text = """
            Dear Sir,
            
            I am writing this email for ask about your product that I saw on your website.
            I want to buy it but I didn't found the price. Can you tell me how much it costs?
            Also, I would like to know if you can delivering to my country.
            
            I look forward to hear from you soon.
            
            Best regards,
            John
            """
        else:  # Food vocabulary
            sample_text = """
            Yesterday I go to a restaurant with my friend. We ordered many delicious foods.
            I eated a steak and potato. My friend had the fish with vegetables. 
            For dessert we shared a chocolate cake. The meal costed a lot but it was very nice.
            """
        
        print(f"\nSample writing about {topic}:")
        print("----------------------------")
        print(sample_text)
        print("----------------------------")
        
        assessment = assess_writing(sample_text, level)
        display_tutor_output(assessment, "assessment")
        
        print("\n✅ Learning journey complete!")
        print("In a full application, the system would track progress and suggest next steps.")

combined_btn.on_click(on_start_journey_click)

# Display combined experience widgets
display(widgets.VBox([combined_topic, combined_btn, output_combined]))

# Conclusion
display_section("Conclusion and Future Directions")

display(Markdown("""
## Summary

This demonstration showcases how generative AI can enhance language learning by providing:

- **Personalized content** tailored to individual learning needs and proficiency levels
- **Immediate feedback** on writing and language use
- **Unlimited practice opportunities** through quizzes and simulated conversations
- **Comprehensive learning journeys** that combine multiple educational approaches

## Future Enhancements

In a production system, we could extend this prototype with:

1. **User profiles and progress tracking** to create truly personalized learning paths
2. **Voice interaction** for pronunciation practice and speaking assessment
3. **More specialized modules** for academic writing, professional communication, test preparation, etc.
4. **Adaptive learning algorithms** to focus on areas where learners need the most help
5. **Community features** to connect learners for language exchange and practice

## Limitations and Ethical Considerations

It's important to acknowledge some limitations and ethical considerations:

- AI-generated content may occasionally contain errors or inaccuracies
- The system should complement human teachers rather than replace them
- Privacy concerns must be addressed when handling student data and writing samples
- Access to technology and AI tools should be made equitable across different populations

## Final Thoughts

This prototype demonstrates the potential of generative AI to democratize high-quality language education
and provide personalized learning experiences at scale. As language models continue to improve, these
systems will become increasingly effective tools for language acquisition.
"""))

print("\n✨ Demo notebook ready to run! Click the buttons above to test each functionality.")
