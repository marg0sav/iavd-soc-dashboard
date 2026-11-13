from dataclasses import dataclass


@dataclass(frozen=True)
class SocModelInferenceResult:
    incident_id: str
    verdict: str
    probability: float
