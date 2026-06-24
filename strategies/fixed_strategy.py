from strategies.base_strategy import AssignmentStrategy


class FixedAssignmentStrategy(
    AssignmentStrategy
):

    def __init__(self):

        self.mapping = {

            "symptom_analysis": {

                "Interpreter":
                    "llama3.1:8b",

                "Evidence Collector":
                    "mistral:latest",

                "Validator":
                    "gemma3:4b"
            },

            "differential_diagnosis": {

                "Diagnosis Leader":
                    "llama3.1:8b",

                "Alternative Generator":
                    "mistral:latest",

                "Reviewer":
                    "gemma3:4b"
            },

            "treatment_planning": {

                "Planner":
                    "llama3.1:8b",

                "Risk Assessor":
                    "mistral:latest",

                "Validator":
                    "gemma3:4b"
            }
        }

    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):

        if stage_name not in self.mapping:
            raise KeyError(
                f"Unknown stage: {stage_name}"
            )

        assignments = self.mapping[stage_name]
        missing_models = [
            model
            for model in assignments.values()
            if model not in available_models
        ]

        if missing_models:
            raise ValueError(
                "Fixed assignment references unavailable models: "
                + ", ".join(missing_models)
            )

        return dict(assignments)