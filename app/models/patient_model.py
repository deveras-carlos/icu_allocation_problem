from dataclasses import dataclass
from . import SOFAScoreModel

@dataclass
class PatientModel:
    id                          : int
    sofa_score                  : SOFAScoreModel
    survival_prob_in_icu        : float
    survival_prob_out_icu       : float
    days_of_occupancy           : dict[ str, int ]  # Days required per ICU type