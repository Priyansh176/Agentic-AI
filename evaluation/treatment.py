import re
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


def extract_medical_concepts(text):

    text = normalize_text(text)

    tokens = re.findall(
        r"[a-zA-Z][a-zA-Z\-]+",
        text
    )

    stopwords = {
        "the",
        "and",
        "with",
        "for",
        "until",
        "daily",
        "high",
        "medium",
        "low",
        "patient",
        "symptoms",
        "treatment",
        "monitor",
        "assess",
        "address"
    }

    return {
        token
        for token in tokens
        if token not in stopwords
        and len(token) > 3
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
    # print("\nGROUND TRUTH TREATMENT")   #
    # print(ground_truth)

    # print("\nPREDICTED PLAN")
    # print(stage3)                       #

    predicted_treatments = set()
    for item in stage3.get("plan", {}).get(
        "treatment_plan",
        []
    ):

        if isinstance(item, dict):

            description = item.get(
                "description",
                ""
            )

            if description:
                predicted_treatments.update(
                    extract_medical_concepts(
                        description
                    )
                )

        else:

            predicted_treatments.update(
                extract_medical_concepts(
                    str(item)
                )
            )

    expected_treatments = set(
        normalize_text(x)
        for x in ground_truth.get("treatment_plan", [])
    )

    treatment_precision, treatment_recall, treatment_f1 = compute_f1(predicted_treatments, expected_treatments)

    predicted_tests = set()
    for item in stage3.get("plan", {}).get(
        "recommended_tests",
        []
    ):
        if isinstance(item, dict):

            test_name = item.get(
                "test_name",
                ""
            )

            if test_name:
                predicted_tests.add(
                    normalize_text(test_name)
                )

        else:
            predicted_tests.add(
                normalize_text(str(item))
            )

    expected_tests = set(
        normalize_text(x)
        for x in ground_truth.get("recommended_tests", [])
    )

    test_precision, test_recall, test_f1 = compute_f1(predicted_tests, expected_tests)

    predicted_monitoring = set()

    for item in stage3.get("plan", {}).get(
        "monitoring",
        []
    ):
        if isinstance(item, dict):

            parameter = item.get(
                "parameter",
                ""
            )

            if parameter:
                predicted_monitoring.add(
                    normalize_text(parameter)
                )

        else:
            predicted_monitoring.add(
                normalize_text(str(item))
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