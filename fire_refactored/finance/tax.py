from dataclasses import dataclass, field
from typing import List
@dataclass
class TaxConfig:
    ordinary_tax_rate: float = 0.22
    social_security_rate: float = 0.079
    bracket_thresholds: List[float] = field(default_factory=lambda: [217400, 306050, 697150, 942400, 1410750])
    bracket_rates: List[float] = field(default_factory=lambda: [0.0, 0.017, 0.04, 0.137, 0.167, 0.177])
    wealth_threshold_single: float = 1760000.0
    wealth_state_rate: float = 0.00475
    wealth_state_rate_high: float = 0.00575
    municipal_wealth_rate: float = 0.0075
    capital_gains_tax_rate: float = 0.22
    ips_contribution_limit: float = 15000.0
    charity_deduction_limit: float = 50000.0

class TaxEngine:
    def __init__(self, config: TaxConfig):
        self.cfg = config
    def bracket_tax(self, personal_income: float) -> float:
        thresholds = [0] + self.cfg.bracket_thresholds + [float('inf')]
        rates = self.cfg.bracket_rates
        tax = 0.0
        for i in range(len(rates)):
            lower = thresholds[i]
            upper = thresholds[i+1]
            if personal_income <= lower:
                break
            taxable = max(0.0, min(personal_income, upper) - lower)
            tax += taxable * rates[i]
        return tax
    def income_tax(self, personal_income: float, deductions: float = 0.0) -> float:
        taxable_income = max(0.0, personal_income - deductions)
        ordinary = taxable_income * self.cfg.ordinary_tax_rate
        ss = personal_income * self.cfg.social_security_rate
        bracket = self.bracket_tax(taxable_income)
        return ordinary + ss + bracket
    def wealth_tax(self, net_wealth: float, is_high=False) -> float:
        base = max(0.0, net_wealth - self.cfg.wealth_threshold_single)
        state_rate = self.cfg.wealth_state_rate_high if (is_high and net_wealth>20_700_000) else self.cfg.wealth_state_rate
        return base * (state_rate + self.cfg.municipal_wealth_rate)
    def capital_gains_tax(self, gain: float) -> float:
        return max(0.0, gain) * self.cfg.capital_gains_tax_rate
    def net_salary(self, gross_salary: float, deductions: float = 0.0) -> float:
        income_tax = self.income_tax(gross_salary, deductions=deductions)
        return gross_salary - income_tax
