def _stage3(
    self,
    stage2
):

    assignments = (
        self.strategy.assign_roles(
            "treatment_planning",
            self.available_models
        )
    )

    planner = OllamaClient(
        assignments["Planner"]
    )

    risk_assessor = OllamaClient(
        assignments["Risk Assessor"]
    )

    validator = OllamaClient(
        assignments["Validator"]
    )

    # ------------------------------------
    # Planner
    # ------------------------------------

    treatment_plan = (
        planner.generate_json(
            f"""
You are the Treatment Planner.

Create a treatment plan based on the diagnosis.

Return ONLY valid JSON.

{{
    "treatment_plan": [],
    "recommended_tests": [],
    "monitoring": []
}}

Diagnosis:

{json.dumps(stage2, indent=2)}
"""
        )
    )

    # ------------------------------------
    # Risk Assessor
    # ------------------------------------

    risks = (
        risk_assessor.generate_json(
            f"""
You are the Risk Assessor.

Identify risks, contraindications,
missing information, and safety concerns.

Return ONLY valid JSON.

{{
    "risk_score": 0,
    "warnings": [],
    "contraindications": []
}}

Treatment Plan:

{json.dumps(treatment_plan, indent=2)}

Diagnosis:

{json.dumps(stage2, indent=2)}
"""
        )
    )

    # ------------------------------------
    # Validator
    # ------------------------------------

    validation = (
        validator.generate_json(
            f"""
You are the Treatment Validator.

Validate the treatment plan and risk assessment.

Return ONLY valid JSON.

{{
    "approved": true,
    "validation_comments": [],
    "required_changes": []
}}

Treatment Plan:

{json.dumps(treatment_plan, indent=2)}

Risk Assessment:

{json.dumps(risks, indent=2)}
"""
        )
    )

    return {

        "plan":
            treatment_plan,

        "risk":
            risks,

        "validation":
            validation
    }