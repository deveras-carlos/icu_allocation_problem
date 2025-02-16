from dataclasses import dataclass

@dataclass
class ParametersModel:
    id                          : int
    icu_capacities              : dict[ str, int ]                      # Standard capacity for each ICU type
    ideal_occupancy_rate        : float                                 # Ideal ICU occupancy rate (0-1)
    daily_costs                 : dict[ str, float ]                    # Daily cost per ICU type
    penalty_multiplier          : float                                 # Penalty for occupancy deviation
    sofa_to_survival_in_icu     : dict[ int, str ]                      # Survival chance mapping for SOFA score
    sofa_to_survival_out_icu    : list[ dict[ str, str ] ]              # Survival chance outside ICU based on questions
    sofa_weights                : dict[ str, list[ float ] ] = None     # Weights for generating SOFA scores
    epidemic_weights            : dict[ str, list[ float ] ] = None     # Weights for generating epidemic SOFA scores

    def __post_init__(self):
        if self.sofa_weights is None:
            self.sofa_weights = {
                "respiration": [ 0.4, 0.3, 0.2, 0.05, 0.05 ],
                "coagulation": [ 0.5, 0.3, 0.15, 0.04, 0.01 ],
                "liver": [ 0.6, 0.2, 0.15, 0.04, 0.01 ],
                "cardiovascular": [ 0.5, 0.2, 0.2, 0.07, 0.03 ],
                "cns": [ 0.6, 0.25, 0.1, 0.04, 0.01 ],
                "renal": [ 0.5, 0.3, 0.15, 0.04, 0.01 ]
            }
        if self.epidemic_weights is None:
            self.epidemic_weights = {
                "respiration": [ 0.1, 0.2, 0.3, 0.3, 0.1 ],
                "renal": [ 0.1, 0.2, 0.3, 0.3, 0.1 ]
            }