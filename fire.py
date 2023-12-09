#! /usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import datetime 
from tabulate import tabulate
sns.set()

class Persons_Finance:

    def __init__(self, 
            name="Mohamed Ismail", 
            birth_year=1996, 
            gross_income=6E5,
            saved=1E6, 
            savings_rate=0.3, survive_rate=0.2, bills_rate=0.5, 
            tax_rate=0.3):
        self.name = name
        self.year = datetime.date.today().year # The year
        self.age = datetime.date.today().year - birth_year # Calculating the age
        self.gross = gross_income # yearly income before tax
        self.start = saved # how much one already have invested
        self.savings_rate = savings_rate # percentage of how much one wants to save
        self.survive = survive_rate # percentage of how much one wants to use on needs
        self.bills_rate = bills_rate # percentage of how much one uses on fixed bills
        self.ds = 1-(savings_rate+bills_rate) # percentage to use on oneself
        self.tr = tax_rate # percentage of how much one must pay in tax

        self.netto = gross_income*(1-tax_rate) # yearly income after tax
        self.tax = gross_income*tax_rate # yearly amount which is paid to taxes

        self.mi = self.netto/12 # monthly income after tax 
        self.invest = savings_rate*self.mi # amount to invest each month


    def living_expenses(self, income, housing, food, other, savings, debt):
        """Calculates the monthly living expenses which goes to essential needs, 
        such as rent, food, bills and etc.

        Args:
            income (float): The monthly income after tax
            housing (float): The amount payed for rent or mortgage each month 
            food (float): The amount payed for food each month
            other (float): The amount payed for other stuff each month, such as subscription
            savings (float): The amount saved each month
            debt (float): The amount which goes to debt payments each month
        """
        
        dt = datetime.datetime.today()
        month = dt.month

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December']

        df_Actual = {}
        df_Expected = {} # Following the 50/30/20 budgetting way
        df_Expected['Income'] = [self.mi]
        df_Expected['Necessities'] = [self.mi*0.6]
        df_Expected['Wants'] = [self.mi*0.06]
        df_Expected['Savings'] = [self.mi*0.34]
        df_Expected['Monthly Budget'] = [months[month-1]]
        expected_costs = self.mi*0.6 + self.mi*0.1 + self.mi*0.3
        df_Expected['Expected Living Cost'] = [expected_costs]
        
        df_Actual['Monthly Expenses'] = [months[month-1]]
        necessities = housing + food + debt
        df_Actual['Income'] = income
        df_Actual['Necessities'] = [necessities]
        df_Actual['Wants'] = [other]
        df_Actual['Savings'] = [savings]
        df_Actual['Actual Living Cost'] = [necessities + other + savings]

        df_Expected = pd.DataFrame(df_Expected)
        df_Actual = pd.DataFrame(df_Actual)
        
        df_Actual.set_index('Monthly Expenses', inplace=True)
        df_Expected.set_index('Monthly Budget', inplace=True)


        print(tabulate(df_Expected, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(df_Actual, headers='keys', tablefmt='fancy_grid'))


    def serial_loan(self, loan, Years, interest_rate, loan_name, extra_contributions=0):
        """
        Calculates the loan amount for a series loan            

        Args:
            loan (float): The total loan for something 
            Years (float): The total years until the loan is finished payed
            interest_rate (float): Yearly interest
            loan_name (str): The type of loan you have
            extra_contributions (float): The extra payments for the loan
        """            

        Start = loan
        years = np.arange(0, Years)

        F = {}
        F['Age'] = years
        # Calculating the first terms
        F['Deductions'] = [Start/(Years)] * len(years)
        F['Interest'] = [Start*interest_rate]
        F['Term Amount'] = [(Start/(Years)) + Start*interest_rate]
        F['Monthly Payment'] = [(Start/(Years) + Start*interest_rate)/12]

        F['Residual Loan of ' + loan_name] = [Start - (Start/(Years))]

        for y in range(1, len(years)):
            deductions = F['Deductions'][y]
            interest = (F['Residual Loan of ' + loan_name][y-1] * interest_rate)
            F['Interest'].append(interest)
            F['Term Amount'].append(interest + deductions)
            F['Monthly Payment'].append((interest+deductions)/12)
            F['Residual Loan of ' + loan_name].append(F['Residual Loan of ' + loan_name][y-1] - deductions - extra_contributions*12)
        
        return F
    
    def annuity_loan(self, loan, Years, interest_rate, loan_name, extra_contributions=0):
        """
        Calculates the loan amount for a annuity loan            

        Args:
            loan (float): The total loan for something 
            Years (float): The total years until the loan is finished payed
            loan_name (str): The type of loan you have
            interest_rate (float): Yearly interest
            extra_contributions (float): The extra payments for the loan
        """            

        Start = loan
        Terms = Years * 12
        monthly_interest = (1+interest_rate)**(1/12) - 1
        years = np.arange(0, Years)

        F = {}
        F['Age'] = years 
        # Calculating the first terms
        F['Monthly Payment'] = [Start*((monthly_interest)/(1-(1+monthly_interest)**(-Terms)))] * len(years)
        F['Interest'] = [Start*interest_rate]
        F['Term Amount'] = [F['Monthly Payment'][0]*12] * len(years)
        F['Deductions'] = [F['Term Amount'][0] - F['Interest'][0]]
        F['Residual Loan of ' + loan_name] = [Start - F['Deductions'][0]]

        for y in range(1, len(years)):
            F['Interest'].append(F['Residual Loan of ' + loan_name][y-1]*interest_rate)
            F['Deductions'].append(F['Term Amount'][y] - F['Interest'][y])
            F['Residual Loan of ' + loan_name].append(F['Residual Loan of ' + loan_name][y-1] - F['Deductions'][y])
        
        return F
    


    def calculate_Loan(self, Loan, Years, interest_rate, loan_name, serial_loan=False, extra_contributions=0):
        """
        Calculates the mortgage and does estimations on it

        Args:
            house_loan (float): The total loan for the house 
            Years (float): The total years until the loan is finished payed
            interest_rate (float): Yearly interest
            loan_name (str): The type of loan you have
            loan_type (str): The type of loan you are getting, either a serial or annuity loan
            extra_contributions (float): The extra payments for the loan
        """

        if serial_loan:
            F = self.serial_loan(Loan, Years, interest_rate, loan_name, extra_contributions)
        else:
            F = self.annuity_loan(Loan, Years, interest_rate, loan_name, extra_contributions)
        
        years = np.arange(0, Years)
        ages = years + self.age
        years += self.year 
        F['Age'] = ages
        F['Year'] = years
        df = pd.DataFrame(F)
        df.set_index('Year', inplace=True)
        df = df[['Age', 'Monthly Payment', 'Deductions', 'Interest', 'Term Amount', 'Residual Loan of ' + loan_name]]
        df.rename(columns = {'Deductions': 'Yearly Deductions', 'Interest': 'Yearly Interest', 'Term Amount': 'Yearly Term'}, inplace=True)
        df.loc['Total']= df.sum() #add total row
        #set last value in team column to be blank
        df.loc[df.index[-1], 'Age',] = None
        df.loc[df.index[-1], 'Monthly Payment',] = None
        df.loc[df.index[-1], 'Residual Loan of ' + loan_name,] = None

        print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
        


    def compound_Interest(self, Interest, Years, Goal, Invest=0):
        """Calculates the compound interest

        Args:
            Interest (float): Yearly interest 
            Years (float): Number of years 
            Goal (float): The amount to become financial independence
        """
        Start = self.start
        if Invest == 0:
            Contributions = self.invest # amount to invest each month
        else:
            Contributions = Invest # amount to invest each month

        years = np.arange(0, Years)
       
        r = Interest
        F = {}
        # Calculating the start
        F['Total'] = [Start]
        F['Contributed'] = [Start]
        F['Interest'] = [0]
    
        for y in range(1, len(years)):
            cont = Contributions*12
            gain = F['Total'][y-1]*(1+r) - F['Contributed'][y-1]  
            total = F['Total'][y-1]*(1+r) + cont
            
            F['Contributed'].append(F['Contributed'][y-1] + cont)
            F['Interest'].append(gain)
            F['Total'].append(total)
    
        ages = years + self.age
        years += self.year
        F['Age'] = ages
        F['Year'] = years
        df = pd.DataFrame(F)
        target = np.ones(len(years))*Goal
        df.plot(x='Year', y=['Total', 'Contributed', 'Interest'] , style='.-')
        df.set_index('Year', inplace=True)

        plt.xticks(range(years[0],years[-1]))
        plt.plot(years, target, '--k')
        plt.legend(['Total', 'Contributed', 'Interest', 'Goal'])
        plt.xlabel("Year")
        plt.ylabel("Money (kr)")
        plt.title("Financial Independence Retire Early")
        plt.show()

    
    def net_Worth(self):
        pass


if __name__ == '__main__':
    life = Persons_Finance()
    life.living_expenses(income=3.5E4, housing=1.4E4, food=3E3, other=2E3, savings=1.3E4, debt=3E3)


    life.calculate_Loan(Loan=1.75E6, Years=20, interest_rate=0.0539, loan_name='Mortgage', serial_loan=False, extra_contributions=0)
    #life.calculate_Loan(Loan=1.77E6, Years=25, interest_rate=0.0539, loan_name='Mortgage', serial_loan=True, extra_contributions=0)

    life.calculate_Loan(Loan=4.53E5, Years=20, interest_rate=0.048, loan_name='Student Loan', serial_loan=False, extra_contributions=0)
    life.calculate_Loan(Loan=7.75E5, Years=16, interest_rate=0.035, loan_name='Neighbourhood Debt', serial_loan=True, extra_contributions=0)

    life.compound_Interest(Interest=0.08, Years=20, Goal=1E7, Invest=1.3E4)