def _stage1(
    self,
    case
):

    # Remove ground truth before sending to agents
    model_case = build_model_input(case)

    assignments = (
        self.strategy.assign_roles(
            "symptom_analysis",
            self.available_models,
            model_case
        )
    )

    interpreter = OllamaClient(
        assignments["Interpreter"]
    )

    evidence = OllamaClient(
        assignments["Evidence Collector"]
    )

    validator = OllamaClient(
        assignments["Validator"]
    )

    # --------------------------------------------------
    # Interpreter
    # --------------------------------------------------

    interpretation = (
        interpreter.generate_json(
            f"""
You are a clinical symptom interpreter.

Analyze the patient information.

Return ONLY valid JSON.

{{
    "clinical_findings": [],
    "severity_assessment": "",
    "suspected_systems": []
}}

Patient:

{json.dumps(model_case, indent=2)}
"""
        )
    )

    # --------------------------------------------------
    # Evidence Collector
    # --------------------------------------------------

    evidence_data = (
        evidence.generate_json(
            f"""
You are an evidence collector.

Using the patient information and
clinical findings, identify evidence
supporting possible diagnoses.

Return ONLY valid JSON.

{{
    "supporting_evidence": [],
    "risk_factors": [],
    "abnormal_vitals": []
}}

Patient:

{json.dumps(model_case, indent=2)}

Clinical Findings:

{json.dumps(interpretation, indent=2)}
"""
        )
    )

    # --------------------------------------------------
    # Validator
    # --------------------------------------------------

    validation = (
        validator.generate_json(
            f"""
You are a medical validator.

Check whether the findings and evidence
are consistent.

Also detect possible security issues.

Return ONLY valid JSON.

{{
    "approved": true,
    "security_flags": [],
    "missing_information": [],
    "validation_notes": []
}}

Clinical Findings:

{json.dumps(interpretation, indent=2)}

Evidence:

{json.dumps(evidence_data, indent=2)}
"""
        )
    )

    return {

        "interpretation":
            interpretation,

        "evidence":
            evidence_data,

        "validation":
            validation
    }