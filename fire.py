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
            necessities_rate=0.59, wants_rate=0.05, savings_rate=0.36, 
            tax_rate=0.28,
            necessities={'Food': 3E3, 'Other': 4E3},
            housing={'Loan': 1.75E6, 'Years': 20, 'Interest': 0.0539, 'Serial Loan': False, 'Bills': 3.5E3, 'Rent': 9E3, 'Extra contributions': 0},
            student_loan={'Loan': 4.5E5, 'Years': 20, 'Interest': 0.048, 'Serial Loan': False, 'Extra contributions': 0},
            other_debt={'Loan': 7.7E5, 'Years': 16, 'Interest': 0.035, 'Serial Loan': True, 'Extra contributions': 0}
            ):
        self.name = name
        self.year = datetime.date.today().year # The year
        self.age = datetime.date.today().year - birth_year # Calculating the age
        self.gross = gross_income # yearly income before tax
        self.start = saved # how much one already have invested
        self.savings_rate = savings_rate # percentage of how much one wants to save
        self.necessities_rate = necessities_rate # percentage of how much one uses on fixed bills
        self.wants_rate = wants_rate # percentage of how much one uses on wants
        self.tr = tax_rate # percentage of how much one must pay in tax

        self.necessities = necessities
        self.housing = housing
        self.student_loan = student_loan
        self.other_debt = other_debt

        self.netto = gross_income*(1-tax_rate) # yearly income after tax
        self.tax = gross_income*tax_rate # yearly amount which is paid to taxes

        self.mi = self.netto/12 # monthly income after tax 
        self.invest = savings_rate*self.mi # amount to invest each month


    def living_expenses(self):
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
        df_Expected = {} # Approximately following the 50/30/20 budgetting way 
        
        df_Expected['Job Income'] = self.mi
        df_Expected['Rent Income'] = self.housing['Rent']
        df_Expected['Necessities'] = self.mi*self.necessities_rate + self.housing['Rent']
        df_Expected['Wants'] = self.mi*self.wants_rate
        df_Expected['Savings'] = self.mi*self.savings_rate
        df_Expected['Monthly Budget'] = [months[month-1]]
        expected_costs = self.mi*self.necessities_rate + self.mi*self.wants_rate + self.mi*self.savings_rate + self.housing['Rent']
        df_Expected['Expected Living Cost'] = expected_costs
        
        df_Actual['Monthly Expenses'] = [months[month-1]]
        
        house_df = self.calculate_Loan(self.housing['Loan'], self.housing['Years'], self.housing['Interest'], 'Housing', self.housing['Serial Loan'])
        student_debt_df = self.calculate_Loan(self.student_loan['Loan'], self.student_loan['Years'], self.student_loan['Interest'], 'Student Loan', self.student_loan['Serial Loan'])
        other_debt_df = self.calculate_Loan(self.other_debt['Loan'], self.other_debt['Years'], self.other_debt['Interest'], 'Other Debt', self.other_debt['Serial Loan'])
        
        df_Actual['Job Income'] = self.mi
        df_Actual['Rent Income'] = self.housing['Rent']
        df_Actual['Housing'] = house_df['Monthly Payment'].values[0]
        df_Actual['Student Loan'] = student_debt_df['Monthly Payment'].values[0]
        df_Actual['Other Debt'] = other_debt_df['Monthly Payment'].values[0]
        df_Actual['Shared Costs'] = self.housing['Bills']


        df_Actual['Food'] = self.necessities['Food']
        df_Actual['Other'] = self.necessities['Other'] 
        df_Actual['Savings'] = self.invest
        df_Actual['Actual Living Cost'] = df_Actual['Housing'] + df_Actual['Student Loan'] + df_Actual['Other Debt'] + df_Actual['Food'] + df_Actual['Other'] + df_Actual['Shared Costs'] + df_Actual['Savings']   

        df_Expected = pd.DataFrame(df_Expected)
        df_Actual = pd.DataFrame(df_Actual)
        
        df_Actual.set_index('Monthly Expenses', inplace=True)
        df_Expected.set_index('Monthly Budget', inplace=True)


        print(tabulate(df_Expected, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(df_Actual, headers='keys', tablefmt='fancy_grid'))

        print(tabulate(house_df, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(student_debt_df, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(other_debt_df, headers='keys', tablefmt='fancy_grid'))

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter("Personal_Finances.xlsx", engine="xlsxwriter")

        # Position the dataframes in the worksheet.
        df_Expected.to_excel(writer, sheet_name="FIRE")  # Default position, cell A1.
        df_Actual.to_excel(writer, sheet_name="FIRE", startrow=3)
        
        house_df.to_excel(writer, sheet_name="FIRE", startrow=6)
        student_debt_df.to_excel(writer, sheet_name="FIRE", startrow=6, startcol=9)
        other_debt_df.to_excel(writer, sheet_name="FIRE", startrow=6, startcol=18)

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()



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

        
        #print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
        return df


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

        #plt.xticks(range(years[0],years[-1]))
        plt.plot(years, target, '--k')
        plt.legend(['Total', 'Contributed', 'Interest', 'Goal'])
        plt.xlabel("Year")
        plt.ylabel("Money (kr)")
        plt.title("Financial Independence Retire Early")
        plt.savefig('FIRE.png')

    
    def net_Worth(self):
        pass


if __name__ == '__main__':
    life = Persons_Finance()
    life.living_expenses()


    #life.calculate_Loan(Loan=1.75E6, Years=20, interest_rate=0.0539, loan_name='Mortgage', serial_loan=False, extra_contributions=0)
    #life.calculate_Loan(Loan=1.77E6, Years=25, interest_rate=0.0539, loan_name='Mortgage', serial_loan=True, extra_contributions=0)

    #life.calculate_Loan(Loan=4.53E5, Years=20, interest_rate=0.048, loan_name='Student Loan', serial_loan=False, extra_contributions=0)
    #life.calculate_Loan(Loan=7.75E5, Years=16, interest_rate=0.035, loan_name='Neighbourhood Debt', serial_loan=True, extra_contributions=0)

    life.compound_Interest(Interest=0.08, Years=25, Goal=1E7, Invest=0)