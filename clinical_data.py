"""
clinical_data.py
----------------
All Nigerian-specific clinical reference data.
This is where your medical knowledge lives as structured data.
Facility-level investigation tiering (Document 2, Section 5):
- Different care levels have different equipment availability
- Investigations are tiered: available vs. refer-if-needed
- This is the single feature that most shows Nigerian clinical insider knowledge
"""
# ■■ ESI display data ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
ESI_LABELS = {
1: {"name": "Resuscitation", "time": "Immediate — do not leave patient", "color": "#B71C1C"},
2: {"name": "Emergent", "time": "Seen within 15 minutes", "color": "#E65100"},
3: {"name": "Urgent", "time": "Seen within 30 minutes", "color": "#F57F17"},
4: {"name": "Less Urgent", "time": "Seen within 1 hour", "color": "#1565C0"},
5: {"name": "Non-Urgent", "time": "Routine assessment", "color": "#2E7D32"},
}
ESI_ICONS = {1: "■", 2: "■", 3: "■", 4: "■", 5: "■"}
ESI_INSTRUCTIONS = {
1: "IMMEDIATE life-saving intervention required. Two large-bore IV cannulas, "
"continuous monitoring, oxygen, senior clinician to bedside NOW.",
2: "Patient must be seen by a doctor within 15 minutes. "
"Continuous monitoring. IV access. Do not give analgesia that masks clinical picture.",
3: "Seen within 30 minutes. Vitals every 15 min. "
"Escalate immediately if any deterioration. May require investigations before senior review.",
4: "Reassess within 1 hour. Patient to alert staff if symptoms change. "
"Simple investigations may be needed.",
5: "Routine assessment. Reassess if symptoms worsen. "
"Consider discharge with safety netting advice.",
}
# ■■ Facility levels with equipment profiles ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Based on Nigerian health system reality (Document 2, Section 5)
FACILITY_LEVELS = {
"Primary Health Centre (PHC)": {
"description": "Community level. Basic vitals only. No imaging.",
"equipment": ["BP cuff", "thermometer", "pulse oximeter",
"glucometer", "malaria RDT", "urine dipstick"]
},
"Secondary Hospital": {
"description": "District level. Basic labs and X-ray usually available.",
"equipment": ["All PHC equipment", "ECG", "plain X-ray",
"FBC", "basic biochemistry", "basic ultrasound (usually)"]
},
"Tertiary / Teaching Hospital": {
"description": "Specialist centre. Most investigations available.",
"equipment": ["All secondary equipment", "troponin", "D-dimer",
"echocardiography", "CT (where functioning)",
"specialist consultation"]
},
}

# ■■ Investigation tiering by facility level and pain type ■■■■■■■■■■■■■■■■■■■■
# This is the most clinically important feature in the whole system.
# A tool that recommends CT to a PHC is useless. A tool that gives
# the right alternative at each level is genuinely valuable.
INVESTIGATIONS = {
"Squeezing / Pressure": {
"Primary Health Centre (PHC)": {
"available": [
"12-lead ECG (if machine present)",
"Blood glucose (glucometer)",
"Blood pressure both arms (check for asymmetry)",
"SpO■ monitoring",
"Aspirin 300mg stat if ACS suspected and no contraindication",
"Sublingual GTN (if available, BP > 100 systolic)",
],
"unavailable": [
"Troponin I/T — refer to secondary/tertiary for this",
"Echocardiogram — tertiary only",
"Cardiac catheterisation — major tertiary centres only",
],
"refer_if": "ESI 1-2, suspected STEMI on ECG, haemodynamic instability, cardiogenic shock, severe LVF",
},
"Tertiary / Teaching Hospital": {
"available": [
"12-lead ECG — immediate",
"Troponin I/T (serial: 0h and 3h)",
"FBC, U&E, creatinine, glucose, LFTs, lipid profile",
"CXR",
"Echocardiography",
"Continuous cardiac monitoring",
"Aspirin 300mg + clopidogrel / ticagrelor",
"Consider thrombolysis if STEMI + PCI not available within 120 min",
],
"unavailable": [],
"refer_if": "None — manage here",
},
},

"Sharp / Stabbing": {
"Primary Health Centre (PHC)": {
"available": [
"SpO■ — PE or pneumothorax may drop oxygen",
"Respiratory rate and pattern",
"Tracheal position (pneumothorax screening)",
"Blood pressure and pulse",
"Look for DVT signs (swollen, red, warm leg)",
"Temperature (exclude pneumonia, pleuritis)",
],
"unavailable": [
"D-dimer — secondary/tertiary only",
"CT Pulmonary Angiography — tertiary only",
"Chest X-ray — refer to secondary if needed urgently",
],
"refer_if": "SpO■ < 94%, suspected PE, suspected pneumothorax, haemoptysis",
},
"Secondary Hospital": {
"available": [
"CXR — pneumothorax, pneumonia, pleural effusion",
"ECG — PE may show S1Q3T3, right heart strain",
"FBC — WBC for infection; Hb for anaemia",
"D-dimer (if available — good negative predictive value)",
"SpO■ monitoring",
"Blood cultures if febrile",
"Sputum AFB if TB suspected (Nigeria has high TB burden)",
],
"unavailable": [
"CTPA — usually tertiary only; request urgent transfer if PE likely",
"V/Q scan — specialist centres",
],
"refer_if": "Suspected PE with haemodynamic compromise, "
"tension pneumothorax (needle decompression first then transfer)",
},
"Tertiary / Teaching Hospital": {
"available": [
"CT Pulmonary Angiography (CTPA) — gold standard for PE",
"D-dimer",
"CXR",
"ABG — assess oxygenation, A-a gradient",
"ECG",
"FBC, coagulation screen (PT/APTT)",
"Lower limb Doppler USS",
"Echo — right heart strain in massive PE",
"Blood cultures + sputum if infection suspected",
"Sputum AFB × 3 if TB suspected",
],
"unavailable": [],
"refer_if": "None — manage here",
},
},
"Tearing/Ripping": {
"Primary Health Centre (PHC)": {
"available": [
"BP BOTH arms — asymmetry > 20 mmHg is red flag",
"Pulse assessment both arms",
"SpO2",
"IV access if available",
"Analgesia (morphine if available)",
"■■ DO NOT give thrombolytics — fatal in dissection",
],
"unavailable": [
"CT Aortogram — tertiary only; this is the diagnostic scan needed",
"Urgent surgical review — tertiary/cardiac surgery only",
],
"refer_if": "ALL tearing chest pain — this is a surgical emergency. "
"Transfer IMMEDIATELY with IV access and analgesia.",
},
"Secondary Hospital": {
"available": [
"CXR — widened mediastinum (> 8cm), aortic knuckle abnormality",
"BP both arms",
"ECG — exclude MI (dissection can occlude coronary ostia)",
"FBC, U&E, group and save",
"SpO■ monitoring",
"IV access, fluid resuscitation if hypotensive",
"Analgesia",
"■■ DO NOT give thrombolytics",
],
"unavailable": [
"CT Aortogram — arrange urgent transfer to tertiary",
"Cardiothoracic surgery — tertiary only",
],
"refer_if": "All confirmed/suspected dissections — urgent cardiothoracic referral",
},
"Tertiary / Teaching Hospital": {
"available": [
"CT Aortogram (chest/abdomen/pelvis) — URGENT",
"CXR",
"ECG",
"FBC, U&E, LFTs, coagulation, group and crossmatch",
"Transoesophageal echocardiogram if CT unavailable",
"Cardiothoracic surgical consultation — IMMEDIATE",
"BP control: IV labetalol or esmolol (target SBP 100-120 mmHg)",
"Strict pain management: IV morphine",
],
"unavailable": [],
"refer_if": "None — manage here with cardiothoracic surgery",
},
},
"Burning": {
"Primary Health Centre (PHC)": {
"available": [
"Therapeutic trial: antacid (if available) — relief suggests GI cause",
"Blood pressure and pulse",
"Blood glucose",
"SpO2",
"ECG if machine available — exclude MI mimicking GI pain",
],
"unavailable": [
"Upper GI endoscopy — secondary/tertiary only",
"Helicobacter pylori testing — secondary/tertiary",
],
"refer_if": "No antacid response, pain > 6/10, abnormal vitals, age > 50",
},
"Secondary Hospital": {
"available": [
"ECG — always exclude cardiac cause in burning chest pain",
"FBC — check for anaemia (PUD complication)",
"H. pylori stool antigen or urease breath test",
"Barium swallow if endoscopy not available",
"Antacid and PPI trial",
],
"unavailable": [
"Upper GI endoscopy — may not be available; refer to tertiary if needed",
],
"refer_if": "Haematemesis, melaena, weight loss, dysphagia",
},
"Tertiary / Teaching Hospital": {
"available": [
"Upper GI endoscopy — definitive diagnosis",
"H. pylori testing (CLO test at endoscopy)",
"ECG — exclude cardiac",
"24-hour oesophageal pH monitoring if GORD suspected",
"CT abdomen if malignancy considered",
"FBC, LFTs, H. pylori eradication therapy",
],
"unavailable": [],
"refer_if": "None",
},
},
"Dull / Aching": {
"Primary Health Centre (PHC)": {
"available": [
"ECG if machine available — atypical ACS common in diabetics",
"Blood glucose — exclude hypoglycaemia",
"Blood pressure",
"SpO■",
],
"unavailable": [
"Troponin — refer if cardiac cause suspected",
"Echocardiography — tertiary",
],
"refer_if": "Diabetic patient + dull chest pain (silent MI common), "
"any haemodynamic instability",
},
"Secondary Hospital": {
"available": [
"ECG",
"FBC, U&E, glucose",
"Troponin if available",
"CXR",
"Cardiac monitoring if troponin elevated",
],
"unavailable": [
"Echo, stress testing — tertiary",
],
"refer_if": "Troponin positive, ECG changes, high clinical suspicion ACS",
},
"Tertiary / Teaching Hospital": {
"available": [
"ECG",
"Troponin (serial)",
"Echocardiography",
"Stress ECG or stress echo if stable",
"FBC, metabolic panel, lipids",
"CXR",
],
"unavailable": [],
"refer_if": "None",
},
},
}


def get_investigations(pain_description, facility):
    """Return the investigation object for a given pain type and facility."""
    pain_data = INVESTIGATIONS.get(pain_description, INVESTIGATIONS["Dull / Aching"])
    return pain_data.get(facility, pain_data.get("Primary Health Centre (PHC)", {}))

# ■■ Worst-case differentials by pain type ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Ordered by: how dangerous is it if missed?
DIFFERENTIALS = {
"Squeezing / Pressure": [
{"name": "STEMI / NSTEMI", "reason": "Must exclude first — time-critical"},
{"name": "Unstable angina", "reason": "ACS spectrum — same workup as MI"},
{"name": "Aortic dissection", "reason": "Squeezing + severe hypertension = red flag"},
{"name": "Acute pulmonary oedema", "reason": "Cardiac failure can present as chest tightness"},
{"name": "Sickle cell acute chest", "reason": "Nigeria-specific — always ask in young patients as its the most dangerous SCD complication"},
{"name": "Peripartum cardiomyopathy", "reason": "Pregnant / postpartum women with cardiac symptoms"},
{"name": "Hypertrophic cardiomyopathy", "reason": "Young Nigerian with squeezing pain + exertion"},
],
"Sharp / Stabbing": [
{"name": "Pulmonary embolism", "reason": "Do not miss — high mortality if untreated"},
{"name": "Tension pneumothorax", "reason": "Life-threatening — immediate needle decompression"},
{"name": "Pericarditis", "reason": "Worse lying flat, better leaning forward"},
{"name": "Pneumothorax", "reason": "Young thin males especially"},
{"name": "Pulmonary tuberculosis", "reason": "High prevalence Nigeria — especially with haemoptysis"},
{"name": "Pleuritis / Pleurisy", "reason": "Viral or bacterial — exclude PE first"},
{"name": "Musculoskeletal", "reason": "Diagnosis of exclusion — only after cardiac causes excluded"},
],
"Tearing / Ripping": [
{"name": "Aortic dissection (Type A)", "reason": "Surgical emergency — mortality 1-2% per hour untreated"},
{"name": "Aortic dissection (Type B)", "reason": "Medical management — BP control essential"},
{"name": "Oesophageal rupture", "reason": "Rare but highly lethal — after forceful vomiting"},
{"name": "Traumatic aortic injury", "reason": "If any trauma history"},
],
"Burning": [
{"name": "Acute MI (inferior)", "reason": "Always exclude — inferior MI mimics GI pain perfectly"},
{"name": "GORD / Oesophagitis", "reason": "Most common cause of burning chest pain"},
{"name": "Peptic ulcer disease", "reason": "H. pylori prevalence very high in Nigeria"},
{"name": "Oesophageal spasm", "reason": "Can mimic ACS — responds to nitrates (misleading)"},
{"name": "Hiatus hernia", "reason": "Positional symptoms, worse postprandially"},
],
"Dull / Aching": [
{"name": "Silent MI (atypical ACS)", "reason": "Common in diabetics — dull ache only, no classic pain"},
{"name": "Stable / Unstable angina", "reason": "Exertional dull ache — needs risk stratification"},
{"name": "Pericarditis", "reason": "Can be dull rather than sharp"},
{"name": "Musculoskeletal", "reason": "Diagnosis of exclusion"},
{"name": "Anaemia-related", "reason": "Severe anaemia causes chest discomfort — check Hb"},
],
}

def get_worst_differentials(pain_description, patient=None):
    """
    Return differentials for a given pain type.
    Patient context allows adding Nigerian-specific differentials dynamically. So
    the worst differentials in this case is patient-specific
    """
    diffs = DIFFERENTIALS.get(pain_description, DIFFERENTIALS["Dull / Aching"]).copy()
    #copy creates a new list instance(preserving the master knowledge base)

    #Now i want to add the patient specific details
    if patient:
        risk = patient.get("risk_factors", {})
        age = patient.get("age", [])#this empty list default should be changed later
        if risk.get("sickle_cell") and not any(d["name"] == "Sickle cell acute chest" for d in diffs):
            diffs.insert(1, {
                "name": "Sickle cell acute chest syndrome",
                "reason": "Patient has SCD — this is the most dangerous SCD chest complication"
            })
        if risk.get("hiv"):
            diffs.append({
                "name": "HIV-related pericarditis / cardiomyopathy",
                "reason": "HIV patients have elevated risk of pericarditis and dilated cardiomyopathy"
            })
        if age < 35 and pain_description.startswith("Squeezing"):
            diffs.append({
                "name": "Rheumatic heart disease",
                "reason": "Young Nigerian + cardiac pain — RHD more prevalent than Western populations"
            })
        return diffs
def get_monitoring_plan(esi_level, patient):
    """Return a monitoring plan appropriate to the ESI level."""
    spo2 = patient.get("spo2", 98)
    bp = patient.get("systolic_bp", 120)
    plans = {
        1: [
            "■ Continuous cardiac monitoring — immediately",
            "■ Continuous pulse oximetry",
            "■ BP every 5 minutes",
            "■ Two large-bore IV cannulas — immediately",
            "■ Oxygen — target SpO■ > 94%",
            "■ Senior clinician to bedside — do not leave patient unattended",
        ],
        2: [
            "Continuous cardiac monitoring",
            "Pulse oximetry — continuous",
            "BP and pulse every 15 minutes",
            "IV access within 10 minutes",
            "Reassess in 15 minutes",
            "Escalate immediately if any deterioration",
        ],
        3: [
            "BP and pulse every 30 minutes",
            "Pulse oximetry every 30 minutes",
            "Reassess within 30 minutes",
            "Escalate if pain increases or vitals deteriorate",
        ],
        4: [
            "Reassess within 1 hour",
            "Vitals on arrival and on reassessment",
            "Patient to alert staff if symptoms change",
        ],
        5: [
            "Routine reassessment",
            "Patient to alert staff if symptoms worsen",
        ],
    }

    plan = plans.get(esi_level, plans[3]).copy()
    if spo2 < 94:
        plan.insert(0, f"SpO2 {spo2}% — oxygen supplementation REQUIRED now")
    if bp < 90:
        plan.insert(0, f"SBP {bp} mmHg — IV fluid resuscitation required")
    if bp > 180:
        plan.insert(0, f" SBP {bp} mmHg — urgent BP control needed")
    return plan

#come back to this fuction later and ascertain if it should still stay
#if it's staying, edit the note context
def get_nigerian_context_notes(patient):
    """
    Generate Nigerian-specific clinical context alerts.
    This function encodes clinical insider knowledge that no
    developer from outside Nigeria would think to include.
    """
    notes = []
    risk = patient.get("risk_factors", {})
    age = patient.get("age", "")
    pain = patient.get("pain_description", "")

    if risk.get("sickle_cell"):
        notes.append({
            "type": "warning",
            "text":  "<b>Sickle Cell Disease:</b> Acute chest syndrome is the "
    "most dangerous SCD pulmonary complication and a leading cause of "
    "SCD death. Do not be reassured by young age. Give oxygen, IV hydration, "
    "analgesia. Urgent haematology review. Exchange transfusion may be needed."

        })

    if age < 40 and pain.startswith("Squeezing"):
        notes.append({
            "type": "info",
            "text": "■ <b>Young Nigerian patient + squeezing pain:</b> Consider rheumatic "
                    "heart disease — Nigeria has significantly higher RHD prevalence than "
                    "high-income countries. Mitral stenosis, AR, and RHD-related cardiac "
                    "failure can all present with chest tightness in young adults."
        })
    if risk.get("hiv"):
        notes.append({
            "type": "info",
            "text": "<b>HIV / ARV therapy:</b> HIV-positive patients and those on ARVs "
                    "have elevated rates of pericarditis, myocarditis, pulmonary hypertension, "
                    "and accelerated atherosclerosis. ACS can occur at younger ages. "
                    "Some ARVs (particularly older NRTIs) are cardiotoxic"})

    if patient.get("systolic_bp", 120) > 180:
        notes.append({
            "type": "warning",
            "text": "<b>Severely elevated BP (> 180 mmHg):</b> In Nigeria, hypertension "
                    "is a major epidemic — 45% adult prevalence. Hypertensive emergency with "
                    "chest pain requires urgent BP reduction. Do not lower BP too fast "
                    "(risk of ischaemia). Target: reduce MAP by 20-25% in first hour."
        })

    if pain.startswith("Squeezing") and patient.get("duration") == "> 12 hours":
        notes.append({
            "type": "warning",
            "text": "■■ <b>Delayed presentation:</b> Patients in Nigeria often present "
                    "late due to transport, cost, or traditional medicine use. A 'late' "
                    "STEMI (> 12 hours) may still benefit from reperfusion — assess clinically. "
                    "Do not withhold aspirin or anticoagulation based on duration alone."

        })

    if not notes:
        notes.append({
            "type": "info",
            "text": "■■ No specific Nigerian-context alerts triggered for this presentation. "
                    "Apply standard chest pain assessment pathway."
        })
    return notes

