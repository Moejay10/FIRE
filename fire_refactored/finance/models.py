from dataclasses import dataclass, field
from typing import Optional, List
import datetime

@dataclass
class Loan:
    principal: float
    annual_rate: float
    years: int
    start_date: Optional[datetime.date] = None
    name: str = "loan"
    def monthly_rate(self) -> float:
        return self.annual_rate / 12.0
    def months(self) -> int:
        return max(1, self.years * 12)

@dataclass
class Investment:
    principal: float
    annual_return: float
    annual_volatility: float = 0.15
    contributions_per_year: int = 1
    account_type: str = "brokerage"

@dataclass
class Person:
    name: str
    salary: float
    savings_rate: float
    expenses: float
    loans: List[Loan] = field(default_factory=list)
    investments: List[Investment] = field(default_factory=list)
    charity_donation: float = 0.0
    ips_contribution: float = 0.0
