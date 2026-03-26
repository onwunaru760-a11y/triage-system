"""
utils.py — Small utility functions
"""
import random
import string
from datetime import datetime

def generate_patient_id():
    """
    Generate a random patient ID.
    No names collected — ID only (Document 2, Section 11 — Privacy).
    Format: NIG-YYYYMMDD-XXXX
    """
    date_part = datetime.now().strftime("%Y%m%d")
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"NIG-{date_part}-{rand_part}"
