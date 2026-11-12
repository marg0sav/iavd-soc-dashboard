from dataclasses import dataclass

@dataclass(frozen=True)
class InferenceResult:
    incident_id: str
    verdict: str
    probability: float