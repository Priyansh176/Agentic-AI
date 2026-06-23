DIAGNOSIS_SYNONYMS = {
    "community acquired pneumonia": {
        "community acquired pneumonia",
        "cap",
        "pneumonia",
        "bacterial pneumonia",
        "lung infection",
        "lower respiratory tract infection"
    },

    "copd exacerbation": {
        "copd exacerbation",
        "copd flare",
        "acute copd",
        "chronic obstructive pulmonary disease exacerbation"
    },

    "deep vein thrombosis": {
        "deep vein thrombosis",
        "dvt"
    },

    "chronic kidney disease": {
        "chronic kidney disease",
        "ckd"
    },

    "diabetic ketoacidosis": {
        "diabetic ketoacidosis",
        "dka"
    },

    "heart failure exacerbation": {
        "heart failure exacerbation",
        "heart failure",
        "acute heart failure",
        "congestive heart failure",
        "chf",
        "decompensated heart failure"
    },
    
    "acute coronary syndrome": {
        "acute coronary syndrome",
        "acs",
        "myocardial infarction",
        "heart attack",
        "stemi",
        "nstemi",
        "acute mi",
        "coronary syndrome"
    },

    "atrial fibrillation": {
        "atrial fibrillation",
        "afib",
        "a-fib",
        "atrial fib",
        "rapid afib"
    },
}

DIAGNOSIS_CATEGORIES = {
    "acute coronary syndrome": "cardiovascular",
    "heart failure exacerbation": "cardiovascular",
    "atrial fibrillation": "cardiovascular",
    "community acquired pneumonia": "respiratory",
    "copd exacerbation": "respiratory",
    "deep vein thrombosis": "vascular",
    "chronic kidney disease": "renal",
    "diabetic ketoacidosis": "endocrine"
}

def canonical_diagnosis(text):
    text = normalize_text(text)
    for canonical, aliases in DIAGNOSIS_SYNONYMS.items():
        if text in aliases:
            return canonical
    return text

def normalize_text(value):
    return str(value or "").strip().lower()

def evaluate_diagnosis(stage2, ground_truth):
    predicted = canonical_diagnosis(
        stage2.get("primary", {}).get("primary_diagnosis","")
    )

    expected = canonical_diagnosis(
        ground_truth.get("primary_diagnosis", "")
    )

    alternatives = [
        canonical_diagnosis(item)
        for item in ground_truth.get("alternative_diagnoses", [])
    ]

    exact_match = int(predicted == expected)

    alternative_match = int(predicted in alternatives)

    partial_match = int(
        bool(predicted)
        and (predicted in expected or expected in predicted)
    )

    weighted_score = (
        1.0
        if exact_match
        else 0.75
        if partial_match
        else 0.5
        if alternative_match
        else 0.0
    )

    predicted_category = DIAGNOSIS_CATEGORIES.get(predicted)

    expected_category = DIAGNOSIS_CATEGORIES.get(expected)

    category_match = int(
        predicted_category == expected_category
        and predicted_category is not None
    )

    return {
        "predicted_primary_diagnosis": predicted,
        "expected_primary_diagnosis": expected,
        "diagnosis_correct": exact_match,
        "primary_diagnosis_exact_match": exact_match,
        "primary_diagnosis_partial_match": partial_match,
        "predicted_is_ground_truth_alternative": alternative_match,
        "diagnosis_weighted_score": weighted_score,
        "diagnosis_category_match": category_match
    }