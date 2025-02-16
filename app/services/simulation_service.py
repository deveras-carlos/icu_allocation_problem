from app.models import ScenarioModel
from . import GenerationService
from app.solvers import MGSSolver, LSFSolver, MSFSolver
import random

class SimulationService:
    def __init__(self, generation_service: GenerationService):
        self.generation_service = generation_service

    def simulate(self, num_rounds: int, patient_to_bed_ratios: list[float], epidemic: str = None):
        results = {
            "MSG": [],
            "LSF": [],
            "MSF": [],
            "FCFS": []
        }

        for j in range(1, num_rounds + 1):
            for ratio in patient_to_bed_ratios:
                num_patients = int(sum(self.generation_service.parameters.icu_capacities.values()) * ratio)
                scenario = self.generation_service.generate_scenario(j, num_patients)

                if epidemic:
                    for patient in scenario.patients:
                        sofa_scores = self.generation_service.generate_epidemic_sofa_scores(1, epidemic)
                        patient.sofa_score = sofa_scores[0]

                # Solve using different allocation strategies
                msg_response = MGSSolver(scenario)
                lsf_response = LSFSolver(scenario)
                msf_response = MSFSolver(scenario)
                fcfs_response = self.fcfs_solver(scenario)

                # Simulate survival
                msg_survival = self.simulate_survival(scenario, msg_response.allocation)
                lsf_survival = self.simulate_survival(scenario, lsf_response.allocation)
                msf_survival = self.simulate_survival(scenario, msf_response.allocation)
                fcfs_survival = self.simulate_survival(scenario, fcfs_response.allocation)

                results["MSG"].append(msg_survival)
                results["LSF"].append(lsf_survival)
                results["MSF"].append(msf_survival)
                results["FCFS"].append(fcfs_survival)

        # Average results
        averaged_results = {
            strategy: sum(values) / len(values) for strategy, values in results.items()
        }
        return averaged_results

    def simulate_survival(self, scenario: ScenarioModel, allocation: dict[int, str]) -> int:
        survival_count = 0
        for patient in scenario.patients:
            rand_val = random.uniform(0, 1)
            if rand_val <= patient.survival_prob_out_icu:
                survival_count += 1
            elif rand_val <= patient.survival_prob_in_icu:
                if patient.id in allocation:
                    survival_count += 1
        return survival_count