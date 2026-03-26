# Bayesian Chest Pain Triage System
### Nigerian Emergency Department · Clinical Decision Support

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://toyinbayesianstatisticstriage.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Portfolio%20%2F%20Not%20Clinically%20Validated-F59E0B?style=flat-square)]()

> **Clinical decision support for chest pain triage in Nigerian emergency departments.** Combines a knowledge-driven Bayesian classifier calibrated to Nigerian epidemiology with a Gradient Boosting ML model trained on synthetic Nigerian ED data. Runs completely offline. No cloud. No internet required after first launch.

---

## Table of Contents

1. [Why This Exists](#1-why-this-exists)
2. [Live Demo](#2-live-demo)
3. [System Architecture](#3-system-architecture)
4. [The Bayesian Model — Every Assumption Explained](#4-the-bayesian-model--every-assumption-explained)
5. [The ML Model — Design Decisions](#5-the-ml-model--design-decisions)
6. [Nigerian-Specific Calibrations](#6-nigerian-specific-calibrations)
7. [Facility-Level Investigation Tiering](#7-facility-level-investigation-tiering)
8. [Data Storage and Privacy Design](#8-data-storage-and-privacy-design)
9. [The Retraining Pathway](#9-the-retraining-pathway)
10. [Project Structure](#10-project-structure)
11. [Running Locally](#11-running-locally)
12. [Known Limitations and Honest Caveats](#12-known-limitations-and-honest-caveats)
13. [Validation Roadmap](#13-validation-roadmap)
14. [Model Card](#14-model-card)
15. [Author](#15-author)

---

## 1. Why This Exists

Emergency department triage tools are almost universally designed for high-income country settings. The Emergency Severity Index (ESI v4) — the most widely used triage framework — was developed and validated on Western patient populations, with access assumptions (CT scanners, troponin assays, immediate specialist availability) that do not reflect the reality of most Nigerian emergency departments.

This project asks: **what would ESI look like if it had been designed for Nigeria?**

Several factors make the Nigerian ED context genuinely distinct:

**Delayed presentation patterns.** Cost, transport barriers, and initial use of traditional or patent medicine vendors mean Nigerian patients frequently arrive sicker than the vital signs alone suggest. A patient who has been symptomatic for 18 hours before reaching a tertiary hospital is not the same as a patient who arrived 40 minutes after symptom onset — even if their vitals on arrival look similar.

**Sickle cell disease burden.** Nigeria has the highest absolute number of people living with sickle cell disease anywhere in the world. Acute chest syndrome — the most dangerous pulmonary complication of SCD and a leading cause of SCD-related death — does not appear in any Western triage algorithm. A tool that does not ask about SCD in Nigeria is not fit for purpose.

**HIV and cardiovascular risk.** Nigeria's HIV prevalence interacts with cardiovascular disease in ways that are not captured by standard risk calculators. HIV-associated pericarditis, pulmonary hypertension, and accelerated atherosclerosis on certain ARV regimens (particularly older NRTIs) all alter the differential diagnosis in ways a clinician needs to actively consider.

**Hypertension epidemic.** Adult hypertension prevalence in Nigeria is approximately 45% — substantially higher than Western reference populations. Hypertensive emergency presenting as chest pain is far more common proportionally, and the acute management pathway (targeted MAP reduction, not aggressive normalisation) is easily missed under pressure.

**Rheumatic heart disease.** RHD remains more prevalent in Nigeria than in high-income countries. A 28-year-old with squeezing chest pain and no traditional cardiac risk factors is a fundamentally different clinical problem in Lagos than in London.

**Differential equipment availability.** A tool that recommends CT pulmonary angiography at a Primary Health Centre is not decision support — it is noise. Useful clinical AI must know what is actually available at each level of the Nigerian health system and tier its recommendations accordingly.

This tool attempts to encode all of the above.

---

## 2. Live Demo

**[toyinbayesianstatisticstriage.streamlit.app](https://toyinbayesianstatisticstriage.streamlit.app/)**

The app has three pages:
- **Triage** — three-stage assessment: demographics/vitals → targeted clinical questions → results
- **Analytics** — aggregate dashboard of all locally saved assessments
- **Model Card** — full transparency documentation

> ⚠️ This is a portfolio demonstration. It has not been validated against real Nigerian patient outcomes. It must not be used for actual clinical decision-making.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     app.py (Streamlit UI)               │
│  Stage 1: Demographics + Vitals                         │
│  Stage 2: Targeted Clinical Questions                   │
│  Stage 3: Results + Differentials + Investigations      │
└────────┬──────────────────────────┬─────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌─────────────────────┐
│  bayesian_model │      │     ml_model.py      │
│  .py            │      │                      │
│                 │      │  GradientBoosting    │
│  Nigerian-      │      │  Classifier          │
│  calibrated     │      │  (synthetic data)    │
│  Bayesian ESI   │      │                      │
│  classifier     │      │  Feature importance  │
│                 │      │  explainability      │
└────────┬────────┘      └──────────┬──────────┘
         │                          │
         └────────────┬─────────────┘
                      ▼
         ┌────────────────────────┐
         │    clinical_data.py    │
         │                        │
         │  ESI labels + icons    │
         │  Investigation tiers   │
         │  Worst-case diffs      │
         │  Monitoring plans      │
         │  Nigerian context      │
         └────────────┬───────────┘
                      ▼
         ┌────────────────────────┐
         │      database.py       │
         │                        │
         │  SQLite (local file)   │
         │  triage_records.db     │
         │  Future training data  │
         └────────────────────────┘
```

**Why this stack?**

- **Streamlit** — fastest path from Python to a usable clinical UI. No frontend framework required. Runs on any laptop.
- **SQLite** — single-file database. Survives power cuts (writes are atomic). Works completely offline. Critically: every assessment saved is future ML training data.
- **scikit-learn only** — no GPU required, no complex dependencies. Any government hospital laptop from 2015 onwards can run this.
- **No cloud, no API calls** — patient data never leaves the device. This is a core design principle, not an afterthought.

---

## 4. The Bayesian Model — Every Assumption Explained

The heart of this system is a Naive Bayes classifier that works entirely from clinical knowledge, requiring no training data. The design choice to start here, rather than with pure ML, was deliberate: in a setting where no validated Nigerian ED outcome dataset exists, a knowledge-driven model that encodes clinical reasoning explicitly is both more trustworthy and more auditable than a black box trained on synthetic guesses.

### How it works

Bayes' theorem:

```
P(ESI | evidence) ∝ P(ESI) × ∏ P(evidence_i | ESI)
```

1. Start with prior probabilities for each ESI level in a Nigerian ED
2. For each clinical feature, multiply the posterior by its likelihood ratio at each ESI level
3. Re-normalise after each update (prevents floating-point underflow)
4. Return the ESI level with the highest posterior probability

### Prior Probabilities — The Nigerian ED Distribution

```python
NIGERIAN_PRIORS = [0.06, 0.20, 0.32, 0.27, 0.15]
# ESI:            [  1,    2,    3,    4,    5  ]
```

**Why these numbers, and not the Western ESI distribution?**

The standard Western ESI literature reports roughly: ESI 1 (1–3%), ESI 2 (8–12%), ESI 3 (32–36%), ESI 4 (32–36%), ESI 5 (12–16%). This Nigerian calibration diverges in three ways:

- **ESI 2 is raised to 20%** (vs ~10% Western). The rationale: delayed presentation in Nigerian EDs means patients who would have been ESI 3 on symptom onset arrive as ESI 2. Cost and transport barriers act as a filter — if you can afford to wait, you do. By the time many patients reach a Nigerian tertiary ED, acuity is higher than their vital signs at presentation may immediately suggest.

- **ESI 5 is lowered to 15%** (vs ~14–16% Western, similar). The reasoning here is the inverse: the cost barrier that keeps mild cases at home or at patent medicine vendors means truly non-urgent patients are under-represented in Nigerian hospital EDs. This is not a dramatic departure, but it's directionally correct.

- **ESI 1 at 6%** is slightly higher than the Western 1–3% floor. This reflects both the delayed presentation pattern (sicker on arrival) and the inclusion of acute chest syndrome, hypertensive emergency, and other high-acuity presentations that are more prevalent in Nigerian populations.

> ⚠️ **These priors are estimated from Nigerian ED literature and clinical reasoning. They have not been validated against a real outcome dataset. The explicit purpose of the SQLite database is to collect the data needed to validate and recalibrate them.**

### Likelihood Ratios — Clinical Reasoning Made Explicit

Each feature in `LIKELIHOODS` represents `P(feature present | ESI level)`. A few key design decisions:

**Shock BP (`systolic_bp < 90`):** `{ESI 1: 0.85, ESI 2: 0.20, ...}`
If a patient is in shock, there is an 85% probability their true acuity is ESI 1. This is a dominant feature and intentionally so — haemodynamic instability is the single most important triage signal.

**Tearing pain character:** `{ESI 1: 0.72, ESI 2: 0.42, ...}`
Tearing or ripping chest pain is a red flag for aortic dissection, which carries mortality of approximately 1–2% per hour untreated. The high ESI 1 likelihood ratio reflects this: if the pain character is tearing, the model should aggressively consider Type A dissection. This is reinforced by `back_radiation` and `instant_max_pain` which together form the classic dissection triad.

**Sickle cell disease:** `{ESI 1: 0.38, ESI 2: 0.48, ...}`
The peak probability is at ESI 2, not ESI 1. This reflects the clinical reality: most SCD patients with chest presentations have acute chest syndrome (ESI 2 — emergent, needs immediate assessment and intervention) rather than immediately life-threatening shock. The ESI 1 weight (0.38) captures the subset who arrive in crisis.

**Young adult (`age < 35`):** `{ESI 1: 0.12, ESI 2: 0.18, ESI 3: 0.24, ESI 4: 0.36, ESI 5: 0.46}`
Lower acuity weight for young adults — lower baseline cardiac risk. However, this feature interacts with `young_squeezing` (young + squeezing pain) and `sickle_cell` which both push the posterior back up. The model does not naively assume young = safe.

**Pregnancy:** `{ESI 1: 0.42, ESI 2: 0.48, ...}`
Elevated across all high-acuity levels. Pregnancy raises the differential for pulmonary embolism (hypercoagulable state), peripartum cardiomyopathy, and aortic dissection (Marfan's, connective tissue disorders). This is not over-stated — it is clinically appropriate.

### The Safety Floor

```python
if calculate_initial_esi(patient) == 1:
    best_esi = 1
```

The Bayesian model cannot downgrade a patient from ESI 1 if the initial rule-based assessment assigned them ESI 1. This is a hard safety constraint. The rule-based pass uses direct vital sign thresholds (BP < 80, SpO₂ < 85, HR > 150) that constitute immediate life threats regardless of what the probabilistic model calculates. The Bayesian model can upgrade a patient's acuity; it cannot lower a patient below the safety floor.

---

## 5. The ML Model — Design Decisions

### Why Gradient Boosting?

For tabular clinical data with mixed numeric and binary features, GradientBoostingClassifier is the appropriate choice. It:

- Handles the mix of continuous (vitals) and binary (symptoms, risk factors) features without preprocessing gymnastics
- Provides feature importances directly, enabling explainability
- Does not require GPU
- Outperforms logistic regression on non-linear interactions (e.g. the interaction between age, pain character, and SCD status) without the opacity of deep learning

Random Forest was considered and rejected — GBM typically outperforms RF on structured clinical data and the slight increase in training time is irrelevant here (model is cached after first run).

### Hyperparameters and Why

```python
GradientBoostingClassifier(
    n_estimators=180,
    max_depth=4,
    learning_rate=0.08,
    subsample=0.85,
    min_samples_leaf=8,
    random_state=42
)
```

- `n_estimators=180` — sufficient trees to learn complex interactions without overfitting synthetic data
- `max_depth=4` — limits tree complexity; clinical decision logic rarely requires more than 4 levels of interaction
- `learning_rate=0.08` — conservative; compensates for synthetic data that may not fully represent real variance
- `subsample=0.85` — stochastic gradient boosting; reduces overfitting on the 600-record synthetic dataset
- `min_samples_leaf=8` — prevents trees from splitting on noise in a small dataset
- `random_state=42` — reproducibility

### Synthetic Data — What It Represents and What It Doesn't

The 600 synthetic records in `ml_model.py` are calibrated to Nigerian ED epidemiology:

- Age distribution skewed younger than Western EDs (Nigerian median presenting age is lower)
- Hypertension prevalence at 45% (matches Nigerian adult population data)
- SCD prevalence at 2.5% (conservative estimate for Nigerian population)
- HIV prevalence at 1.6% (UNAIDS Nigeria estimate)
- ESI distribution matching `NIGERIAN_PRIORS`
- Vital sign distributions conditioned on ESI level (ESI 1 patients have mean BP 82 mmHg, not 130)

**What this is:** A demonstration that the ML pipeline works and produces sensible feature importances. A placeholder that shows what the model will look like when real data replaces it.

**What this is not:** A substitute for real patient data. The cross-validation accuracy of ~0.78 on synthetic data is expected to change — possibly substantially — when the model is retrained on real outcomes. This is not a failure; it is the plan.

---

## 6. Nigerian-Specific Calibrations

These are the features that most distinguish this tool from a port of any Western triage algorithm:

### Sickle Cell Acute Chest Syndrome
Acute chest syndrome (ACS) is defined as a new pulmonary infiltrate on chest X-ray accompanied by fever, chest pain, or respiratory symptoms in a patient with SCD. It is the most dangerous acute pulmonary complication of SCD and the leading cause of death in SCD patients. Nigeria has the world's highest SCD population burden — approximately 150,000 SCD babies are born in Nigeria annually.

No Western triage algorithm asks about SCD. This tool makes it an explicit risk factor with its own likelihood ratios and generates a specific clinical alert when SCD is present.

### Hypertensive Emergency
Adult hypertension prevalence in Nigeria is approximately 45%, compared to ~30% in the US and ~25% in Europe. Hypertensive emergency — severely elevated BP with end-organ damage — presenting as chest pain is disproportionately common. The tool generates a specific Nigerian context note when SBP > 180 mmHg, reminding the clinician of the MAP reduction target (20–25% in the first hour) and the danger of over-aggressive BP lowering.

### Delayed Presentation
The model's elevated ESI 2 prior (20% vs ~10% Western) encodes the clinical reality that delayed presentations shift the acuity distribution of arriving patients upward. A specific context note fires when squeezing chest pain has been present for > 12 hours — reminding clinicians not to withhold aspirin or anticoagulation based on duration alone, since late STEMI may still benefit from reperfusion.

### Rheumatic Heart Disease
RHD prevalence in Nigeria is substantially higher than in high-income countries due to incomplete streptococcal pharyngitis treatment in childhood. Mitral stenosis and AR secondary to RHD can present as chest tightness in young adults. The `young_squeezing` likelihood feature (age < 40 + squeezing pain) captures this, and a context note fires for young patients with this presentation.

### HIV and Cardiovascular Risk
The `hiv_arv` likelihood feature covers multiple mechanisms: HIV-associated pericarditis, myocarditis, pulmonary arterial hypertension, and the cardiotoxicity of older NRTI antiretroviral drugs (particularly zidovudine and didanosine). A context note fires for HIV-positive patients, explicitly noting the ARV cardiotoxicity angle which is often missed in routine care.

---

## 7. Facility-Level Investigation Tiering

This is arguably the most practically important feature in the system.

The Nigerian health system operates across three tiers that have fundamentally different diagnostic capabilities:

| Facility Level | Typical Equipment | Common Gaps |
|---|---|---|
| Primary Health Centre (PHC) | BP cuff, glucometer, pulse oximeter, malaria RDT | No ECG, no imaging, no labs |
| Secondary Hospital | Basic labs, ECG, plain X-ray, basic USS | No troponin, no CT, no echo |
| Tertiary / Teaching Hospital | Full biochemistry, troponin, echo, CT (where functioning) | Variable CT availability even at tertiary level |

For every pain type, the tool provides:
- **Available investigations** — what you can actually order at this facility
- **Unavailable investigations** — what you cannot get here (with referral guidance)
- **Refer if** — explicit triggers for escalation

**Example:** A patient with tearing chest pain at a Primary Health Centre receives these instructions: establish IV access, give analgesia, check BP in both arms for asymmetry — and immediately transfer. The tool does not suggest CT aortography at a PHC. It knows this is not available and says so explicitly.

This tiering reflects real knowledge about how Nigerian healthcare infrastructure works. It is the feature that most demonstrates insider clinical and contextual knowledge.

---

## 8. Data Storage and Privacy Design

All data is stored in a local SQLite file (`triage_records.db`). Nothing is ever transmitted externally.

**Privacy design decisions:**
- No patient names are collected — only an auto-generated anonymous ID (`NIG-YYYYMMDD-XXXX`) or an existing hospital number
- The ID format is designed to be memorably linkable within a session but non-identifying outside it
- NDPR (Nigeria Data Protection Regulation) alignment by design

**Why SQLite specifically:**
- Atomic writes — if power cuts mid-write, the database is not corrupted
- Single file — easy to back up, easy to transfer, no database server to maintain
- Zero configuration — works immediately on any laptop

**The dual purpose of the database:**
Every triage assessment saved is future ML training data. The schema includes an `actual_outcome` field (null at time of triage) and a separate `outcomes` table for recording clinical disposition once the patient's journey is known. When this table is populated, `retrain_model.py` can replace the synthetic training data with real Nigerian patient outcomes.

---

## 9. The Retraining Pathway

```
Stage 1 (NOW):     Synthetic data → pipeline demonstrated, model deployed
Stage 2 (future):  200+ records + verified outcomes → retrain_model.py
Stage 3 (future):  Subgroup analysis: age, sex, facility level, geopolitical zone
Stage 4 (future):  Clinical validation study → sensitivity, specificity, AUROC
Stage 5 (future):  IRB approval → prospective deployment with governance
```

`retrain_model.py` is not scaffolding — it is the documented path from portfolio project to validated tool. It loads only records with verified outcomes from the `outcomes` table, maps clinical disposition to ESI labels, rebuilds the feature matrix, runs 5-fold cross-validation, retrains the GBM on all available data, and saves the new model to disk.

The threshold is set conservatively at 200 records minimum. Below 50, the script declines to retrain and explains why. The UI sidebar tracks progress toward the 200-record milestone.

---

## 10. Project Structure

```
triage-system/
├── app.py                  # Streamlit UI — all three pages (762 lines)
├── bayesian_model.py       # Bayesian classifier + Nigerian priors (351 lines)
├── ml_model.py             # GBM classifier + synthetic data generation (259 lines)
├── clinical_data.py        # Nigerian clinical reference data (499 lines)
├── database.py             # SQLite persistence layer (136 lines)
├── retrain_model.py        # Retraining script for real outcome data (156 lines)
├── utils.py                # Patient ID generator (17 lines)
├── requirements.txt        # Dependencies
├── ml_model.pkl            # Trained model (generated on first run)
├── triage_records.db       # SQLite database (generated on first run)
└── README.md
```

**Total: 2,180 lines across 7 files**

---

## 11. Running Locally

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/onwunaru760-a11y/triage-system.git
cd triage-system
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`. On first run, the ML model trains on synthetic data and saves to `ml_model.pkl` (~5–10 seconds). All subsequent runs load the cached model instantly.

### Dependencies

```
streamlit
numpy
pandas
scikit-learn
```

No GPU required. No cloud services. No API keys. Runs completely offline after first `pip install`.

---

## 12. Known Limitations and Honest Caveats

These are not disclaimers to satisfy lawyers. They are genuine limitations that any clinician or technical reviewer needs to understand.

**1. Neither model has been validated on real patient outcomes.**
The Bayesian priors are estimated from literature and clinical reasoning. The ML model is trained on synthetic data. The cross-validation accuracy of 0.78 is on synthetic data — it may be lower, higher, or differently distributed on real patients. This cannot be known without a clinical validation study.

**2. Chest pain only.**
The system is not generalisable to other presenting complaints. A patient with dyspnoea, syncope, or epigastric pain should not be triaged with this tool, even though these presentations may involve the same underlying diagnoses.

**3. English-only interface.**
The tool does not handle Yoruba, Hausa, Igbo, or Nigerian Pidgin input. In a country with hundreds of languages and dialects, this is a real accessibility limitation.

**4. Single-complaint model.**
Real triage involves multiple simultaneous patients, dynamic queue management, and resource allocation decisions across the department. This tool handles one patient at a time and does not model departmental flow.

**5. Equipment availability assumptions are approximations.**
The facility-level tiering is based on reasonable estimates of what is typically available. Real availability varies enormously by state, funding cycle, and equipment maintenance status.

**6. Naive Bayes independence assumption.**
The Bayesian model treats each clinical feature as conditionally independent given the ESI level. This is a known simplification — diaphoresis and radiation co-occur in ACS more than their individual probabilities would suggest. The independence assumption makes the model tractable and interpretable, but it introduces error.

---

## 13. Validation Roadmap

For this tool to progress from portfolio demonstration to deployable clinical tool, the following steps are required — in order:

1. **Ethics approval** — IRB/HREC approval from a Nigerian institution for prospective data collection
2. **Outcome data collection** — Record verified dispositions (ICU, ward, discharge, diagnosis) for each triage assessment
3. **Bayesian prior recalibration** — Validate and update `NIGERIAN_PRIORS` against real outcome distribution
4. **ML retraining** — Run `retrain_model.py` with 200+ real outcome records
5. **Prospective validation study** — Sensitivity, specificity, AUROC, PPV, NPV for ESI 1–2 detection
6. **Subgroup analysis** — Age, sex, facility level, geopolitical zone, SCD status, HIV status
7. **NAFDAC Software as Medical Device review** — Nigerian regulatory pathway for clinical software
8. **Institutional deployment** — With governance framework, clinician training, and monitoring protocol

---

## 14. Model Card

| Field | Value |
|---|---|
| **Model name** | Bayesian Chest Pain Triage System |
| **Version** | 1.0.0 (Portfolio / Pre-validation) |
| **Model type** | Hybrid: Bayesian inference + Gradient Boosting classifier |
| **Clinical domain** | Emergency triage — adult chest pain |
| **Target setting** | Nigerian emergency departments (all facility levels) |
| **Training data (Bayesian)** | Nigerian ED literature + clinical expertise (no patient data) |
| **Training data (ML)** | 600 synthetic records, Nigerian ED-calibrated |
| **Real-world validation** | ❌ Not yet conducted |
| **ML CV accuracy (synthetic)** | ~0.78 (5-fold cross-validation) |
| **Languages** | English only |
| **Patient ages** | Adults ≥ 16 years |
| **Privacy** | No PII collected. All data stored locally. NDPR-aligned. |
| **Stack** | Python, Streamlit, SQLite, scikit-learn — no cloud |
| **Human oversight required** | Yes — mandatory. Tool is decision support only. |

*Model Card format: Mitchell et al. (2019). Model Cards for Model Reporting. FAccT 2019.*

---

## 15. Author

**Toyin** — 5th-year medical student (6-year MBBS programme, Nigeria) with a parallel track in health technology.

This project sits at the intersection of clinical medicine and machine learning in African healthcare contexts. It was built to demonstrate what happens when clinical insider knowledge — understanding of Nigerian epidemiology, health system structure, and patient population — is combined with technical implementation skills. The goal was not to build a generic triage app, but to build one that could only have been designed by someone who understands both the clinical and systems-level realities of emergency medicine in Nigeria.

**GitHub:** [github.com/onwunaru760-a11y](https://github.com/onwunaru760-a11y)

**Live app:** [toyinbayesianstatisticstriage.streamlit.app](https://toyinbayesianstatisticstriage.streamlit.app/)

---

## Citation

If you use this project in research or build on it:

```bibtex
@software{toyin_bayesian_triage_2025,
  title   = {Bayesian Chest Pain Triage System: Nigerian Emergency Department Clinical Decision Support},
  author  = {Toyin},
  year    = {2025},
  url     = {https://github.com/onwunaru760-a11y/triage-system}
}
```

---

*This tool is a portfolio demonstration. It has not been validated against real Nigerian patient outcomes. It must not be used for clinical decision-making. The final triage decision rests entirely with the attending clinician.*
