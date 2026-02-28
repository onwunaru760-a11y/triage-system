### ESI RULE SCORING ###

def calculate_esi(patient):  # initial esi based on systolic bp, pulse, pain score, age, pregnancy
    systolic_bp = patient["systolic_bp"]
    pulse = patient["pulse"]
    pain = patient["pain_score"]
    age = patient["age"]
    pregnant = patient["pregnant"]

    if systolic_bp < 90:
        return 1  # unstable
    if pain >= 8 or pulse > 120 or age >= 65 or pregnant.lower() == "yes":
        return 2
    if pain >= 5 and pain < 8:
        return 3
    if pain > 0 and pain < 5:
        return 4
    return 5
