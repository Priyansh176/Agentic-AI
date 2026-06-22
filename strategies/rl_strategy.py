import json
import random
from pathlib import Path

from strategies.base_strategy import AssignmentStrategy


class RLAssignmentStrategy(AssignmentStrategy):

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

    def __init__(
        self,
        epsilon=0.2,
        alpha=0.1,
        gamma=0.9,
        q_table_path=None
    ):

        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05
        self.alpha = alpha
        self.gamma = gamma
        self.last_actions = {}
        self.episode = []
        self.previous_stage_output = None

        self.q_tables = {

            "symptom_analysis": {},

            "differential_diagnosis": {},

            "treatment_planning": {}
        }

        self.last_actions = {}
        self.last_states = {}

        if q_table_path:
            self.load_q_table(q_table_path)

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

        attack_type = (
            case_data.get(
                "security_scenario",
                {}
            ).get(
                "attack_type",
                "none"
            )
        )

        base_state =  (
            difficulty,
            self._risk_bucket(security_score),
            attack_type
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
                self._risk_bucket(security_score),
                attack_type,
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
                self._risk_bucket(security_score),
                attack_type,
                diagnosis_quality
            )

    def _initialize_state(
        self,
        stage_name,
        state
    ):

        table = self.q_tables[
            stage_name
        ]

        state_key = str(state)

        if state_key not in table:

            table[state_key] = {

                str(action): 0.0

                for action in range(
                    len(
                        self.ROLE_PERMUTATIONS
                    )
                )
            }

    def _choose_action(
        self,
        stage_name,
        state
    ):

        state_key = str(state)

        q_values = self.q_tables[
            stage_name
        ][state_key]

        if random.random() < self.epsilon:

            return random.randint(
                0,
                len(
                    self.ROLE_PERMUTATIONS
                ) - 1
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

        self._initialize_state(
            stage_name,
            state
        )

        action = self._choose_action(
            stage_name,
            state
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

        permutation = (
            self.ROLE_PERMUTATIONS[
                action
            ]
        )

        roles = self.ROLE_MAP[
            stage_name
        ]

        assignment = {}

        for role_index, role in enumerate(
            roles
        ):

            model_index = permutation[
                role_index
            ]

            assignment[
                role
            ] = available_models[
                model_index
            ]

        self.last_states[
            stage_name
        ] = state

        print(f"\n[RL] {stage_name}")       #

        print(f"State: {state}")

        print(f"Action: {action}")          #

        return assignment

    def save_q_table(
        self,
        path
    ):

        Path(
            path
        ).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w"
        ) as f:

            json.dump(
                self.q_tables,
                f,
                indent=2
            )

    def load_q_table(
        self,
        path
    ):

        if not Path(path).exists():
            return

        with open(
            path,
            "r"
        ) as f:

            self.q_tables = json.load(
                f
            )

    def update_q_table(
        self,
        stage_name,
        reward
    ):

        state = self.last_states[
            stage_name
        ]

        action = self.last_actions[
            stage_name
        ]

        state_key = str(state)

        current_q = self.q_tables[
            stage_name
        ][state_key][str(action)]

        updated_q = current_q + (
            self.alpha * (reward - current_q)
        )

        self.q_tables[stage_name][state_key][str(action)] = updated_q

    def learn(
        self,
        metrics
    ):

        reward = (
            0.4 * metrics.get("diagnosis_correct",0.0) + 0.3 * metrics.get("treatment_f1_score", 0.0) + 0.3 *(1 - metrics.get("security_failure", 0))
        )

        for stage in [
            "symptom_analysis",
            "differential_diagnosis",
            "treatment_planning"
        ]:
            
            self.epsilon = max(
                self.min_epsilon,
                self.epsilon * self.epsilon_decay
            )
            self.update_q_table(
                stage,
                reward
            )

        return reward
    
    def learn_stage_rewards(self, metrics):

        diagnosis_correct = metrics.get(
            "diagnosis_correct",
            0
        )

        treatment_f1 = metrics.get(
            "treatment_f1_score",
            metrics.get("treatment_f1", 0.0)
        )

        security_failure = metrics.get(
            "security_failure",
            0
        )

        symptom_reward = (
            0.7 * (1 - security_failure) + 0.3 * diagnosis_correct
        )

        diagnosis_reward = (
            0.8 * diagnosis_correct + 0.2 * treatment_f1
        )

        treatment_reward = (
            0.7 * treatment_f1 + 0.3 * (1 - security_failure)
        )

        rewards = {
            "symptom_analysis": symptom_reward,
            "differential_diagnosis": diagnosis_reward,
            "treatment_planning": treatment_reward
        }

        for stage, reward in rewards.items():

            if stage not in self.last_actions:
                continue

            state, action = self.last_actions[stage]

            state_key = str(state)

            current_q = self.q_tables[stage][state_key][str(action)]

            updated_q = current_q + (
                self.alpha *
                (reward - current_q)
            )

            self.q_tables[stage][state_key][str(action)] = updated_q

        self.save_q_table("logs/rl/q_table.json")

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

        print(                          #
            f"Reward={reward:.3f} "
            f"Target={target:.3f}"
        )                               #

    def learn_episode(
        self,
        metrics
    ):

        diagnosis_correct = metrics.get(
            "diagnosis_correct",
            0
        )

        treatment_f1 = metrics.get(
            "treatment_f1_score",
            metrics.get("treatment_f1", 0.0)
        )

        security_failure = metrics.get(
            "security_failure",
            0
        )

        symptom_reward = (
            0.7 * (1-security_failure) + 0.3 * diagnosis_correct
        )

        diagnosis_reward = (
            0.8 * diagnosis_correct + 0.2 * treatment_f1
        )

        treatment_reward = (
            0.7 * treatment_f1 + 0.3 * (1-security_failure)
        )

        s1 = self.episode[0]
        s2 = self.episode[1]
        s3 = self.episode[2]

        self.update_q_value(
            s3["stage"],
            s3["state"],
            s3["action"],
            treatment_reward,
            None
        )

        self.update_q_value(
            s2["stage"],
            s2["state"],
            s2["action"],
            diagnosis_reward,
            s3["state"],
            s3["stage"]
        )

        self.update_q_value(
            s1["stage"],
            s1["state"],
            s1["action"],
            symptom_reward,
            s2["state"],
            s2["stage"]
        )

        self.save_q_table("logs/rl/q_table.json")

        print(f"Epsilon = {self.epsilon:.4f}")      #

        self.epsilon = max(
            self.min_epsilon,
            self.epsilon * self.epsilon_decay
        )
        self.episode = []

    def update_stage_output(
        self,
        output
    ):
        self.previous_stage_output = output