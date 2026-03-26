import numpy as np

ESI_LEVELS = [1, 2, 3, 4, 5]
# ■■ Priors: estimated Nigerian ED chest pain ESI distribution ■■■■■■■■■■■■■■■■
# Source: Estimated from Nigerian ED literature + clinical experience
# To validate: compare against your real SQLite outcomes once collected
NIGERIAN_PRIORS = np.array([
0.06,
0.20,
0.32,
0.27,
0.15
])
# ■■ Likelihood ratios: P(evidence present | ESI level) ■■■■■■■■■■■■■■■■■■■■■■
# Each feature: how much more likely is this finding at each ESI level?

LIKELIHOODS = {

# ■■ Vital signs ■■
"shock_bp": {1: 0.85, 2: 0.20, 3: 0.06, 4: 0.02, 5: 0.01},
# Systolic < 90 → very strong ESI 1 signal
"hypertensive_bp": {1: 0.30, 2: 0.38, 3: 0.28, 4: 0.18, 5: 0.10},
# BP > 180 → raises ESI 1-2; hypertensive emergency common in Nigeria
"tachycardia": {1: 0.72, 2: 0.52, 3: 0.30, 4: 0.14, 5: 0.05},
"tachycardia_severe":{1: 0.85, 2: 0.35, 3: 0.10, 4: 0.03, 5: 0.01},
# HR > 130 → more acute than simple tachycardia
"low_spo2": {1: 0.78, 2: 0.48, 3: 0.22, 4: 0.08, 5: 0.02},
# SpO2 < 94% → significant; < 90% would be ESI 1 territory
"tachypnoea": {1: 0.65, 2: 0.42, 3: 0.22, 4: 0.09, 5: 0.02},
# RR > 20 — note: RR is often the earliest sign of deterioration
"severe_pain": {1: 0.50, 2: 0.58, 3: 0.32, 4: 0.10, 5: 0.02},
"moderate_pain": {1: 0.18, 2: 0.28, 3: 0.58, 4: 0.38, 5: 0.12},

# ■■ Demographics ■■
"elderly": {1: 0.25, 2: 0.38, 3: 0.42, 4: 0.30, 5: 0.20},
# Age ≥ 65 — atypical presentations more common; less physiological reserve
"young_adult": {1: 0.12, 2: 0.18, 3: 0.24, 4: 0.36, 5: 0.46},
# Age < 35 — lower cardiac risk overall; consider SCD, cocaine, RHD
"pregnant": {1: 0.42, 2: 0.48, 3: 0.28, 4: 0.12, 5: 0.04},
# Pregnancy: PE, peripartum cardiomyopathy, aortic dissection all elevated

# ■■ Cardiac symptom pattern ■■
"radiation": {1: 0.58, 2: 0.62, 3: 0.26, 4: 0.09, 5: 0.03},
# Radiation to jaw/left arm — Levine sign; strongly suggests ischaemia
"diaphoresis": {1: 0.62, 2: 0.55, 3: 0.24, 4: 0.08, 5: 0.02},
# Sweating — autonomic response; common in ACS and massive PE
"nausea": {1: 0.45, 2: 0.42, 3: 0.28, 4: 0.15, 5: 0.08},
"sob": {1: 0.68, 2: 0.48, 3: 0.28, 4: 0.12, 5: 0.03},
"palpitations": {1: 0.40, 2: 0.45, 3: 0.30, 4: 0.20, 5: 0.10},
"exertional": {1: 0.35, 2: 0.48, 3: 0.38, 4: 0.20, 5: 0.08},
"sudden_onset": {1: 0.48, 2: 0.42, 3: 0.26, 4: 0.16, 5: 0.10},

# ■■ Pleuritic/PE pattern ■■
"pleuritic": {1: 0.28, 2: 0.38, 3: 0.32, 4: 0.22, 5: 0.15},
"haemoptysis": {1: 0.45, 2: 0.42, 3: 0.22, 4: 0.08, 5: 0.02},
"leg_swelling": {1: 0.38, 2: 0.38, 3: 0.22, 4: 0.12, 5: 0.05},
"immobility": {1: 0.30, 2: 0.35, 3: 0.28, 4: 0.18, 5: 0.10},

# ■■ Aortic dissection pattern ■■
"tearing_character": {1: 0.72, 2: 0.42, 3: 0.15, 4: 0.05, 5: 0.02},
# Tearing/ripping = red flag for dissection; strong ESI 1 signal
"back_radiation": {1: 0.55, 2: 0.38, 3: 0.18, 4: 0.08, 5: 0.03},
"instant_max_pain": {1: 0.62, 2: 0.38, 3: 0.18, 4: 0.08, 5: 0.03},

# ■■ Standard risk factors ■■
"hypertension": {1: 0.32, 2: 0.42, 3: 0.46, 4: 0.36, 5: 0.26},
"diabetes": {1: 0.28, 2: 0.38, 3: 0.42, 4: 0.32, 5: 0.22},
"smoking": {1: 0.22, 2: 0.30, 3: 0.36, 4: 0.28, 5: 0.20},
"prior_ami": {1: 0.42, 2: 0.52, 3: 0.36, 4: 0.22, 5: 0.10},

# ■■ Nigerian-specific features (not in any Western ESI tool) ■■
"sickle_cell": {1: 0.38, 2: 0.48, 3: 0.32, 4: 0.14, 5: 0.04},
# Acute chest syndrome (ESI 1-2) or vaso-occlusive crisis (ESI 2-3)
# Nigeria has one of the world's highest SCD burdens
"hiv_arv": {1: 0.22, 2: 0.32, 3: 0.32, 4: 0.22, 5: 0.14},
# HIV: pericarditis, pulmonary HTN, accelerated atherosclerosis on ARVs
"young_squeezing": {1: 0.28, 2: 0.38, 3: 0.32, 4: 0.20, 5: 0.10},
# Young patient + squeezing pain → consider RHD (higher prevalence in Nigeria)
}

def calculate_initial_esi(patient):
    """
    Fast rule-based ESI — deterministic, used as first-pass display.
    The Bayesian ESI is never lower than this result (safety floor).
    """
    bp = patient.get("systolic_bp", 120)
    pain = patient.get("pain_score", 0)
    pulse = patient.get("pulse", 80)
    spo2 = patient.get("spo2", 98)
    rr = patient.get("rr", 16)

    # ESI 1 — immediate life threat
    if bp < 80 or spo2 < 85 or pulse > 150:
        return 1
    # ESI 2 — emergent
    if bp < 90 or bp > 200 or pain >= 9 or pulse > 120 or spo2 < 92 or rr > 28:
        return 2

    # ESI 3 — urgent
    if pain >= 6 or pulse > 100 or spo2 < 95 or rr > 22:
        return 3
    # ESI 4 — less urgent
    if pain >= 3:
        return 4
    return 5

def generate_agent_questions(pain_description):
    """
    Targeted clinical questions based on pain character.
    Returns list of (question, tooltip) pairs.
    Tooltips explain the clinical reasoning — good for training juniors too.
    """

    base = [
    ("Shortness of breath?",
     "Dyspnoea raises suspicion for PE, pneumothorax, pulmonary oedema"),
    ("Sweating or feeling clammy?",
     "Diaphoresis is an autonomic response common in ACS and massive PE"),
    ("Nausea or vomiting?",
     "Vagal symptoms occur in inferior MI and other high-acuity events"),
    ]
    squeezing = [
    ("Pain radiating to jaw or left arm?",
     "Classic radiation pattern of myocardial ischaemia (Levine's sign)"),
    ("Worse with exertion, better with rest?",
     "Exertional component strongly suggests ischaemic aetiology"),
    ("Any palpitations or irregular heartbeat?",
     "Arrhythmia may be secondary to ischaemia or electrolyte disturbance"),
    ]
    sharp = [
    ("Worse with deep breathing or coughing?",
    "Pleuritic pain suggests PE, pericarditis, pleuritis, or pneumothorax"),
    ("Any coughing up blood?",
    "Haemoptysis is a red flag for PE, TB, or malignancy"),
    ("Any recent long travel or prolonged sitting (>4 hours)?",
    "Immobility is a major PE risk factor"),
    ("Any leg swelling, redness, or calf pain?",
    "DVT symptoms support PE diagnosis — legs are the source in most cases"),
    ]
    tearing = [
    ("Did pain reach maximum severity instantly?",
    "Instantaneous maximal pain is characteristic of aortic dissection"),
    ("Does the pain radiate to the back or between shoulder blades?",
    "Back radiation suggests aortic dissection — a surgical emergency"),
    ("Any difference in pulse or BP between arms?",
    "Pulse deficit is a sign of type A aortic dissection"),
    ]
    burning = [
    ("Related to meals, or worse lying down?",
    "Positional and postprandial symptoms suggest oesophageal origin"),
    ("Any acid taste or belching?",
    "GORD is the most common cardiac mimic in Nigerian primary care"),
    ("Relieved by antacids?",
    "Response to antacids strongly suggests GI rather than cardiac cause"),
    ]
    dull = [
    ("Pain radiating to jaw or left arm?",
    "Dull pain with radiation — consider atypical ACS, common in diabetics"),
    ("Any history of similar episodes?",
    "Recurrent dull chest pain in a risk-factor patient warrants cardiac workup"),
    ("Worse with exertion?",
    "Exertional dull pain — consider stable/unstable angina"),
    ]

    question_map = {
        "Squeezing / Pressure": squeezing,
        "Sharp / Stabbing": sharp,
        "Tearing / Ripping": tearing,
        "Burning": burning,
        "Dull / Aching": dull,
    }

    specific = question_map.get(pain_description, squeezing)
    return base + specific

def bayesian_esi(patient, answers, risk_factors):
    """
    Full Bayesian ESI update.
    Process:
    1. Start with Nigerian-calibrated priors
    2. Build evidence from vitals, answers, risk factors
    3. Multiply posterior by each likelihood ratio
    4. Normalise — sum must equal 1.0
    5. Return most probable ESI and full posterior
    Interpretability: we can explain every number.
    'ESI 2 has 48% probability because: tachycardia (LR 0.52),
    radiation present (LR 0.62), diaphoresis present (LR 0.55)...'
    """
    pain_desc = patient.get("pain_description", "")
    age = patient.get("age", 40)

    evidence = {
        # Vitals
        "shock_bp": patient["systolic_bp"] < 90,
        "hypertensive_bp": patient["systolic_bp"] > 180,
        "tachycardia": 100 < patient["pulse"] <= 130,
        "tachycardia_severe": patient["pulse"] > 130,
        "low_spo2": patient["spo2"] < 94,
        "tachypnoea": patient["rr"] > 20,
        "severe_pain": patient["pain_score"] >= 8,
        "moderate_pain": 5 <= patient["pain_score"] <= 7,
        # Demographics
        "elderly": age >= 65,
        "young_adult": age < 35,
        "pregnant": patient.get("pregnant") == "Yes",
        # Cardiac symptoms
        "radiation": answers.get("Pain radiating to jaw or left arm?") == "Yes",
        "diaphoresis": answers.get("Sweating or feeling clammy?") == "Yes",
        "nausea": answers.get("Nausea or vomiting?") == "Yes",
        "sob": answers.get("Shortness of breath?") == "Yes",
        "palpitations": answers.get("Any palpitations or irregular heartbeat?") == "Yes",
        "sudden_onset": patient.get("onset") == "Sudden (<1 min)",
        # Pleuritic / PE
        "pleuritic": answers.get("Worse with deep breathing or coughing?") == "Yes",
        "haemoptysis": answers.get("Any coughing up blood?") == "Yes",
        "leg_swelling": answers.get("Any leg swelling, redness, or calf pain?") == "Yes",
        "immobility": answers.get("Any recent long travel or prolonged sitting (>4 hours)?") == "Yes",
        # Dissection
        "tearing_character": pain_desc.startswith("Tearing"),
        "back_radiation": answers.get("Does the pain radiate to the back or between shoulder blades?") == "Yes",
        "instant_max_pain": answers.get("Did pain reach maximum severity instantly?") == "Yes",
        # Risk factors
        "hypertension": risk_factors.get("hypertension", False),
        "diabetes": risk_factors.get("diabetes", False),
        "smoking": risk_factors.get("smoking", False),
        "prior_ami": risk_factors.get("prior_ami", False),
        # Nigerian-specific
        "sickle_cell": risk_factors.get("sickle_cell", False),
        "hiv_arv": risk_factors.get("hiv", False),
        "young_squeezing": (age < 40 and pain_desc.startswith("Squeezing")),
    }
#### Tackle the pain_desc problem later ###
    posterior = np.copy(NIGERIAN_PRIORS)
    for feature, present in evidence.items():
        lk = LIKELIHOODS.get(feature)
        if lk is None:
            continue

    for i, esi in enumerate(ESI_LEVELS):
        p = lk[esi]
        posterior[i] *= (p if present else 1.0 - p)
        # Re-normalise frequently to prevent underflow
        s = posterior.sum()
        if s > 0:
            posterior /= s

    #Final normalize
    total = posterior.sum()
    posterior = posterior / total if total > 0 else np.copy(NIGERIAN_PRIORS)
    best_esi = ESI_LEVELS[int(np.argmax(posterior))]

    # Safety floor — so it never downgrades from rule-based ESI 1
    if calculate_initial_esi(patient) == 1:
        best_esi = 1
    return best_esi, posterior

def explain_top_drivers(patient, answers, risk_factors, top_n = 5):
    """
    Return the top features driving the Bayesian result.
    Used in the results UI to explain the model's reasoning.
    Shows which evidence changed the posterior most from the prior.
    """
    drivers = []
    pain_desc = patient.get("pain_description", "")
    age = patient.get("age", 40)
    evidence = {
        "Shock BP (< 90 mmHg)": patient["systolic_bp"] < 90,
        "Hypertensive BP (> 180 mmHg)": patient["systolic_bp"] > 180,
        "Tachycardia (> 100 bpm)": patient["pulse"] > 100,
        "Severe tachycardia (> 130)": patient["pulse"] > 130,
        "Low SpO■ (< 94%)": patient["spo2"] < 94,
        "Tachypnoea (RR > 20)": patient["rr"] > 20,
        "Severe pain (≥ 8/10)": patient["pain_score"] >= 8,
        "Radiation to jaw / arm": answers.get("Pain radiating to jaw or left arm?") == "Yes",
        "Diaphoresis": answers.get("Sweating or feeling clammy?") == "Yes",
        "Shortness of breath": answers.get("Shortness of breath?") == "Yes",
        "Pleuritic pain character": answers.get("Worse with deep breathing or coughing?") == "Yes",
        "Haemoptysis": answers.get("Any coughing up blood?") == "Yes",
        "Tearing pain character": pain_desc.startswith("Tearing"),
        "Sickle cell disease": risk_factors.get("sickle_cell", False),
        "Prior MI / cardiac history": risk_factors.get("prior_ami", False),
        "Pregnant": patient.get("pregnant") == "Yes",
        "Age ≥ 65": age >= 65,
    }

    for name, present in evidence.items():
        if present:
            drivers.append(name)
        if len(drivers) >= top_n:
            break
        return drivers if drivers else ["No high-acuity features identified"]









