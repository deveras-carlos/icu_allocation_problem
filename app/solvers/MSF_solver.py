from app.models import ScenarioModel, ICUAllocationResponseModel
from gurobipy import Model, GRB, quicksum

def MSFSolver( scenario: ScenarioModel ) -> ICUAllocationResponseModel:
    model = Model(  )

    patients = scenario.patients
    params = scenario.parameters

    # Decision variables
    x = {
        ( p.id, icu_type ): model.addVar( vtype = GRB.BINARY, name = f"x_{p.id}_{icu_type}" )
        for p in patients for icu_type in params.icu_capacities.keys(  )
    }
    
    theta = model.addVar( lb = 0, vtype = GRB.CONTINUOUS, name = "theta" )

    # Constraints
    for icu_type in params.icu_capacities:
        model.addConstr( 
            quicksum( x[p.id, icu_type] for p in patients ) <= params.icu_capacities[icu_type],
            name = f"capacity_{icu_type}"
         )

    for p in patients:
        model.addConstr( 
            quicksum( x[p.id, icu_type] for icu_type in params.icu_capacities.keys(  ) ) <= 1,
            name = f"one_allocation_{p.id}"
         )

    # Penalty for occupancy deviation
    total_allocated = quicksum( x[p.id, icu_type] for p in patients for icu_type in params.icu_capacities.keys(  ) )
    total_capacity = sum( params.icu_capacities.values(  ) )
    model.addConstr( ( total_allocated / total_capacity - params.ideal_occupancy_rate ) + theta >= 0, "occupancy_penalty" )

    # Objective function components
    survival_in_icu = quicksum( x[p.id, icu_type] * p.survival_prob_in_icu for p in patients for icu_type in params.icu_capacities.keys(  ) )
    survival_out_icu = quicksum( ( 1 - quicksum( x[p.id, icu_type] for icu_type in params.icu_capacities.keys(  ) ) ) * p.survival_prob_out_icu for p in patients )
    occupancy_penalty = params.penalty_multiplier * theta
    cost = quicksum( x[p.id, icu_type] * p.days_of_occupancy[icu_type] * params.daily_costs[icu_type] for p in patients for icu_type in params.icu_capacities.keys(  ) )

    model.setObjective( survival_in_icu - occupancy_penalty - cost, GRB.MINIMIZE )

    # Solve model
    model.optimize(  )

    # Extract results
    allocation = {}
    if model.status == GRB.OPTIMAL:
        for p in patients:
            for icu_type in params.icu_capacities.keys(  ):
                if x[p.id, icu_type].x > 0.5:
                    allocation[p.id] = icu_type

    response = ICUAllocationResponseModel( 
        total_survival_in_icu=survival_in_icu.getValue(  ),
        total_survival_out_icu=survival_out_icu.getValue(  ),
        total_cost=cost.getValue(  ),
        allocation=allocation
     )

    return response