from abc import ABC, abstractmethod


class AssignmentStrategy(ABC):

    @abstractmethod
    def assign_roles(
        self,
        stage_name,
        available_models,
        case_data=None
    ):
        pass
    
    def update_profiles(
        self,
        result,
        metrics
    ):
        pass