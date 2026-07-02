import json
from pathlib import Path
from strategies.base_strategy import AssignmentStrategy

STAGE_ROLES = {

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


class GreedyAssignmentStrategy(
    AssignmentStrategy
):

    def __init__(
        self,
        available_models,
        profile_path=None
    ):

        self.profile_path = profile_path

        self.model_profiles = {

            model: {

                "Interpreter": 0.5,
                "Evidence Collector": 0.5,
                "Validator": 0.5,

                "Diagnosis Leader": 0.5,
                "Alternative Generator": 0.5,
                "Reviewer": 0.5,

                "Planner": 0.5,
                "Risk Assessor": 0.5,

                "assignments": 0

            }

            for model in available_models
        }

        if self.profile_path:
            self.load_profiles(self.profile_path)

    def _role_score(
        self,
        profile,
        role
    ):

        return profile[role]

    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):
                                     
        roles = STAGE_ROLES[stage_name]

        unused_models = set(available_models)

        assignment = {}

        for role in roles:

            best_model = max(

                unused_models,

                key=lambda model:

                self._role_score(
                    self.model_profiles[model],
                    role
                )
            )

            assignment[role] = best_model

            unused_models.remove(best_model)

        return assignment

    def save_profiles(
        self,
        path
    ):

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(path, "w") as f:
            json.dump(
                self.model_profiles,
                f,
                indent=2
            )

    def load_profiles(
        self,
        path
    ):

        if not Path(path).exists():
            return

        with open(path, "r") as f:
            self.model_profiles = json.load(f)

        print(
            "Loaded existing greedy model profiles."
        )

    def update_profiles(
        self,
        result,
        metrics
    ):

        diagnosis_reward = max(
            0.3,
            metrics.get("diagnosis_score", 0.0)
        )

        security_reward = max(
            0.3,
            metrics.get("security_score", 0)
        )

        treatment_reward = max(
            0.3,
            metrics.get("clinical_treatment_score", 0.0)
        )

        for trace in result.get(
            "trace",
            []
        ):

            role = trace["role"]
            model = trace["model"]

            profile = self.model_profiles[model]

            old_score = profile[role]

            if role in {
                "Diagnosis Leader",
                "Alternative Generator",
                "Reviewer"
            }:

                reward = diagnosis_reward

            elif role in {
                "Validator",
                "Risk Assessor"
            }:

                reward = security_reward

            elif role in {
                "Planner"
            }:

                reward = treatment_reward

            else:
                reward = (diagnosis_reward + treatment_reward) / 2

            profile[role] = (old_score * 0.8 + reward * 0.2)

            profile["assignments"] += 1

            if (self.profile_path and profile["assignments"] % 20 == 0):
                self.save_profiles(self.profile_path)