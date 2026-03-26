import streamlit as st
from datetime import datetime
# Local modules
from database import init_db, save_assessment, get_record_count
from curr_bayesian_function import (
calculate_initial_esi, bayesian_esi,
generate_agent_questions, explain_top_drivers
)
from ml_model import train_or_load_model, predict_ml
from clinical_data import (
ESI_LABELS, ESI_ICONS, ESI_INSTRUCTIONS,
FACILITY_LEVELS,
get_investigations, get_worst_differentials,
get_monitoring_plan, get_nigerian_context_notes,
)
from utils import generate_patient_id


# App config

st.set_page_config(
page_title="Chest Pain Triage — Nigerian ED",
page_icon="■",
layout="wide",
initial_sidebar_state="expanded"
)

# CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+M
ono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
/* Dark mode colors */
[data-testid="stAppViewContainer"] { background-color: #000000; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #111111; }
.stMarkdown { color: #ffffff; }
.top-bar {
background: linear-gradient(120deg, #0D2B55 0%, #1565C0 100%);
color: white; padding: 1.4rem 2rem;
border-radius: 8px; margin-bottom: 1.4rem;
}
.top-bar h1 { margin:0; font-size:1.5rem; font-weight:700; letter-spacing:-0.3px; }
.top-bar p { margin:0.3rem 0 0; font-size:0.82rem; opacity:0.8; }
.esi-card {
padding: 1.4rem; border-radius: 8px;
text-align: center; margin-bottom: 1rem;
}
.esi-card .num { font-size:3rem; font-weight:700; margin:0; line-height:1; }
.esi-card .name { font-size:1.1rem; font-weight:600; margin:0.3rem 0 0; }
.esi-card .time { font-size:0.82rem; opacity:0.88; margin:0.2rem 0 0; }
.esi-1 { background:#B71C1C; color:white; }
.esi-2 { background:#E65100; color:white; }
.esi-3 { background:#F57F17; color:#1a1a1a; }
.esi-4 { background:#1565C0; color:white; }
.esi-5 { background:#2E7D32; color:white; }
.info-box {
background:#1e3a5f; border-left:4px solid #4a9eff;
padding:.8rem 1rem; border-radius:0 6px 6px 0; margin:.5rem 0; font-size:.9rem; color:#e0e0e0;
}
.warn-box {
background:#4a3a1a; border-left:4px solid #ffa500;
padding:.8rem 1rem; border-radius:0 6px 6px 0; margin:.5rem 0; font-size:.9rem; color:#ffc107;
}
.danger-box {
background:#5a1a1a; border-left:4px solid #ff4444;
padding:.8rem 1rem; border-radius:0 6px 6px 0; margin:.5rem 0; font-size:.9rem; color:#ff6b6b;
}
.success-box {
background:#1a4a2a; border-left:4px solid #4ade80;
padding:.8rem 1rem; border-radius:0 6px 6px 0; margin:.5rem 0; font-size:.9rem; color:#4ade80;
}
.section-label {
font-size:.72rem; font-weight:700; letter-spacing:1.8px;
text-transform:uppercase; color:#888888;
border-bottom:1px solid #333333;
padding-bottom:.3rem; margin:1.2rem 0 .6rem;
}
.model-card {
background:#1a1f2e; border:1px solid #333333;
border-radius:8px; padding:.9rem; margin:.4rem 0;
font-size:.85rem; color:#e0e0e0;
}
#MainMenu {visibility:hidden;} footer {visibility:hidden;} footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

#init
init_db()

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 1
if 'patient' not in st.session_state:
    st.session_state.patient = {}
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'risk' not in st.session_state:
    st.session_state.risk = {}
if 'bay_result' not in st.session_state:
    st.session_state.bay_result = None
if 'ml_result' not in st.session_state:
    st.session_state.ml_result = None
if 'pid' not in st.session_state:
    st.session_state.pid = generate_patient_id()

################ # Load ML model once at startup — cached so it doesn't retrain on every click
@st.cache_resource
def load_model():
    return train_or_load_model()
ml_model = load_model() #################

def reset():
    """New patient — wipe everything, generate fresh ID."""
    for k in ["stage", "patient", "answers", "risk", "bay_result", "ml_result","pid"]:
        if k in st.session_state:
            del st.session_state[k]
        defaults = {
            "stage": 1,
            "patient": {},
            "answers": {},
            "risk": {},
            "bay_result": None,
            "ml_result": None,
            "pid": generate_patient_id(),
        }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

#SIDEBAR

with st.sidebar:
    st.markdown("### ■ Triage System")
    st.caption("Nigerian Emergency Department")
    st.markdown("---")

    # New Patient — most important button, top of sidebar
    if st.button("■ New Patient", use_container_width=True):
        reset()
        st.rerun()
    st.markdown("___")

    # Facility level — drives investigation recommendations
    st.markdown("**Facility Level**")
    facility = st.selectbox(
    "facility",
    list(FACILITY_LEVELS.keys()),
    label_visibility="collapsed"
    )
    st.caption(FACILITY_LEVELS[facility]["description"])
    st.markdown("---")

    # Progress #Interested in seeing the output of this
    st.markdown("**Assessment Progress**")
    stage_names = {1: "Patient Info", 2: "Clinical Questions", 3: "Results"}
    for s, name in stage_names.items():
        if s < st.session_state.stage:
            st.markdown(f"■ {name}")
        elif s == st.session_state.stage:
            st.markdown(f"**{name}**")

    #Page navigation
    page = st.radio(
        "Navigate",
        ["■ Triage", "■ Analytics", "■ Model Card"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    record_count = get_record_count()
    st.metric("Assessments saved", record_count)
    if record_count < 200:
        st.caption(f"{200 - record_count} more needed to retrain ML on real data")
    else:
        st.caption("■ Enough data to retrain ML model on real outcomes")
        st.markdown("---")
        st.markdown(
            '<div style="font-size:.78rem;color:#9E9E9E;">'
            '■■ <b>Disclaimer:</b> Decision support only. '
            'Clinical responsibility remains with the attending clinician.<br><br>'
            '■ <b>Offline:</b> All data stored locally. No internet required.'
            '</div>',
            unsafe_allow_html=True
        )

#PAGE TRIAGE
if page == "■ Triage":
    st.markdown(
    f'<div class="top-bar">'
    f'<h1>■ Chest Pain Triage By Toyin(Using Bayesian Statistics)</h1>'
    f'<p>Nigerian Emergency Department &nbsp;|&nbsp; '
    f'Facility: <b>{facility}</b> &nbsp;|&nbsp; '
    f'Patient ID: <span class="pid">{st.session_state.pid}</span></p>'
    f'</div>',
    unsafe_allow_html=True
    )

    # ■■ STAGE 1: Demographics + Vitals
if st.session_state.stage == 1:
    st.markdown('<p class="section-label">Stage 1 of 3 — Patient Information & Vitals</p>',
    unsafe_allow_html=True)
    st.markdown(
    '<div class="info-box">'
    '■ <b>Privacy:</b> Do not enter the patient\'s name. '
    'Use the auto-generated ID above, or enter a hospital number. '
    'No personally identifiable information is collected.'
    '</div>', unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Demographics**")
        age = st.number_input("Age (years)", 0, 120, 45)
        sex = st.selectbox("Sex", ["Male", "Female"])
        pregnant = "No"
        if sex == "Female" and 12 <= age <= 55:
            pregnant = st.radio("Pregnant?", ["No", "Yes"], horizontal=True)
    with col2:
        st.markdown("**Vitals**")
        systolic_bp = st.number_input("Systolic BP (mmHg)", 40, 300, 130)
        pulse = st.number_input("Pulse (bpm)", 20, 250, 88)
        spo2 = st.number_input("SpO■ (%)", 50, 100, 97)
        rr = st.number_input("Respiratory Rate (breaths/min)", 4, 60, 18)

    st.markdown("**Presenting Complaint**")
    col3, col4 = st.columns(2)
    with col3:
        pain_score = st.slider("Pain Score (0–10)", 0, 10, 6)
        pain_desc = st.selectbox(
            "Pain Character",
            ["Squeezing / Pressure", "Sharp / Stabbing",
             "Tearing / Ripping", "Burning", "Dull / Aching"],
            help="Choose the character that best matches the patient's description"
        )
    with col4:
        onset = st.selectbox("Onset", ["Sudden (<1 min)", "Rapid (1–10 min)", "Gradual (>10 min)"])
        duration = st.selectbox("Duration", ["< 30 minutes", "30 min – 12 hours", "> 12 hours", "Ongoing"])

    # Live initial ESI
    temp = {"systolic_bp": systolic_bp, "pulse": pulse, "spo2": spo2,
            "rr": rr, "pain_score": pain_score}
    init_esi = calculate_initial_esi(temp)
    st.markdown("---")
    col5, col6 = st.columns([3, 1])
    with col5:
        box_class = "danger-box" if init_esi <= 2 else "warn-box" if init_esi == 3 else "info-box"
        st.markdown(
            f'<div class="{box_class}">'
            f'{ESI_ICONS[init_esi]} <b>Initial Rule-Based ESI: {init_esi} — '
            f'{ESI_LABELS[init_esi]["name"]}</b> ({ESI_LABELS[init_esi]["time"]}). '
            f'Bayesian model will refine this in Stage 2.'
            f'</div>', unsafe_allow_html=True
        )

    with col6:
        if st.button("Continue →", use_container_width=True, type="primary"):
            st.session_state.patient = {
                "patient_id": st.session_state.pid,
                "age": age,
                "sex": sex,
                "pregnant": pregnant,
                "systolic_bp": systolic_bp,
                "pulse": pulse,
                "spo2": spo2,
                "rr": rr,
                "pain_score": pain_score,
                "pain_description": pain_desc,
                "onset": onset,
                "duration": duration,
                "initial_esi": init_esi,
                "timestamp": datetime.now().isoformat(),
            }
            st.session_state.stage = 2
            st.rerun()


#STAGE 2: Clinical Questions
elif st.session_state.stage == 2:
    if not st.session_state.patient or 'age' not in st.session_state.patient:
        st.session_state.stage = 1
        st.rerun()
    else:
        p = st.session_state.patient
        st.markdown('<p class="section-label">Stage 2 of 3 — Targeted Clinical Questions</p>',
                    unsafe_allow_html=True)
        # Patient summary strip
        st.markdown(
            f'<div class="info-box">'
            f'<b>{p["age"]}y {p["sex"]}</b>'
            f'{" | Pregnant" if p.get("pregnant") == "Yes" else ""}'
            f' &nbsp;|&nbsp; BP <b>{p["systolic_bp"]} mmHg</b>'
            f' &nbsp;|&nbsp; Pulse <b>{p["pulse"]} bpm</b>'
            f' &nbsp;|&nbsp; SpO■ <b>{p["spo2"]}%</b>'
            f' &nbsp;|&nbsp; Pain <b>{p["pain_score"]}/10</b> ({p["pain_description"]})'
            f'</div>', unsafe_allow_html=True
        )


        questions = generate_agent_questions(p["pain_description"])
        answers = {}
        st.markdown("**Targeted Questions** *(based on pain character)*")
        col1, col2 = st.columns(2)
        for i, (q, tooltip) in enumerate(questions):
            answers[q] = st.radio(q, ["No", "Yes"],
            horizontal = True,
            key = f"q{i}",
            help = tooltip)
        st.markdown("**Risk Factors**")
        col3, col4, col5 = st.columns(3)
        with col3:
            htn = st.checkbox("Hypertension")
            dm = st.checkbox("Diabetes mellitus")
        with col4:
            smoking = st.checkbox("Smoking / tobacco use")
            prior_mi = st.checkbox("Previous MI or cardiac history")
        with col5:
            scd = st.checkbox("Sickle cell disease",
                              help="Nigeria has the world's highest SCD burden")
            hiv = st.checkbox("HIV / on ARV therapy",
                              help="HIV significantly alters cardiac risk profile")

        risk = {
            "hypertension": htn, "diabetes": dm, "smoking": smoking,
            "prior_ami": prior_mi, "sickle_cell": scd, "hiv": hiv,
        }
        st.markdown("---")
        col6, col7 = st.columns([1, 1])
        with col6:
            if st.button("← Back", use_container_width=True):
                st.session_state.stage = 1
                st.rerun()


        with col7:
            if st.button("Calculate Triage →", use_container_width=True, type="primary"):
                st.session_state.answers = answers

                st.session_state.risk = risk
                st.session_state.patient["risk_factors"] = risk

                # Running both models(the bayesian model and the ml model)

                bay_esi, posterior = bayesian_esi(p, answers, risk)
                #p is pt info, answers is clinical symptoms, risk is risk factors
                ml_esi, conf, importances = predict_ml(p, answers, risk, ml_model)
                st.session_state.bay_result = {
                "esi": bay_esi,
                "posterior": posterior.tolist(),
                } #tolist method makes it easy to store a numpy array

                st.session_state.ml_result = {
                    "esi": ml_esi,
                    "confidence": conf,
                    "importances": importances,
                }

                # Save immediately — before display, so power cuts don't lose it
                save_assessment(
                    patient=p,
                    answers=answers,
                    risk_factors=risk,
                    bayesian_esi_result=bay_esi,
                    ml_esi_result=ml_esi,
                    posterior=posterior.tolist(),
                    initial_esi=p["initial_esi"],
                    facility=facility,
                )
                st.session_state.stage = 3
                st.rerun()

    #STAGE 3: Results
elif st.session_state.stage == 3:
    # Validate all required session state exists
    if (not st.session_state.patient or 'age' not in st.session_state.patient or
        not st.session_state.bay_result or not st.session_state.ml_result or
        not st.session_state.answers or not st.session_state.risk):
        st.session_state.stage = 1
        st.rerun()
    else:
        p = st.session_state.patient
        bay = st.session_state.bay_result
        ml = st.session_state.ml_result
        ans = st.session_state.answers
        risk = st.session_state.risk

        bay_esi = bay["esi"]
        ml_esi = ml["esi"]
        st.markdown('<p class="section-label">Stage 3 of 3 — Triage Results</p>',
                    unsafe_allow_html=True)

        # ■■ Primary ESI result ■■
        col_main, col_detail = st.columns([1, 2])
        with col_main:
            st.markdown(
                f'<div class="esi-card esi-{bay_esi}">'
                f'<p class="num">{ESI_ICONS[bay_esi]} {bay_esi}</p>'
                f'<p class="name">{ESI_LABELS[bay_esi]["name"].upper()}</p>'
                f'<p class="time">{ESI_LABELS[bay_esi]["time"]}</p>'
                f'</div>', unsafe_allow_html=True
            )

        #Monitoring plan

        st.markdown("**Monitoring Plan**")
        for item in get_monitoring_plan(bay_esi, p):
            st.markdown(f"- {item}")
        with col_detail:
            st.markdown(f"**Clinical Action:** {ESI_INSTRUCTIONS[bay_esi]}")
            # Key drivers
            drivers = explain_top_drivers(p, ans, risk)
            st.markdown("**Key Features Driving This Classification:**")
            for d in drivers:
                st.markdown(f"- ■ {d}")
            st.markdown("---")
            # ■■ Model comparison ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            st.markdown('<p class="section-label">Model Comparison</p>', unsafe_allow_html=True)
            col_bay, col_ml = st.columns(2)
            with col_bay:
                st.markdown("#### ■ Bayesian Model")
                st.markdown(
                '<div class="model-card">'
                'Knowledge-driven. Encodes Nigerian ED epidemiology directly. '
                'Every probability is explainable. No training data required. '
                'Priors calibrated to Nigerian patient population.'
                '</div>', unsafe_allow_html=True
                )
                st.markdown("**Posterior Probability Distribution:**")
                for i, prob in enumerate(bay["posterior"], 1):
                    label = f"ESI {i} — {ESI_LABELS[i]['name']}"
                    st.markdown(f"<small>{label}</small>", unsafe_allow_html=True)
                    st.progress(float(prob), text=f"{round(prob*100, 1)}%")
            with col_ml:
                st.markdown("#### ■ ML Model (Gradient Boosting)")
                st.markdown(
                '<div class="model-card">'
                f'Data-driven. Trained on 600 synthetic Nigerian ED records. '
                f'Confidence: <b>{round(ml["confidence"]*100, 1)}%</b>. '
                f'When real outcome data accumulates in SQLite, '
                f'retrain with: <code>python retrain_model.py</code>'
                '</div>', unsafe_allow_html=True
                )
                agree = ml_esi == bay_esi
                if agree:
                    st.markdown(
                    f'<div class="success-box">■ <b>Models agree: ESI {ml_esi}</b></div>',
                    unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                    f'<div class="warn-box">■■ <b>Models disagree.</b> '
                    f'Bayesian: ESI {bay_esi} | ML: ESI {ml_esi}. '
                    f'Bayesian uses calibrated Nigerian priors — treat as primary. '
                    f'Disagreement signals clinical complexity; apply senior judgement.'
                    f'</div>', unsafe_allow_html=True
                    )
                st.markdown("**Feature Importance (top 6):**")
                importances = ml.get("importances", {})
                top6 = list(importances.items())[:6]
                if top6:
                    max_imp = top6[0][1] if top6 else 1.0
                    for feat, imp in top6:
                        display = feat.replace("_", " ").title()
                        normalised = imp / max_imp if max_imp > 0 else 0
                        st.markdown(f"<small>{display}</small>", unsafe_allow_html=True)
                        st.progress(float(normalised), text=f"{round(imp*100, 1)}%")
            st.markdown("---")
            # ■■ Differentials + Investigations ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            st.markdown('<p class="section-label">Clinical Differentials & Investigations</p>',
            unsafe_allow_html=True)
            col_diff, col_inv = st.columns(2)
            with col_diff:
                st.markdown("#### ■■ Worst-Case Differentials")
                st.caption("Ordered by: what must NOT be missed")
                diffs = get_worst_differentials(p["pain_description"], p)
                for i, dx in enumerate(diffs, 1):
                    st.markdown(f"**{i}. {dx['name']}**")
                    st.caption(dx["reason"])
            with col_inv:
                st.markdown(f"#### ■ Investigations")
                st.caption(f"Tiered for: {facility}")
                inv = get_investigations(p["pain_description"], facility)
                st.markdown("**Available at this facility:**")
                for item in inv["available"]:
                    st.markdown(f"- ■ {item}")
                if inv.get("unavailable"):
                    st.markdown("**Not typically available — refer if needed:**")
                    for item in inv["unavailable"]:
                        st.markdown(f"- ■■ {item}")
                if inv.get("refer_if"):
                    st.markdown(
                    f'<div class="warn-box">'
                    f'■ <b>Refer if:</b> {inv["refer_if"]}'
                    f'</div>', unsafe_allow_html=True
                    )
            st.markdown("---")
            # ■■ Nigerian context notes ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            st.markdown('<p class="section-label">Nigerian Clinical Context</p>',
            unsafe_allow_html=True)
            context_notes = get_nigerian_context_notes(p)
            for note in context_notes:
                box = "danger-box" if note["type"] == "warning" else "info-box"
                st.markdown(f'<div class="{box}">{note["text"]}</div>',
                unsafe_allow_html=True)
                st.markdown("---")
                # ■■ Disclaimer ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
                st.markdown(
                '<div class="warn-box">'
                '<b>■■ Clinical Responsibility:</b> This tool provides decision support only. '
                'Neither the Bayesian model nor the ML model has been validated on real '
                'Nigerian patient outcomes. Both are trained on synthetic or estimated data. '
                'The final triage decision rests entirely with the attending clinician.'
                '</div>', unsafe_allow_html=True
                )
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if st.button("■ New Patient", type="primary", use_container_width=True):
                        reset()
                        st.rerun()
                st.caption(
                f"Saved | ID: {p['patient_id']} | "
                f"Facility: {facility} | "
                f"{p['timestamp'][:19].replace('T', ' ')}"
                )
