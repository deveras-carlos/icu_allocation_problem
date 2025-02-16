from app.models import ScenarioModel, ICUAllocationResponseModel

def FCFSSolver(scenario: ScenarioModel) -> ICUAllocationResponseModel:
    allocation = {}
    icu_capacities = scenario.parameters.icu_capacities.copy()

    for patient in scenario.patients:
        for icu_type in icu_capacities:
            if icu_capacities[icu_type] > 0:
                allocation[patient.id] = icu_type
                icu_capacities[icu_type] -= 1
                break

    total_survival_in_icu = sum(
        patient.survival_prob_in_icu
        for patient in scenario.patients
        if patient.id in allocation
    )
    total_survival_out_icu = sum(
        patient.survival_prob_out_icu
        for patient in scenario.patients
        if patient.id not in allocation
    )
    total_cost = sum(
        patient.days_of_occupancy[allocation[patient.id]] * scenario.parameters.daily_costs[allocation[patient.id]]
        for patient in scenario.patients
        if patient.id in allocation
    )

    return ICUAllocationResponseModel(
        total_survival_in_icu=total_survival_in_icu,
        total_survival_out_icu=total_survival_out_icu,
        total_cost=total_cost,
        allocation=allocation
    )
