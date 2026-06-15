def _stage2(
    self,
    stage1
):

    assignments = (
        self.strategy.assign_roles(
            "differential_diagnosis",
            self.available_models
        )
    )

    leader = OllamaClient(
        assignments["Diagnosis Leader"]
    )

    alternative_generator = OllamaClient(
        assignments["Alternative Generator"]
    )

    reviewer = OllamaClient(
        assignments["Reviewer"]
    )

    # ------------------------------------
    # Diagnosis Leader
    # ------------------------------------

    primary_diagnosis = (
        leader.generate_json(
            f"""
You are the Diagnosis Leader.

Based on the clinical findings and evidence,
identify the most likely diagnosis.

Return ONLY valid JSON.

{{
    "primary_diagnosis": "",
    "confidence": 0.0,
    "reasoning": []
}}

Stage1 Output:

{json.dumps(stage1, indent=2)}
"""
        )
    )

    # ------------------------------------
    # Alternative Diagnosis Generator
    # ------------------------------------

    alternatives = (
        alternative_generator.generate_json(
            f"""
You are the Alternative Diagnosis Generator.

Suggest alternative diagnoses that should
also be considered.

Return ONLY valid JSON.

{{
    "alternative_diagnoses": []
}}

Stage1 Output:

{json.dumps(stage1, indent=2)}

Primary Diagnosis:

{json.dumps(primary_diagnosis, indent=2)}
"""
        )
    )

    # ------------------------------------
    # Reviewer
    # ------------------------------------

    review = (
        reviewer.generate_json(
            f"""
You are the Diagnosis Reviewer.

Review the proposed diagnosis and
alternative diagnoses.

Return ONLY valid JSON.

{{
    "approved": true,
    "review_comments": [],
    "missing_considerations": []
}}

Primary Diagnosis:

{json.dumps(primary_diagnosis, indent=2)}

Alternatives:

{json.dumps(alternatives, indent=2)}
"""
        )
    )

    return {

        "primary":
            primary_diagnosis,

        "alternatives":
            alternatives,

        "review":
            review
    }