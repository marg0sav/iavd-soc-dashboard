from abc import ABC, abstractmethod
import pandas as pd

class SocInferenceService(ABC):
    @abstractmethod
    def predict(self, incident_id: str, features: pd.DataFrame):
        pass