from .models import Investment, Loan, Person
from .loans import amortization_schedule
from .tax import TaxEngine, TaxConfig
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from tabulate import tabulate

def real_value(nominal, inflation_rate, years):
    return [v / ((1+inflation_rate)**y) for y,v in enumerate(nominal, start=1)]

class Simulation:
    def __init__(self, tax_config: TaxConfig = None):
        self.tax_engine = TaxEngine(tax_config or TaxConfig())
        self.cfg = tax_config or TaxConfig()
    def project_yearly(self, person: Person, years: int = 30, inflation: float = 0.02) -> pd.DataFrame:
        rows = []
        assets_by_account = { 'brokerage': sum(inv.principal for inv in person.investments if inv.account_type=='brokerage'),
                              'ASK': sum(inv.principal for inv in person.investments if inv.account_type=='ASK'),
                              'IPS': sum(inv.principal for inv in person.investments if inv.account_type=='IPS') }
        debts = sum(loan.principal for loan in person.loans)
        cumulative_contrib = 0.0
        for year in range(1, years+1):
            gross = person.salary
            ips_deduction = min(person.ips_contribution, self.cfg.ips_contribution_limit)
            charity_deduction = min(person.charity_donation, self.cfg.charity_deduction_limit)
            deductions = ips_deduction + charity_deduction
            saved = gross * person.savings_rate
            cumulative_contrib += saved
            total_assets = sum(assets_by_account.values())
            if total_assets <= 0:
                assets_by_account['brokerage'] += saved
            else:
                for k in assets_by_account.keys():
                    assets_by_account[k] += saved * (assets_by_account[k] / total_assets)
            # growth
            for inv in person.investments:
                assets_by_account[inv.account_type] *= (1 + inv.annual_return)
            # loan amortization simplified
            for loan in person.loans:
                schedule = amortization_schedule(loan)
                principal_paid = sum(item['principal'] for item in schedule[:12])
                loan.principal = max(0.0, loan.principal - principal_paid)
            debts = sum(loan.principal for loan in person.loans)
            net_wealth = sum(assets_by_account.values()) - debts
            income_tax = self.tax_engine.income_tax(gross, deductions=deductions)
            net_salary = gross - income_tax
            wealth_tax = self.tax_engine.wealth_tax(net_wealth)
            rows.append({
                'year': year,
                'assets_brokerage': assets_by_account['brokerage'],
                'assets_ASK': assets_by_account['ASK'],
                'assets_IPS': assets_by_account['IPS'],
                'total_assets': sum(assets_by_account.values()),
                'debt': debts,
                'net_wealth': net_wealth,
                'gross_salary': gross,
                'deductions': deductions,
                'income_tax': income_tax,
                'net_salary': net_salary,
                'wealth_tax': wealth_tax,
                'saved': saved,
                'cumulative_contrib': cumulative_contrib
            })
        df = pd.DataFrame(rows)
        df['real_net_wealth'] = [v / ((1+inflation)**i) for i,v in enumerate(df['net_wealth'].tolist(), start=1)]
        return df
    def realize_and_tax(self, df: pd.DataFrame, realize_ask: float = 0.0, realize_brokerage: float = 0.0, realize_ips_withdraw: float = 0.0) -> Dict[str, float]:
        final = df.iloc[-1]
        results = {}
        total_assets = final['total_assets']
        total_contrib = final['cumulative_contrib']
        total_gain = max(0.0, total_assets - total_contrib)
        tax_ask = tax_brokerage = tax_ips = 0.0
        if realize_ask>0:
            ask_balance = final['assets_ASK']
            ask_contrib_share = total_contrib * (ask_balance/total_assets) if total_assets>0 else 0
            ask_gain = max(0.0, min(realize_ask, ask_balance) - ask_contrib_share)
            tax_ask = self.tax_engine.capital_gains_tax(ask_gain)
        if realize_brokerage>0:
            br_balance = final['assets_brokerage']
            br_contrib_share = total_contrib * (br_balance/total_assets) if total_assets>0 else 0
            br_gain = max(0.0, min(realize_brokerage, br_balance) - br_contrib_share)
            tax_brokerage = self.tax_engine.capital_gains_tax(br_gain)
        if realize_ips_withdraw>0:
            tax_ips = self.tax_engine.income_tax(realize_ips_withdraw)
        results['tax_ask'] = tax_ask
        results['tax_brokerage'] = tax_brokerage
        results['tax_ips'] = tax_ips
        results['total_tax_on_realization'] = tax_ask + tax_brokerage + tax_ips
        results['total_gain'] = total_gain
        return results
    def format_table(self, df: pd.DataFrame, maxrows: int = 10) -> str:
        head = df.head(maxrows)
        return tabulate(head, headers='keys', tablefmt='psql', floatfmt=".0f")
