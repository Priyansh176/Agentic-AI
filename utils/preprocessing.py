def build_model_input(case):

    model_input = {

        "case_id": case["case_id"],

        "patient_profile":
            case["patient_profile"],

        "symptom_information":
            case["symptom_information"],

        "security_scenario":
            case["security_scenario"]
    }

    if "ground_truth" in model_input:
        raise ValueError(
            "ground_truth must never be included in model input"
        )

    return model_input
