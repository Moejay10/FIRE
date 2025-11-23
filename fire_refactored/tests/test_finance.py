import pytest
from finance.loans import annuity_payment
from finance.tax import TaxConfig, TaxEngine

def test_annuity():
    p=120000
    assert annuity_payment(p,0.0,10)==p/(10*12)

def test_tax_engine():
    cfg=TaxConfig()
    te=TaxEngine(cfg)
    assert te.income_tax(500000)>0
