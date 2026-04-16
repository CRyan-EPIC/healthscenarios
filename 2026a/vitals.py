# Patient vital signs data for all 21 patients
# Abnormal values include a tag for display highlighting

PATIENT_VITALS = {
    "Julian": {
        "HR": "98 bpm",
        "Temp": "100.2 F (elevated)",
        "BP": "105/68",
        "SpO2": "98%",
        "Resp": "18/min",
    },
    "Emily": {
        "HR": "102 bpm (elevated)",
        "Temp": "98.1 F",
        "BP": "90/58 (low)",
        "SpO2": "98%",
        "Blood Sugar": "54 mg/dL (LOW)",
    },
    "Sophia": {
        "HR": "82 bpm",
        "Temp": "98.4 F",
        "BP": "108/70",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Camila": {
        "HR": "80 bpm",
        "Temp": "99.0 F",
        "BP": "106/68",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Connor": {
        "HR": "78 bpm",
        "Temp": "98.6 F",
        "BP": "104/66",
        "SpO2": "99%",
        "Resp": "15/min",
    },
    "Ben": {
        "HR": "76 bpm",
        "Temp": "98.5 F",
        "BP": "110/70",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Aidan": {
        "HR": "100 bpm (elevated)",
        "Temp": "102.4 F (HIGH)",
        "BP": "100/62 (low)",
        "SpO2": "97%",
        "Resp": "20/min (elevated)",
    },
    "Emma": {
        "HR": "108 bpm (elevated)",
        "Temp": "98.6 F",
        "BP": "118/76",
        "SpO2": "99%",
        "Resp": "22/min (elevated)",
    },
    "Lizzy": {
        "HR": "90 bpm",
        "Temp": "98.4 F",
        "BP": "110/70",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Michaela": {
        "HR": "88 bpm",
        "Temp": "101.8 F (HIGH)",
        "BP": "108/68",
        "SpO2": "98%",
        "Resp": "17/min",
    },
    "Ian": {
        "HR": "92 bpm",
        "Temp": "98.6 F",
        "BP": "112/72",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Samira": {
        "HR": "104 bpm (elevated)",
        "Temp": "98.8 F",
        "BP": "114/74",
        "SpO2": "99%",
        "Resp": "18/min",
    },
    "Ethan": {
        "HR": "110 bpm (elevated)",
        "Temp": "98.6 F",
        "BP": "100/65",
        "SpO2": "91% (LOW)",
        "Resp": "28/min (HIGH)",
    },
    "Jackson": {
        "HR": "82 bpm",
        "Temp": "99.8 F (elevated)",
        "BP": "108/70",
        "SpO2": "98%",
        "Resp": "17/min",
    },
    "Cynthia": {
        "HR": "78 bpm",
        "Temp": "98.6 F",
        "BP": "106/68",
        "SpO2": "99%",
        "Resp": "15/min",
    },
    "Olivia": {
        "HR": "68 bpm (low)",
        "Temp": "98.4 F",
        "BP": "126/82 (elevated)",
        "SpO2": "99%",
        "Resp": "14/min",
    },
    "Leo": {
        "HR": "64 bpm (low)",
        "Temp": "97.8 F (low)",
        "BP": "100/62 (low)",
        "SpO2": "99%",
        "Resp": "14/min",
    },
    "Zoe": {
        "HR": "80 bpm",
        "Temp": "98.6 F",
        "BP": "110/70",
        "SpO2": "99%",
        "Resp": "16/min",
    },
    "Tyler": {
        "HR": "96 bpm (elevated)",
        "Temp": "98.8 F",
        "BP": "120/78 (elevated)",
        "SpO2": "98%",
        "Resp": "16/min",
    },
    "Riley": {
        "HR": "124 bpm (HIGH)",
        "Temp": "99.2 F",
        "BP": "132/86 (HIGH)",
        "SpO2": "99%",
        "Resp": "22/min (elevated)",
    },
    "Mason": {
        "HR": "106 bpm (elevated)",
        "Temp": "98.6 F",
        "BP": "116/74",
        "SpO2": "99%",
        "Resp": "20/min (elevated)",
    },
}


def get_vitals(patient_name):
    """Return vitals dict for a patient, or None if not found."""
    return PATIENT_VITALS.get(patient_name)


def format_vitals_for_display(patient_name):
    """Return a list of (label, value, is_abnormal) tuples for display."""
    vitals = get_vitals(patient_name)
    if not vitals:
        return []
    result = []
    for label, value in vitals.items():
        is_abnormal = any(tag in value for tag in ("elevated", "low", "HIGH", "LOW"))
        result.append((label, value, is_abnormal))
    return result
