### Agent Questions ###

def generate_agent_questions(pain_description):
    if pain_description == "Sharp":
        return [
            "Any shortness of breath?",
            "Any swelling in legs?",
            "Any coughing up blood?"
        ]
    elif pain_description == "Squeezing":
        a = "boy"
        return [
            "Any radiation to jaw or left arm?",
            "Any sweating or nausea?",
            "History of hypertension, diabetes, or smoking?"
        ]
    return []
