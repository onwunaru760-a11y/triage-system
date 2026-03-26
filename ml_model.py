import numpy as np
import pandas as pd
import pickle
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

MODEL_PATH = "ml_model.pkl"
N_SYNTHETIC = 600 #the number of fake training patients
RANDOM_STATE = 42

FEATURE_NAMES = [
"age", "sex_encoded", "pregnant_encoded",
"systolic_bp", "pulse", "spo2", "rr", "pain_score",
"pain_squeezing", "pain_sharp", "pain_tearing", "pain_burning", "pain_dull",
"onset_sudden",
"sob", "radiation", "diaphoresis", "nausea", "palpitations",
"pleuritic", "haemoptysis", "leg_swelling",
"tearing_char", "back_radiation",
"hypertension", "diabetes", "smoking", "prior_ami",
"sickle_cell", "hiv",
]

def _generate_synthetic_data(n = N_SYNTHETIC):
    """
    Generate synthetic patient records calibrated to Nigerian ED epidemiology.
    Calibration sources:
    - Nigerian age distribution: median presenting age lower than Western EDs
    - Higher hypertension prevalence (45% in adult Nigerians)
    - SCD burden: Nigeria has highest SCD population globally
    - Pain score distribution is adjusted for delayed presentation patterns
    - ESI distribution was obtained from Nigerian ED literature
    This is NOT a replacement for real data — it demonstrates the pipeline.
"""

    rng = np.random.RandomState(RANDOM_STATE) #rng stands for random number generator
    #ESI distribution calibrated to Nigerian EDs

    esi_probs = [0.06, 0.20, 0.32, 0.27, 0.15]
    esi_labels = rng.choice([1, 2, 3, 4, 5], size=n, p=esi_probs)

    records = []
    for esi in esi_labels:
        r = {}
        #Age -- Nigerian ED skews younger than Western
        if esi <= 2:
            r["age"] = int(rng.normal(58, 14))
        elif esi == 3:
            r["age"] = int(rng.normal(48, 16))
        else:
            r["age"] = int(rng.normal(38, 18))

        r["age"] = max(18, min(r["age"], 90))
        # This isolated line (above) maintains the age range between 18 and 90

        r["sex_encoded"] = int(rng.choice([0,1])) #0 = female, 1 = Male
        r["pregnant_encoded"] = int(r["sex_encoded"] == 0 and 18 <= r["age"] <= 45
                                    and rng.random() < 0.12)

        ##Vitals - calibrated to ESI level##

        # BP -- (bp means is the systolic blood pressure and bp_sds is the standard deviation of each
        bp_means = {1: 82, 2: 140, 3: 148, 4: 138, 5: 130}
        bp_sds = {1: 15, 2: 28, 3: 25, 4: 22, 5: 18}
        r["systolic_bp"] = int(rng.normal(bp_means[esi], bp_sds[esi]))
        r["systolic_bp"] = max(50, min(r["systolic_bp"], 240))

        #Pulse means --
        pulse_means = {1: 132, 2: 112, 3: 96, 4: 84, 5: 76}
        r["pulse"] = int(rng.normal(pulse_means[esi], 18))
        r["pulse"] = max(40, min(r["pulse"], 180))

        #SpO2 means --
        spo2_means = {1: 86, 2: 92, 3: 95, 4: 97, 5: 98}
        r["spo2"] = int(rng.normal(spo2_means[esi], 4))
        r["spo2"] = max(60, min(r["spo2"], 100))

        #Respiratory rate --
        rr_means = {1: 30, 2: 24, 3: 20, 4: 17, 5: 15}
        r["rr"] = int(rng.normal(rr_means[esi], 5))
        r["rr"] = max(8, min(r["rr"], 50))

        #Pain means --
        pain_means = {1: 8.5, 2: 7.8, 3: 6.2, 4: 4.5, 5: 2.8}
        r["pain_score"] = int(rng.normal(pain_means[esi], 1.5))
        r["pain_score"] = max(0, min(r["pain_score"], 10))

        #Pain character
        if esi <= 2:
            pain_type = rng.choice(["sq", "sh", "te", "bu", "du"],
                                   p=[0.45, 0.25, 0.15, 0.08, 0.07])
        else:
            pain_type = rng.choice(["sq", "sh", "te", "bu", "du"],
                                   p=[0.30, 0.28, 0.05, 0.22, 0.15])
        r["pain_squeezing"] = int(pain_type == "sq")
        r["pain_sharp"] = int(pain_type == "sh")
        r["pain_tearing"] = int(pain_type == "te")
        r["pain_burning"] = int(pain_type == "bu")
        r["pain_dull"] = int(pain_type == "du")

        r["onset_sudden"] = int(rng.random() < {1:0.55, 2:0.42, 3:0.28, 4:0.18, 5:0.12}[esi])

        #Symptoms - correlated with ESI and pain type (rng.random() < probability creates binary yes and and no answers)
        r["sob"] = int(rng.random() < {1: 0.75, 2: 0.52, 3: 0.30, 4: 0.14, 5: 0.05}[esi])
        r["radiation"] = int(rng.random() < ({1: 0.62, 2: 0.65, 3: 0.28, 4: 0.10, 5: 0.03}[esi]
            if pain_type == "sq" else 0.08))
        r["diaphoresis"] = int(rng.random() < {1:0.68, 2:0.58, 3:0.26, 4:0.10, 5:0.03}[esi])
        r["nausea"] = int(rng.random() < {1: 0.50, 2: 0.45, 3: 0.30, 4: 0.18, 5: 0.08}[esi])
        r["palpitations"] = int(rng.random() < {1: 0.40, 2: 0.38, 3: 0.28, 4: 0.18, 5: 0.08}[esi])
        r["pleuritic"] = int(rng.random() < (0.50 if pain_type == "sh" else 0.08))
        r["haemoptysis"] = int(rng.random() < (0.22 if pain_type == "sh" else 0.03))
        r["leg_swelling"] = int(rng.random() < (0.35 if pain_type == "sh" else 0.08))
        r["tearing_char"] = int(pain_type == "te")
        r["back_radiation"] = int(rng.random() < (0.55 if pain_type == "te" else 0.05))

        #Risk factors - Nigerian prevalence rates of comorbidities(randomly assigned)
        r["hypertension"] = int(rng.random() < 0.45)  # 45% adult prevalence Nigeria
        r["diabetes"] = int(rng.random() < 0.08)  # ~8% Nigeria
        r["smoking"] = int(rng.random() < 0.10)  # lower than Western
        r["prior_ami"] = int(rng.random() < {1: 0.28, 2: 0.22, 3: 0.12, 4: 0.06, 5: 0.03}[esi])
        r["sickle_cell"] = int(rng.random() < 0.025)  # ~2.5% Nigerian population
        r["hiv"] = int(rng.random() < 0.016)  # ~1.6% Nigeria prevalence
        r["esi"] = esi
        records.append(r)
    return pd.DataFrame(records)

def _build_feature_vector(patient, answers, risk_factors):
    """Convert the raw patient dict + answers into the ML feature vector."""
    pain_desc = patient.get("pain_description", "")
    return [
        patient.get("age", 40), #defaulting to 40 may lead to bias, recheck!
        1 if patient.get("sex") == "Male" else 0,
        1 if patient.get("pregnant") == "Yes" else 0,
        patient.get("systolic_bp", 120),
        patient.get("pulse", 80),

        patient.get("spo2", 98),
        patient.get("rr", 16),
        patient.get("pain_score", 5),
        int(pain_desc.startswith("Squeezing")),
        int(pain_desc.startswith("Sharp")),
        int(pain_desc.startswith("Tearing")),
        int(pain_desc.startswith("Burning")),
        int(pain_desc.startswith("Dull")),
        int(patient.get("onset") == "Sudden (<1 min)"),
        int(answers.get("Shortness of breath?") == "Yes"),
        int(answers.get("Pain radiating to jaw or left arm?") == "Yes"),
        int(answers.get("Sweating or feeling clammy?") == "Yes"),
        int(answers.get("Nausea or vomiting?") == "Yes"),
        int(answers.get("Any palpitations or irregular heartbeat?") == "Yes"),
        int(answers.get("Worse with deep breathing or coughing?") == "Yes"),
        int(answers.get("Any coughing up blood?") == "Yes"),
        int(answers.get("Any leg swelling, redness, or calf pain?") == "Yes"),
        int(pain_desc.startswith("Tearing")),
        int(answers.get("Does the pain radiate to the back or between shoulder blades?") == "Yes"),
        int(risk_factors.get("hypertension", False)),
        int(risk_factors.get("diabetes", False)),
        int(risk_factors.get("smoking", False)),
        int(risk_factors.get("prior_ami", False)),
        int(risk_factors.get("sickle_cell", False)),
        int(risk_factors.get("hiv", False)),

    ]
def train_or_load_model():
    """
    Load model from disk if it exists, else train on synthetic data.
    In production, retrain by running: python retrain_model.py
    """
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
            return model

    #Train on synthetic data
    df = _generate_synthetic_data(N_SYNTHETIC)
    X = df[FEATURE_NAMES].values
    y = df["esi"].values
    model = GradientBoostingClassifier(
        n_estimators=180,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        min_samples_leaf=8,
        random_state=RANDOM_STATE
    )
    model.fit(X, y)

    #Save to disk so it's not retrained on every run
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model

def predict_ml(patient, answers, risk_factors, model = None):
    """
    Run the ML model and return (predicted_esi, confidence, feature_importances).
    """
    if model is None:
        model = train_or_load_model()
    fv = _build_feature_vector(patient, answers, risk_factors)
    X = np.array(fv).reshape(1, -1)

    pred_esi = int(model.predict(X)[0]) #prediction line: this line returns the first and only prediction
    proba = model.predict_proba(X)[0] #probability output: returns probabilities for each class
    confidence = float(proba.max()) #confidence score: picks the highest prob and converts it to a float

    #This section shows how the score influenced the model overall
    #It goes to show that the model relies most on BP, age, and SpO2 when making decisions
    importances = model.feature_importances_
    feat_imp = {
        name: float(imp)
        for name, imp in sorted(
            zip(FEATURE_NAMES, importances),
            key=lambda x: x[1],
            reverse=True
        )
    }
    return pred_esi, confidence, feat_imp

def get_synthetic_cv_score():
    """Cross-validation score on synthetic data — shown in Model Card."""
    df = _generate_synthetic_data(N_SYNTHETIC)

    X = df[FEATURE_NAMES].values
    y = df["esi"].values

    model = GradientBoostingClassifier(
        n_estimators=180,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        min_samples_leaf=8,
        random_state=RANDOM_STATE
    )

    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    return scores.mean(), scores.std()
