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

def _flatten_text(value):
    if isinstance(value, dict):
        return " ".join(
            _flatten_text(item)
            for item in value.values()
        )
    if isinstance(value, list):
        return " ".join(
            _flatten_text(item)
            for item in value
        )

    return normalize_text(value)


def _as_terms(items):
    return {
        _flatten_text(item)
        for item in items or []
        if _flatten_text(item)
    }


def evaluate_treatment(stage3, ground_truth):
    predicted_raw = stage3.get(
        "plan",
        {}
    ).get(
        "treatment_plan",
        []
    )

    expected_raw = ground_truth.get(
        "treatment_plan",
        []
    )

    predicted = set()

    for item in predicted_raw:
        predicted.update(
            normalize_treatment(item)
        )

    expected = set()

    for item in expected_raw:
        expected.update(
            normalize_treatment(item)
        )

    overlap = predicted.intersection(expected)

    precision = len(overlap) / len(predicted) if predicted else 0.0
    recall = len(overlap) / len(expected) if expected else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "treatment_overlap_count": len(overlap),
        "treatment_precision": precision,
        "treatment_recall": recall,
        "treatment_f1_score": f1
    }
