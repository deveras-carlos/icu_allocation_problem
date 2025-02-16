from dataclasses import dataclass

@dataclass
class ICUAllocationResponseModel:
    id                      : int
    total_survival_in_icu   : int
    total_survival_out_icu  : int
    total_cost              : int
    allocation              : dict[ int, str ]  # Patient ID to ICU type mapping