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
"refer_if": "ESI 1-2, suspected STEMI on ECG, haemodynamic instability",
"cardiogenic shock, severe LVF",
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

