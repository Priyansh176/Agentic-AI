import re
import json     #
from evaluation.diagnosis import normalize_text
from evaluation.ontology import (
    canonicalize,
    TREATMENT_CLASSES,
    TEST_CLASSES,
    MONITORING_CLASSES
)

def compute_f1(predicted_set, expected_set):
    overlap = predicted_set.intersection(expected_set)

    precision = (len(overlap) / len(predicted_set) if predicted_set else 0.0)
    recall = (len(overlap) / len(expected_set) if expected_set else 0.0)
    f1 = (2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0)

    return precision, recall, f1

def canonicalize_treatment(text):
    text = normalize_text(text)
    matches = set()
    for canonical, synonyms in TREATMENT_CLASSES.items():
        canonical_norm = normalize_text(canonical)
        if canonical_norm in text:
            matches.add(canonical)
        for synonym in synonyms:
            synonym_norm = normalize_text(synonym)
            if synonym_norm in text:
                matches.add(canonical)

    return matches

def canonicalize_test(text):
    text = normalize_text(text)
    matches = set()
    for canonical, synonyms in TEST_CLASSES.items():
        canonical_norm = normalize_text(canonical)
        if canonical_norm in text:
            matches.add(canonical)
        for synonym in synonyms:
            synonym_norm = normalize_text(synonym)
            if synonym_norm in text:
                matches.add(canonical)

    return matches

def evaluate_treatment(stage3, ground_truth):
    # print("\nGROUND TRUTH TREATMENT")   #
    # print(ground_truth)

    # print("\nPREDICTED PLAN")
    # print(stage3)                       #

    gt_treatments = set()
    for item in ground_truth.get("treatment_plan", []):
        gt_treatments.update(canonicalize_treatment(item))

    pred_treatments = set()
    for item in stage3.get("plan", {}).get("treatment_plan", []):
        if isinstance(item, dict):
            text = ""
            if isinstance(item, dict):
                text = " ".join(str(v) for v in item.values())
            else:
                text = str(item)
            pred_treatments.update(canonicalize_treatment(text))
        else:
            pred_treatments.update(canonicalize_treatment(str(item)))

    treatment_precision, treatment_recall, treatment_f1 = compute_f1(pred_treatments, gt_treatments)

    gt_tests = set()
    for item in ground_truth.get("recommended_tests", []):
        gt_tests.update(canonicalize_test(item))

    pred_tests = set()
    for item in stage3.get("plan", {}).get("recommended_tests", []):
        text = ""
        if isinstance(item, dict):
            text = " ".join(str(v) for v in item.values())
        else:
            text = str(item)
        pred_tests.update(canonicalize_test(text))

    test_precision, test_recall, test_f1 = compute_f1(pred_tests, gt_tests)

    components = []
    if gt_treatments:
        components.append(("treatment", treatment_f1, 0.7))
    if gt_tests:
        components.append(("test", test_f1, 0.3))

    total_weight = sum(weight for _, _, weight in components)

    clinical_treatment_score = 0
    for _, score, weight in components:
        clinical_treatment_score += (weight / total_weight) * score

    # print("\nTREATMENT EVAL")                                       #
    # print("GT Treatments:", gt_treatments)
    # print("Pred Treatments:", pred_treatments)
    # print("GT Tests:", gt_tests)
    # print("Pred Tests:", pred_tests)
    # print("Treatment F1:", treatment_f1)
    # print("Test F1:", test_f1)
    print("Clinical Treatment Score:", clinical_treatment_score)    #                            

    return {
        "treatment_precision": round(treatment_precision, 3),
        "treatment_recall": round(treatment_recall, 3),
        "treatment_f1": round(treatment_f1, 3),
        "test_precision": round(test_precision, 3),
        "test_recall": round(test_recall, 3),
        "test_f1": round(test_f1, 3),
        "clinical_treatment_score": round(clinical_treatment_score, 3)
    }