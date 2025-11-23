"""
Full Streamlit app with account-type realism (ASK/IPS), brutto/netto, deductions, inflation,
Plotly visualizations, tabulate formatted tables, multiple strategies and Excel export.
Run: streamlit run streamlit_full.py
"""
import streamlit as st
import pandas as pd, numpy as np, io, yaml, os
import plotly.graph_objects as go
from finance.models import Person, Loan, Investment
from finance.simulation import Simulation
from finance.tax import TaxConfig
from datetime import datetime
from tabulate import tabulate

st.set_page_config(page_title="FIRE Simulator — Advanced", layout="wide")
st.title("FIRE Simulator — Advanced (ASK, IPS, Deductions, Inflation)")

def load_config(path="config_example.yaml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except:
        return {}

cfg = load_config("config_example.yaml")
tax_cfg = TaxConfig(
    ordinary_tax_rate=cfg.get("ordinary_tax_rate", 0.22),
    social_security_rate=cfg.get("social_security_rate", 0.079),
    bracket_thresholds=cfg.get("bracket_thresholds", []),
    bracket_rates=cfg.get("bracket_rates", []),
    wealth_threshold_single=cfg.get("wealth_threshold_single", 1760000),
    wealth_state_rate=cfg.get("wealth_state_rate", 0.00475),
    wealth_state_rate_high=cfg.get("wealth_state_rate_high", 0.00575),
    municipal_wealth_rate=cfg.get("municipal_wealth_rate", 0.0075),
    capital_gains_tax_rate=cfg.get("capital_gains_tax_rate", 0.22),
    ips_contribution_limit=cfg.get("ips_contribution_limit", 15000),
    charity_deduction_limit=cfg.get("charity_deduction_limit", 50000)
)

# Sidebar controls
st.sidebar.header("Simulation controls")
years = st.sidebar.slider("Projection years", 1, 60, 30)
monthly = st.sidebar.checkbox("Monthly simulation (vs yearly)", value=False)
inflation = st.sidebar.number_input("Annual inflation (decimal)", 0.02, step=0.001)
compare = st.sidebar.checkbox("Compare strategy/scenario B", value=False)

# Strategy presets
st.sidebar.header("Strategy presets")
strategy = st.sidebar.selectbox("Choose strategy", ["Base", "Aggressive invest", "Pay down debt", "Frugal (cut expenses)"])
extra_savings_pct = 0.0
if strategy == "Aggressive invest":
    extra_savings_pct = 0.1
elif strategy == "Pay down debt":
    extra_savings_pct = -0.05
elif strategy == "Frugal (cut expenses)":
    extra_savings_pct = 0.05

# Inputs for scenario A (primary)
st.header("Scenario A inputs")
name = st.text_input("Name", "Alice", key="nameA")
salary = st.number_input("Gross annual salary (NOK)", 600000.0, step=1000.0, key="salaryA")
savings_rate = st.slider("Base savings rate (fraction)", 0.0, 1.0, 0.2, key="saveA")
expenses = st.number_input("Annual expenses (NOK)", 240000.0, step=1000.0, key="expA")
charity = st.number_input("Annual charity donations (deductible)", 0.0, step=1000.0, key="charityA")
ips = st.number_input("Annual IPS contribution (deductible up to cap)", 0.0, step=1000.0, key="ipsA")

# Investments - allow multiple and select account type
st.subheader("Investments (Scenario A)")
n_inv = st.number_input("Number of investments", 1, 5, 2, key="ninvA")
investments = []
for i in range(int(n_inv)):
    with st.expander(f"Investment {i+1}", expanded=(i==0)):
        p = st.number_input(f"Initial principal {i}", value=100000.0, step=1000.0, key=f"invpA_{i}")
        r = st.number_input(f"Expected annual return {i}", value=0.06, step=0.001, key=f"invrA_{i}")
        vol = st.number_input(f"Volatility {i}", value=0.15, step=0.01, key=f"invvolA_{i}")
        acct = st.selectbox(f"Account type {i}", ["brokerage","ASK","IPS"], key=f"invacctA_{i}")
        investments.append(Investment(principal=p, annual_return=r, annual_volatility=vol, account_type=acct))

# Loans
st.subheader("Loans (Scenario A)")
n_loan = st.number_input("Number of loans", 0, 5, 1, key="nloanA")
loans = []
for i in range(int(n_loan)):
    lp = st.number_input(f"Loan principal {i}", 0.0, step=1000.0, key=f"loanpA_{i}")
    lr = st.number_input(f"Loan rate {i}", 0.03, step=0.0001, key=f"loanrA_{i}")
    ly = st.number_input(f"Loan years {i}", 20, step=1, key=f"loanyA_{i}")
    if lp>0:
        loans.append({'principal':lp, 'rate':lr, 'years':int(ly)})

from finance.models import Person, Loan as LoanClass, Investment as InvClass
personA = Person(name=name, salary=salary, savings_rate=min(1.0, savings_rate+extra_savings_pct), expenses=expenses, charity_donation=charity, ips_contribution=ips)
personA.investments = investments
personA.loans = [LoanClass(principal=l['principal'], annual_rate=l['rate'], years=l['years']) for l in loans]

# Scenario B
personB = None
if compare:
    st.header("Scenario B inputs (comparison)")
    nameB = st.text_input("Name B", "Bob", key="nameB")
    salaryB = st.number_input("Gross annual salary B (NOK)", 500000.0, step=1000.0, key="salaryB")
    savings_rateB = st.slider("Savings rate B", 0.0, 1.0, 0.15, key="saveB")
    expensesB = st.number_input("Annual expenses B (NOK)", 200000.0, step=1000.0, key="expB")
    pB = st.number_input("Initial investable assets B", 50000.0, step=1000.0, key="invpB")
    rB = st.number_input("Expected return B", 0.05, step=0.001, key="invrB")
    acctB = st.selectbox("Account type B", ["brokerage","ASK","IPS"], key="acctB")
    invB = InvClass(principal=pB, annual_return=rB, account_type=acctB)
    personB = Person(name=nameB, salary=salaryB, savings_rate=savings_rateB, expenses=expensesB)
    personB.investments = [invB]

sim = Simulation(tax_cfg)
st.header("Simulation results")
col1, col2 = st.columns([2,1])

dfA = sim.project_yearly(personA, years=years, inflation=inflation)
if compare and personB:
    dfB = sim.project_yearly(personB, years=years, inflation=inflation)
else:
    dfB = None

with col1:
    x = dfA['year']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=dfA['total_assets'], name='Total assets', mode='lines'))
    fig.add_trace(go.Scatter(x=x, y=dfA['net_wealth'], name='Net wealth', mode='lines'))
    fig.add_trace(go.Scatter(x=x, y=dfA['real_net_wealth'], name='Real net wealth (inflation adj)', mode='lines', line=dict(dash='dot')))
    if dfB is not None:
        fig.add_trace(go.Scatter(x=x, y=dfB['net_wealth'], name='Scenario B net wealth', mode='lines'))
    fig.update_layout(title="Assets & Net Wealth over time", xaxis_title="Year", yaxis_title="NOK", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=x, y=dfA['assets_brokerage'], name='Brokerage'))
    fig2.add_trace(go.Bar(x=x, y=dfA['assets_ASK'], name='ASK'))
    fig2.add_trace(go.Bar(x=x, y=dfA['assets_IPS'], name='IPS'))
    fig2.update_layout(barmode='stack', title="Assets by account type", xaxis_title="Year", yaxis_title="NOK")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Yearly table (first 10 rows)")
    st.text(sim.format_table(dfA, maxrows=10))
    st.dataframe(dfA.head(20))

    st.subheader("Realize and tax (estimate)")
    realize_ask = st.number_input("Withdraw from ASK (NOK)", 0.0, step=1000.0, key="realask")
    realize_bro = st.number_input("Sell from brokerage (NOK)", 0.0, step=1000.0, key="realbro")
    realize_ips = st.number_input("Withdraw from IPS (taxed as ordinary income) (NOK)", 0.0, step=1000.0, key="realips")
    if st.button("Estimate taxes on realization"):
        res = sim.realize_and_tax(dfA, realize_ask=realize_ask, realize_brokerage=realize_bro, realize_ips_withdraw=realize_ips)
        st.json(res)

    def to_excel_bytes(df_year=None, path='fire_report.xlsx'):
        import pandas as pd, io
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                if df_year is not None:
                    df_year.to_excel(writer, sheet_name='Yearly', index=False)
            return buffer.getvalue()
    excel_bytes = to_excel_bytes(df_year=dfA)
    st.download_button("Download Excel report (Yearly)", data=excel_bytes, file_name="fire_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col2:
    st.subheader("Summary metrics")
    st.metric("Start total assets", f"{dfA['total_assets'].iloc[0]:,.0f}")
    st.metric("Start net wealth", f"{dfA['net_wealth'].iloc[0]:,.0f}")
    st.metric("End net wealth (year {y})".format(y=years), f"{dfA['net_wealth'].iloc[-1]:,.0f}")

st.markdown("---")
st.caption("This advanced prototype models ASK/IPS behavior (simplified), deductions, inflation, and provides tax estimates on realization. Update config_example.yaml to match current tax rules.")
