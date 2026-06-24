import re
from evaluation.ontology import (
    canonicalize,
    get_disease_category,
    DIAGNOSIS_SYNONYMS,
    DIAGNOSIS_MAP
)
from rapidfuzz import fuzz

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text

def diagnosis_match_score(predicted, expected):
    predicted = canonicalize(predicted, DIAGNOSIS_SYNONYMS)
    expected = canonicalize(expected, DIAGNOSIS_SYNONYMS)
    if predicted == expected:
        return 1.0

    similarity = fuzz.token_sort_ratio(predicted, expected) / 100.0

    return similarity

def evaluate_diagnosis(stage2, ground_truth):
    predicted_primary = canonicalize(stage2.get("primary", {}).get("primary_diagnosis", ""),DIAGNOSIS_SYNONYMS)
    predicted_alternatives = [
        canonicalize(item, DIAGNOSIS_SYNONYMS)
        for item in stage2.get("alternatives", {}).get("alternative_diagnoses", [])
    ]

    gt_primary = canonicalize(ground_truth.get("primary_diagnosis", ""), DIAGNOSIS_SYNONYMS)
    gt_alternatives = [
        canonicalize(item, DIAGNOSIS_SYNONYMS)
        for item in
        ground_truth.get("alternative_diagnoses", [])
    ]

    primary_score = diagnosis_match_score(predicted_primary, gt_primary)

    alternative_score = 0.0
    if gt_alternatives and predicted_alternatives:
        scores = []
        for gt_alt in gt_alternatives:
            best_match = max(
                diagnosis_match_score(pred_alt, gt_alt)
                for pred_alt in predicted_alternatives
            )
            scores.append(best_match)

        alternative_score = (sum(scores) / len(scores))
    if primary_score >= 0.95:
        alternative_score = 1.0

    pred_category = get_disease_category(predicted_primary)
    gt_category = get_disease_category(gt_primary)

    category_score = (1.0 if pred_category == gt_category else 0.0)
    reviewer_score = (1.0 if stage2.get("review", {}).get("approved", False) else 0.0)
    evidence_score = 0.0

    diagnosis_score = (0.60 * primary_score + 0.20 * alternative_score + 0.10 * category_score + 0.05 * reviewer_score + 0.05 * evidence_score)
    diagnosis_correct = (diagnosis_score >= 0.70)

    print("\nDIAGNOSIS EVAL")                           #
    print("GT Primary:", gt_primary)
    print("Pred Primary:", predicted_primary)
    print("Primary Score:", primary_score)
    print("Alternative Score:", alternative_score)
    print("Category Score:", category_score)
    print("Reviewer Score:", reviewer_score)
    print("Diagnosis Score:", diagnosis_score)          #

    return {
        "predicted_primary_diagnosis": predicted_primary,
        "expected_primary_diagnosis": gt_primary,
        "primary_score": round(primary_score, 3),
        "alternative_score": round(alternative_score, 3),
        "category_score": round(category_score, 3),
        "reviewer_score": round(reviewer_score, 3),
        "evidence_score": round(evidence_score, 3),
        "diagnosis_score": round(diagnosis_score, 3),
        "diagnosis_correct": int(diagnosis_correct),
        "diagnosis_weighted_score": round(diagnosis_score, 3),
        "diagnosis_category_match": category_score
    }