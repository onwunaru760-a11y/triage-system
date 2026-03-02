import streamlit as st
import numpy as np
from esi_rule_scoring import calculate_esi
from prev_bayesian_function import bayesian_esi
from agent_questions import generate_agent_questions


st.set_page_config(page_title='AI Triage System',
                   layout='centered')  # sets the basic configuration for the streamlit app and centers the page. the page_title appears in the browser tab
st.title("Dr. Toyin's Triage System")

# Initial patient information form
with st.form('Triage_form'):  # the with statement allows all inputs inside the with block are executed before streamlit runs to prevent rerunning for each input
    full_name = st.text_input('Full name')
    age = st.number_input('Age', min_value=0)  # so there are no negative values
    sex = st.selectbox('Sex', ['Male', 'Female'])
    complaint = st.selectbox("What's the problem?", ['Chest pain', 'Abdominal pain'])
    systolic_bp = st.number_input("Systolic BP(mmHg)")
    pulse = st.number_input("Pulse(BPM)")
    pain_score = st.slider("Pain score(0-10)", 0, 10)
    pain_description = st.selectbox("How does the pain feel like?", ['Sharp', 'Squeezing'])
    pregnant = st.selectbox("Pregnant?", ['Yes', 'No'])
    submitted = st.form_submit_button("Run Triage")

# Collect follow-up questions BEFORE form submission
pain_description_selected = pain_description  # Get current pain description selection
agent_questions = generate_agent_questions(pain_description_selected)

# Display follow-up questions outside the form
if agent_questions:
    st.header("Please answer the following questions:")
    answers = {}
    for q in agent_questions:
        selected_answer = st.radio(
            label=q,
            options=["No", "Yes"],
            key=q
        )  # streamlit reruns the full script after every interaction from the user so 'key' allows streamlit to remember what was previously selected
        answers[q] = selected_answer  # uses the questions as a key and the user's selected answer as a value
else:
    answers = {}

### Execution After Submitting ###

if submitted:
    # patient dict
    patient = {
        "full_name": full_name,
        "age": age,
        "sex": sex,
        "systolic_bp": systolic_bp,
        "pulse": pulse,
        "pain_score": pain_score,
        "pain_description": pain_description,
        "pregnant": pregnant,
    }

    initial_esi = calculate_esi(patient)


    ### Bayesian calculation ###

    new_esi, posterior_probs = bayesian_esi(patient, answers) #remember that the bayesian_esi function returns...
    # ...most_likely_esi and posterior so by unpacking them, new_esi equals most_likely_esi and posterior_probs equals answers
    st.subheader("Results")
    st.write("Initial ESI(Rule-based): ", initial_esi)
    for level, prob in zip([1,2,3,4,5], posterior_probs):
        st.write(f"ESI {level}: {round(prob*100, 2)}%")
    st.success(f"Most Likely ESI(Bayesian): {new_esi}")
    # Suggested Investigations
    if pain_description == "Sharp":
        st.write(
            "Worst Differentials: Pulmonary embolism, Pneumothorax, Pericarditis; Suggested Investigations: "
            "D-dimer, CT Pulmonary Angiography, Chest X-ray")
    elif pain_description == "Squeezing":
        st.write(
            "Worst Differentials: Myocardial infarction, Angina, Hypertrophic Cardiomyopathy; "
            "Suggested Investigations: ECG, Troponin I/T, Echocardiogram")


