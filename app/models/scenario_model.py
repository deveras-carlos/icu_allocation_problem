from dataclasses import dataclass
from . import ParametersModel, PatientModel

@dataclass
class ScenarioModel:
    id          : int
    patients    : list[ PatientModel ]
    parameters  : ParametersModel