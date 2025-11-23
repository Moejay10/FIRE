from typing import List, Dict
from .models import Loan

def annuity_payment(principal: float, annual_rate: float, years: int) -> float:
    if annual_rate == 0 or years == 0:
        return principal / max(1, years*12)
    r = annual_rate / 12.0
    n = years * 12
    payment = principal * (r * (1+r)**n) / ((1+r)**n - 1)
    return payment

def amortization_schedule(loan: Loan) -> List[Dict]:
    payment = annuity_payment(loan.principal, loan.annual_rate, loan.years)
    balance = loan.principal
    schedule = []
    for m in range(1, loan.months()+1):
        interest = balance * (loan.annual_rate / 12.0)
        principal_paid = min(balance, payment - interest)
        balance = balance - principal_paid
        schedule.append({'month': m-1, 'payment': payment if balance>0 else principal_paid+interest, 'interest': interest, 'principal': principal_paid, 'balance': max(0.0, balance)})
        if balance <= 0:
            break
    return schedule
