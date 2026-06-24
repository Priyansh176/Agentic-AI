from evaluation.diagnosis import normalize_text

TREATMENT_CONCEPTS = {
    "oxygen": {
        "oxygen",
        "oxygen therapy",
        "supplemental oxygen",
        "oxygen support"
    },

    "antibiotic": {
        "antibiotic",
        "antibiotics",
        "empiric antibiotics",
        "early antibiotics"
    },

    "bronchodilator": {
        "bronchodilator",
        "bronchodilators",
        "albuterol"
    },

    "corticosteroid": {
        "corticosteroid",
        "corticosteroids",
        "steroid",
        "steroids"
    },

    "anticoagulation": {
        "anticoagulation",
        "heparin",
        "apixaban"
    },

    "diuretic": {
        "diuretic",
        "diuretics",
        "furosemide"
    },

    "insulin": {
        "insulin"
    },

    "hydration": {
        "hydration",
        "iv fluids",
        "fluid management",
        "fluids"
    },

    "electrolyte_management": {
        "electrolyte",
        "electrolyte correction"
    },

    "rehabilitation": {
        "rehabilitation",
        "physical therapy"
    },

    "isolation": {
        "isolation",
        "isolation precautions"
    },

    "monitoring": {
        "monitor",
        "monitoring"
    },

    "fall_prevention": {
        "fall prevention"
    },

    "thyroid_treatment": {
        "levothyroxine",
        "thyroid monitoring"
    },

    "endocrinology_followup": {
        "endocrinology follow-up",
        "endocrinology referral"
    }
}

def compute_f1(predicted_set, expected_set):
    overlap = predicted_set.intersection(expected_set)

    precision = (len(overlap) / len(predicted_set) if predicted_set else 0.0)
    recall = (len(overlap) / len(expected_set) if expected_set else 0.0)
    f1 = (2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0)

    return precision, recall, f1

def normalize_treatment(item):
    item = normalize_text(item)
    concepts = set()
    for concept, aliases in TREATMENT_CONCEPTS.items():
        for alias in aliases:
            if alias in item:
                concepts.add(concept)
    if concepts:
        return concepts

    tokens = {
        token
        for token in item.split()
        if len(token) > 4
    }

    return tokens if tokens else {item}

def evaluate_treatment(stage3, ground_truth):
    predicted_raw = stage3.get("plan", {}).get("treatment_plan", [])
    expected_raw = ground_truth.get("treatment_plan", [])

    predicted = set()
    for item in predicted_raw:
        predicted.update(normalize_treatment(item))

    expected = set()
    for item in expected_raw:
        expected.update(normalize_treatment(item))

    treatment_precision, treatment_recall, treatment_f1 = compute_f1(predicted, expected)

    predicted_tests = set(
        normalize_text(x)
        for x in stage3.get("recommended_tests", [])
    )

    expected_tests = set(
        normalize_text(x)
        for x in ground_truth.get("recommended_tests", [])
    )

    test_precision, test_recall, test_f1 = compute_f1(predicted_tests, expected_tests)

    predicted_monitoring = set(
        normalize_text(x)
        for x in stage3.get("monitoring", [])
    )

    expected_monitoring = set(
        normalize_text(x)
        for x in ground_truth.get("monitoring", [])
    )

    monitoring_precision, monitoring_recall, monitoring_f1 = compute_f1(predicted_monitoring, expected_monitoring)

    clinical_f1 = (0.6 * treatment_f1 + 0.2 * test_f1 + 0.2 * monitoring_f1)

    return {
        "treatment_precision": treatment_precision,
        "treatment_recall": treatment_recall,
        "treatment_f1": treatment_f1,
        "test_f1": test_f1,
        "monitoring_f1": monitoring_f1,
        "clinical_f1": clinical_f1
    }
