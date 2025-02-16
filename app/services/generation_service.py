from app.models import SOFAScoreModel, ParametersModel, PatientModel, ScenarioModel
import random
from dataclasses import dataclass

@dataclass
class SOFAScoreModel:
    respiration: int  # PaO2/FiO2 mmHg
    coagulation: int  # Platelets x10^3/mm^3
    liver: int  # Bilirubin mg/dL
    cardiovascular: int  # Hypotension/Medication level
    cns: int  # Glasgow Coma Score
    renal: int  # Creatinine mg/dL or Urine output

    def total_score(self) -> int:
        return self.respiration + self.coagulation + self.liver + self.cardiovascular + self.cns + self.renal

@dataclass
class PatientModel:
    id: int
    sofa_score: SOFAScoreModel
    survival_prob_in_icu: float
    survival_prob_out_icu: float
    days_of_occupancy: dict[str, int]  # Days required per ICU type
    is_burn_patient: bool  # Flag to indicate burn status
    burn_priority_icu: int = 0  # Calculated ICU priority for burns
    burn_priority_non_icu: int = 0  # Calculated non-ICU priority for burns

class GenerationService:
    def __init__(self, parameters: ParametersModel):
        self.parameters = parameters

    def generate_random_sofa_score(self) -> SOFAScoreModel:
        return SOFAScoreModel(
            respiration=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["respiration"]
            )[0],
            coagulation=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["coagulation"]
            )[0],
            liver=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["liver"]
            )[0],
            cardiovascular=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["cardiovascular"]
            )[0],
            cns=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["cns"]
            )[0],
            renal=random.choices(
                [0, 1, 2, 3, 4], weights=self.parameters.sofa_weights["renal"]
            )[0],
        )

    def calculate_burn_priority(self, patient: PatientModel, act: float, critical_areas: bool):
        """Calculate ICU and non-ICU burn priorities for a patient."""
        # ICU Burn Priority
        burn_priority_icu = 0

        # ACT contribution to ICU priority
        if act > 40:
            burn_priority_icu += 5
        elif 20 <= act <= 40:
            burn_priority_icu += 3
        else:
            burn_priority_icu += 1

        # Critical areas contribution
        if critical_areas:
            burn_priority_icu += 1

        # SOFA score contribution
        sofa_total = patient.sofa_score.total_score()
        if sofa_total <= 5:
            burn_priority_icu += 1
        elif 6 <= sofa_total <= 9:
            burn_priority_icu += 2
        elif 10 <= sofa_total <= 11:
            burn_priority_icu += 3
        else:
            burn_priority_icu += 4

        # Ventilation/vasopressors contribution (assuming patient needs support)
        if patient.sofa_score.respiration >= 3:
            burn_priority_icu += 1
        if patient.sofa_score.cardiovascular >= 3:
            burn_priority_icu += 1

        burn_priority_icu = min(burn_priority_icu, 5)  # Cap at 5

        # Non-ICU Burn Priority
        if patient.survival_prob_out_icu == "very low":
            burn_priority_non_icu = 1  # ICU essential
        elif sofa_total <= 5 and not critical_areas:
            burn_priority_non_icu = 5  # Manageable outside ICU
        elif 6 <= sofa_total <= 9:
            burn_priority_non_icu = 3
        else:
            burn_priority_non_icu = 2

        patient.burn_priority_icu = burn_priority_icu
        patient.burn_priority_non_icu = burn_priority_non_icu

    def generate_patient(self, patient_id: int, is_burn_patient: bool = False, act: float = 0.0, critical_areas: bool = False) -> PatientModel:
        sofa_score = self.generate_random_sofa_score()
        survival_prob_in_icu = self.parameters.sofa_to_survival_in_icu[sofa_score.total_score()]
        survival_prob_out_icu = self.parameters.sofa_to_survival_out_icu[sofa_score.total_score()]
        days_of_occupancy = {
            icu_type: random.randint(1, 10)
            for icu_type in self.parameters.icu_capacities.keys()
        }

        patient = PatientModel(
            id=patient_id,
            sofa_score=sofa_score,
            survival_prob_in_icu=survival_prob_in_icu,
            survival_prob_out_icu=survival_prob_out_icu,
            days_of_occupancy=days_of_occupancy,
            is_burn_patient=is_burn_patient,
        )

        if is_burn_patient:
            self.calculate_burn_priority(patient, act, critical_areas)

        return patient

    def generate_scenario(self, scenario_id: int, num_patients: int) -> ScenarioModel:
        patients = [
            self.generate_patient(patient_id=i, is_burn_patient=random.choice([True, False]), act=random.uniform(5, 60), critical_areas=random.choice([True, False]))
            for i in range(1, num_patients + 1)
        ]
        return ScenarioModel(id=scenario_id, patients=patients, parameters=self.parameters)
