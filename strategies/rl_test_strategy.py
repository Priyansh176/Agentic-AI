import json
import random
from pathlib import Path

from strategies.rl_strategy import RLAssignmentStrategy


class RLTestAssignmentStrategy(RLAssignmentStrategy):

    ROLE_MAP = {
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

    ROLE_PERMUTATIONS = [

        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0)
    ]

    def __init__(self, q_table_path):

        super().__init__(
            epsilon=0.0,
            training=False,
            q_table_path=q_table_path
        )

        print("\n========== RL TEST MODE ==========")
        print("Q-table frozen")
        print("Exploration disabled")
        print("==================================\n")

    def _risk_bucket(
        self,
        score
    ):

        if score <= 3:
            return "low"

        if score <= 6:
            return "medium"

        return "high"

    def _build_state(
        self,
        case_data,
        stage_name=None,
        stage_output=None
    ):

        if case_data is None:
            return (
                "unknown",
                "low",
                "none"
            )

        difficulty = case_data.get(
            "difficulty_level",
            "unknown"
        )

        security_score = case_data.get(
            "security_risk_score",
            0
        )

        base_state = (
            difficulty,
            self._risk_bucket(
                security_score
            )
        )

        if stage_name == "symptom_analysis":
            return base_state
        
        if stage_name == "differential_diagnosis":
            symptom_quality = (
                stage_output.get(
                    "symptom_quality",
                    "unknown"
                )
                if stage_output
                else "unknown"
            )

            return (
                difficulty,
                self._risk_bucket(
                    security_score
                ),
                symptom_quality
            )

        if stage_name == "treatment_planning":
            diagnosis_quality = (
                stage_output.get(
                    "diagnosis_quality",
                    "unknown"
                )
                if stage_output
                else "unknown"
            )

            return (
                difficulty,
                self._risk_bucket(
                    security_score
                ),
                diagnosis_quality
            )

    def _initialize_state(
        self,
        stage_name,
        state
    ):

        table = self.q_tables[stage_name]
        state_key = str(state)

        if state_key not in table:
            table[state_key] = {
                str(action): 0.0
                for action in range(
                    len(self.ROLE_PERMUTATIONS)
                )
            }

    def _choose_action(
        self,
        stage_name,
        state
    ):

        state_key = str(state)
        q_values = self.q_tables[stage_name][state_key]

        if self.training:
            if random.random() < self.epsilon:
                return random.randint(
                    0,
                    len(self.ROLE_PERMUTATIONS) - 1
                )

        best_value = max(
            q_values.values()
        )

        best_actions = [
            int(action)

            for action, value
            in q_values.items()

            if value == best_value
        ]

        return random.choice(
            best_actions
        )

    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):

        state = self._build_state(
            case_data,
            stage_name,
            self.previous_stage_output
        )

        state_key = str(state)

        if state_key in self.q_tables[stage_name]:

            action = self._choose_action(
                stage_name,
                state
            )

        else:

            print(
                f"[TEST] Unseen state {state}"
            )

            action = self.default_action(
                stage_name
            )

        self.episode.append({
            "stage": stage_name,
            "state": state,
            "action": action
        })

        self.last_actions[stage_name] = (
            state,
            action
        )

        action = int(action)

        permutation = (self.ROLE_PERMUTATIONS[action])

        roles = self.ROLE_MAP[stage_name]

        assignment = {}

        for role_index, role in enumerate(roles):
            model_index = permutation[role_index]
            assignment[role] = available_models[model_index]

        self.last_states[stage_name] = state

        print(f"\n[RL] {stage_name}")       #
        print(f"State: {state}")
        print(f"Action: {action}")          #

        return assignment

    def save_q_table(
        self,
        path
    ):
        return

    def load_q_table(
        self,
        path
    ):

        if not Path(path).exists():
            return

        with open(path, "r") as f:
            data = json.load(f)

        if "q_tables" in data:
            self.q_tables = data["q_tables"]

            metadata = data.get("metadata", {})

            self.epsilon = metadata.get(
                "epsilon",
                self.epsilon
            )
            self.alpha = metadata.get(
                "alpha",
                self.alpha
            )
            self.gamma = metadata.get(
                "gamma",
                self.gamma
            )
            self.reward_history = []
            self.cumulative_rewards = []
        else:
            self.q_tables = data

        self.total_episodes = 0

        if not self.training:
            self.epsilon = 0.0

        print(                                          #
            f"Loaded epsilon={self.epsilon:.4f}, "
            f"episodes={self.total_episodes}"
        )                                               #

    def update_q_value(
        self,
        stage,
        state,
        action,
        reward,
        next_state=None,
        next_stage=None
    ):

        state_key = str(state)

        current_q = self.q_tables[stage][state_key][str(action)]

        if next_state is None:
            target = reward

        else:
            next_key = str(next_state)

            max_future_q = max(
                self.q_tables[next_stage]
                .get(next_key, {})
                .values(),
                default=0.0
            )

            target = reward + (
                self.gamma *
                max_future_q
            )

        new_q = current_q + (self.alpha * (target - current_q))

        self.q_tables[stage][state_key][str(action)] = new_q

        # print(                          #
        #     f"Reward={reward:.3f} "
        #     f"Target={target:.3f}"
        # )                               #

    def learn_episode(
        self,
        metrics
    ):
        return

    def update_stage_output(
        self,
        output
    ):
        self.previous_stage_output = output
    
    def default_action(
        self,
        stage_name
    ):

        table = self.q_tables[stage_name]

        if not table:
            return 0

        averages = {}

        for action in range(
            len(self.ROLE_PERMUTATIONS)
        ):

            values = []

            for state in table.values():

                values.append(
                    state[str(action)]
                )

            averages[action] = (
                sum(values) /
                len(values)
            )

        return max(
            averages,
            key=averages.get
        )