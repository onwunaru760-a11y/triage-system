"""
database.py
-----------
All data storage. Uses SQLite — a single file on your computer.
No internet. No server. No cloud. Everything stays on your machine.
Why SQLite:
- Works completely offline (Document 2, Sec 2 — Offline-First)
- Survives power cuts — writes are atomic (Document 2, Sec 7)
- Every assessment saved immediately after calculation
- Your future ML training data lives here
"""
import sqlite3
import json
from datetime import datetime
DB_PATH = "triage_records.db"

def init_db():
    """Create the database and tables on first run. Safe to call every time."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Main triage log — one row per completed assessment
    # No patient names — patient_id only (Document 2, Sec 11 — Privacy)
    c.execute("""
    CREATE TABLE IF NOT EXISTS triage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    age INTEGER,
    sex TEXT,
    pregnant TEXT,
    systolic_bp INTEGER,
    pulse INTEGER,
    spo2 INTEGER,
    rr INTEGER,
    pain_score INTEGER,
    pain_description TEXT,
    onset TEXT,
    duration TEXT,
    facility_level TEXT,
    answers_json TEXT,
    risk_factors_json TEXT,
    initial_esi INTEGER,
    bayesian_esi INTEGER,
    ml_esi INTEGER,
    posterior_json TEXT,
    actual_outcome TEXT DEFAULT NULL
    )
    """)
    # Add missing columns if they don't exist (for existing databases)
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN sex TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN pregnant TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN systolic_bp INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN pulse INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN spo2 INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN rr INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN pain_score INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN pain_description TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN onset TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN duration TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN facility_level TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN answers_json TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN risk_factors_json TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN initial_esi INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN bayesian_esi INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN ml_esi INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN posterior_json TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE triage_log ADD COLUMN actual_outcome TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    # Separate table for outcomes — added later when disposition is known
    # This is how you build your real training dataset
    c.execute("""
    CREATE TABLE IF NOT EXISTS outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    triage_log_id INTEGER,
    disposition TEXT,
    actual_diagnosis TEXT,
    notes TEXT,
    recorded_at TEXT,
    FOREIGN KEY (triage_log_id) REFERENCES triage_log(id)
    )
    """)
    conn.commit()
    conn.close()

def save_assessment(
    patient, answers, risk_factors, bayesian_esi_result, ml_esi_result,
    posterior, initial_esi, facility
):
    """Save a completed triage assessment to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    INSERT INTO triage_log (
    timestamp, patient_id, age, sex, pregnant,
    systolic_bp, pulse, spo2, rr,
    pain_score, pain_description, onset, duration,
    facility_level, answers_json, risk_factors_json,
    initial_esi, bayesian_esi, ml_esi, posterior_json
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(),
        patient.get("patient_id", "UNKNOWN"),
        patient.get("age"),
        patient.get("sex"),
        patient.get("pregnant", "No"),
        patient.get("systolic_bp"),
        patient.get("pulse"),
        patient.get("spo2"),
        patient.get("rr"),
        patient.get("pain_score"),
        patient.get("pain_description"),
        patient.get("onset"),
        patient.get("duration"),
        facility,
        json.dumps(answers),
        json.dumps(risk_factors),
        initial_esi,
        bayesian_esi_result,
        ml_esi_result,
        json.dumps(posterior)
    ))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def load_all_records():
    """Load all records for the analytics dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM triage_log ORDER BY timestamp DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_record_count():
    conn = sqlite3.connect(DB_PATH)

    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM triage_log")
    count = c.fetchone()[0]
    conn.close()
    return count
