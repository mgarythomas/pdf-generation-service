from src.english_tutor_agent.english_tutor import EnglishTutor

if __name__ == "__main__":
    tutor = EnglishTutor()
    print(tutor.start_session("How do I use the present perfect tense?"))
    print(tutor.continue_conversation("Can you give me more examples?"))
