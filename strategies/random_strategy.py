import random

from strategies.base_strategy import AssignmentStrategy


class RandomAssignmentStrategy(AssignmentStrategy):

    def __init__(self, seed=42):

        self.rng = random.Random(seed)

        self.stage_roles = {
            "symptom_analysis": [
                "Interpreter",
                "Evidence Collector",
                "Validator"
            ],
            "differential_diagnosis": [
                "Diagnosis Leader",
                "Alternative Generator",
                "Reviewer"
            ],
            "treatment_planning": [
                "Planner",
                "Risk Assessor",
                "Validator"
            ]
        }

    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):

        if stage_name not in self.stage_roles:

            raise ValueError(
                f"Unknown stage: {stage_name}"
            )

        models = list(
            available_models.keys()
        )

        roles = self.stage_roles[
            stage_name
        ]

        if len(models) < len(roles):

            raise ValueError(
                f"Need at least {len(roles)} models "
                f"for stage {stage_name}"
            )

        selected_models = self.rng.sample(
            models,
            len(roles)
        )

        return {
            role: model
            for role, model in zip(
                roles,
                selected_models
            )
        }