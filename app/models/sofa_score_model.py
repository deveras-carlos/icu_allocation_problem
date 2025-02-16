from dataclasses import dataclass

@dataclass
class SOFAScoreModel:
    respiration         : int  # PaO2/FiO2 mmHg
    coagulation         : int  # Platelets x10^3/mm^3
    liver               : int  # Bilirubin mg/dL
    cardiovascular      : int  # Hypotension/Medication level
    cns                 : int  # Glasgow Coma Score
    renal               : int  # Creatinine mg/dL or Urine output

    def total_score(self) -> int:
        return self.respiration + self.coagulation + self.liver + self.cardiovascular + self.cns + self.renal