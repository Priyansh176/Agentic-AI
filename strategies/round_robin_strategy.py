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


class RoundRobinAssignmentStrategy(
    AssignmentStrategy
):

    def __init__(
        self
    ):

        self.rotation_index = 0

    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):

        roles = STAGE_ROLES[stage_name]

        rotation = (
            self.rotation_index % len(
                available_models
            )
        )

        assignment = {}

        for index, role in enumerate(
            roles
        ):

            model = available_models[(index + rotation) % len(available_models)]

            assignment[role] = model

        if stage_name == "treatment_planning":
            self.rotation_index += 1

        return assignment