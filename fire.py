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
            salary_income=6.5E5,
            bonus_income=4.0E4,
            saved=1.7E6, 
            necessities_rate=0.50, wants_rate=0.10, savings_rate=0.40, 
            invest_info={'Interest': 0.08, 'Years': 20, 'Goal': 1.5E7, 'Invest': 0},
            tax_info={'min_deduction': 104450, 'personal_deduction': 88250, 'social_security_tax': 0.082, 'state_tax': 0.23, 'stage_tax': [0.017, 0.04, 0.136]},
            necessities={'Food': 4E3, 'Other': 5.0E3},
            housing={'Loan': 1.7E6, 'Start Time': datetime.datetime.strptime('15/09/2023', '%d/%m/%Y').date(), 'Years': 19, 'Interest': 0.056, 'Serial Loan': False, 'Shared Costs': 4E3, 'Rent': 9.5E3, 'Extra contributions': 0},
            student_loan={'Loan': 4.49E5, 'Start Time': datetime.datetime.strptime('15/06/2024', '%d/%m/%Y').date(), 'Years': 12, 'Interest': 0.0543, 'Serial Loan': False, 'Extra contributions': 0},
            other_debt={'Loan': 7.7E5, 'Start Time': datetime.datetime.strptime('15/09/2023', '%d/%m/%Y').date(), 'Years': 12, 'Interest': 0.031, 'Serial Loan': False, 'Extra contributions': 0}
            ):
        self.name = name
        self.year = datetime.date.today().year # The year 
        self.birth_year = birth_year
        self.age = datetime.date.today().year - birth_year # Calculating the age
        self.salary = salary_income # Salary Income
        self.bonus = bonus_income # Bonuses earned
        self.gross = salary_income + bonus_income # yearly income before tax
        self.start = saved # how much one already have invested
        self.savings_rate = savings_rate # percentage of how much one wants to save
        self.necessities_rate = necessities_rate # percentage of how much one uses on fixed bills
        self.wants_rate = wants_rate # percentage of how much one uses on wants

        # Dictionaries with information
        self.necessities = necessities
        self.housing = housing
        self.student_loan = student_loan
        self.other_debt = other_debt
        self.tax_info = tax_info
        self.invest_info = invest_info


    def add_columns(self, df_list, column_names):
        a = list(df_list[0][column_names[0]])[:-1]
        b = list(df_list[1][column_names[1]])[:-1]
        c = list(df_list[2][column_names[2]])[:-1]
        
        l1, l2, l3 = len(a), len(b), len(c)
        # now find the max
        max_len = max(l1, l2, l3)

        # Resize all according to the determined max length
        if not max_len == l1:
            a.extend([0]*(max_len - l1))
        if not max_len == l2:
            b.extend([0]*(max_len - l2))
        if not max_len == l3:
            c.extend([0]*(max_len - l3))
        
        total_df = pd.DataFrame(
            {
            'Total Debt': np.array(a) + np.array(b) + np.array(c)
            }
        )

        return total_df

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

        n_months = {'1': 12, '2': 11, '3': 10, '4': 9, '5': 8, '6': 7, '7': 6, '8': 5,
        '9': 4, '10': 3, '11': 2, '12': 1}

        time_factor = (n_months[str(month)]/12)

        df_Actual = {}
        df_Expected = {} # Approximately following the 50/30/20 budgetting way 


        house_df = self.calculate_Loan(self.housing['Loan'], self.housing['Start Time'], self.housing['Years'], self.housing['Interest'], 'Housing', self.housing['Serial Loan'], self.housing['Extra contributions'])
        student_debt_df = self.calculate_Loan(self.student_loan['Loan'], self.student_loan['Start Time'], self.student_loan['Years'], self.student_loan['Interest'], 'Student Loan', self.student_loan['Serial Loan'], self.student_loan['Extra contributions'])
        other_debt_df = self.calculate_Loan(self.other_debt['Loan'], self.other_debt['Start Time'], self.other_debt['Years'], self.other_debt['Interest'], 'Shared Loan', self.other_debt['Serial Loan'], self.other_debt['Extra contributions'])
        
        tax_df = self.tax_calculator(house_df, student_debt_df, other_debt_df)

        tax_df['Tax %'] = [self.tr]*len(tax_df)

        summary_dict = {
            'Month': [months[month-1]],
            'Year': [tax_df['Year'][0]],
            'Gross Salary': [self.salary],
            'Bonus': [self.bonus],
            'Total Tax': [tax_df['Total Tax'][1]],
            'Tax %': [round(tax_df['Tax %'][0]*100)],
            'Netto Salary': [self.salary* (1-self.tr)],
            'Taxes Already Payed': [tax_df['Total Tax'][1]*(month/12)],
            'Vacation Money': [self.salary*0.12],
            'Total Debt': list(house_df['Residual Loan of Housing'])[0] + list(student_debt_df['Residual Loan of Student Loan'])[0] + list(other_debt_df['Residual Loan of Shared Loan'])[0]
        }

        summary_df = pd.DataFrame(summary_dict)
        # Set the 'Name' column as the index
        summary_df = summary_df.set_index('Month')

        self.netto = self.salary*(1-self.tr) # yearly income after tax
        self.tax = self.salary*self.tr # yearly amount which is paid to taxes
        self.mi = (self.netto/12) # monthly income after tax 
        self.invest = self.savings_rate*self.mi # amount to invest each month
        
        df_Expected['Job Income'] = self.mi
        df_Expected['Rent Income'] = self.housing['Rent']
        df_Expected['Necessities'] = self.mi*self.necessities_rate + self.housing['Rent']
        df_Expected['Wants'] = self.mi*self.wants_rate
        df_Expected['Savings'] = self.mi*self.savings_rate
        df_Expected['Monthly Budget'] = [months[month-1]]
        expected_costs = self.mi*self.necessities_rate + self.mi*self.wants_rate + self.mi*self.savings_rate + self.housing['Rent']
        df_Expected['Expected Living Cost'] = expected_costs
        
        df_Actual['Monthly Expenses'] = [months[month-1]]
        
        df_Actual['Job Income'] = self.mi
        df_Actual['Rent Income'] = self.housing['Rent']
        df_Actual['Housing'] = house_df['Monthly Payment'].values[0]
        df_Actual['Student Loan'] = student_debt_df['Monthly Payment'].values[0]
        df_Actual['Shared Loan'] = other_debt_df['Monthly Payment'].values[0]
        df_Actual['Shared Costs'] = self.housing['Shared Costs']


        df_Actual['Food'] = self.necessities['Food']
        df_Actual['Other'] = self.necessities['Other'] 
        df_Actual['Savings'] = self.invest
        df_Actual['Actual Living Cost'] = df_Actual['Housing'] + df_Actual['Student Loan'] + df_Actual['Shared Loan'] + df_Actual['Food'] + df_Actual['Other'] + df_Actual['Shared Costs'] + df_Actual['Savings']   

        diff = df_Expected['Expected Living Cost'] - df_Actual['Actual Living Cost'] # Calculating the difference in budgeted and actual costs
        if diff > 0:
            df_Actual['Savings'] = df_Actual['Savings'] + diff
            self.invest += diff 
            df_Actual['Actual Living Cost'] = df_Actual['Actual Living Cost'] + diff
        else:
            df_Actual['Savings'] = df_Actual['Savings'] - abs(diff)
            self.invest -= abs(diff)
            df_Actual['Actual Living Cost'] = df_Actual['Actual Living Cost'] - abs(diff)

        df_Expected = pd.DataFrame(df_Expected)
        df_Actual = pd.DataFrame(df_Actual)
        
        invest_df = self.compound_Interest(self.invest_info['Interest'], self.invest_info['Years'], self.invest_info['Goal'], self.invest_info['Invest'])
        invest_df.rename(columns = {'Total':'Total Invested'}, inplace = True)
        total_debt = self.add_columns([house_df, student_debt_df, other_debt_df], ['Residual Loan of Housing', 'Residual Loan of Student Loan', 'Residual Loan of Shared Loan'])

        assets_df = self.net_Worth(total_debt, invest_df)

        tax_df['Asset Tax'] = assets_df['Asset Tax']

        summary_df['Total Assets'] = assets_df['Total Assets'][0]
        summary_df['Total Tax'] += assets_df['Asset Tax'][0]


        df_Actual.set_index('Monthly Expenses', inplace=True)
        df_Expected.set_index('Monthly Budget', inplace=True)


        print(tabulate(summary_df, headers='keys', tablefmt='fancy_grid'))

        print(tabulate(df_Expected, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(df_Actual, headers='keys', tablefmt='fancy_grid'))

        print(tabulate(house_df, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(student_debt_df, headers='keys', tablefmt='fancy_grid'))
        print(tabulate(other_debt_df, headers='keys', tablefmt='fancy_grid'))
        
        print(tabulate(invest_df, headers='keys', tablefmt='fancy_grid'))

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



    def serial_loan(self, loan, start_time, Years, interest_rate, loan_name, extra_contributions=0):
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
        dt = start_time #datetime.datetime.today()
        month = dt.month
        months = {'1': 12, '2': 11, '3': 10, '4': 9, '5': 8, '6': 7, '7': 6, '8': 5,
        '9': 4, '10': 3, '11': 2, '12': 1}
        time_factor = (months[str(month)]/12)

        F = {}
        F['Age'] = years
        # Calculating the first terms
        F['Deductions'] = [Start/(Years)] * len(years)
        F['Deductions'][0] = F['Deductions'][0]*time_factor
        F['Interest'] = [Start*interest_rate*time_factor]
        F['Term Amount'] = [(Start/(Years)) + Start*interest_rate*time_factor]
        F['Monthly Payment'] = [(Start/(Years) + Start*interest_rate)/12]
        F['Extra Contributions'] = [extra_contributions]*len(years)

        F['Residual Loan of ' + loan_name] = [Start - F['Deductions'][0] - extra_contributions*12*time_factor]

        for y in range(1, len(years)):
            deductions = F['Deductions'][y]
            interest = (F['Residual Loan of ' + loan_name][y-1] * interest_rate)
            F['Interest'].append(interest)
            F['Term Amount'].append(interest + deductions)
            F['Monthly Payment'].append((interest+deductions)/12)
            F['Residual Loan of ' + loan_name].append(F['Residual Loan of ' + loan_name][y-1] - deductions - extra_contributions*12)
        
        return F
    
    def annuity_loan(self, loan, start_time, Years, interest_rate, loan_name, extra_contributions=0):
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
        dt = start_time #datetime.datetime.today()
        month = dt.month
        months = {'1': 12, '2': 11, '3': 10, '4': 9, '5': 8, '6': 7, '7': 6, '8': 5,
        '9': 4, '10': 3, '11': 2, '12': 1}
        time_factor = (months[str(month)]/12)
        

        F = {}
        F['Age'] = years 
        # Calculating the first terms
        F['Monthly Payment'] = [Start*((monthly_interest)/(1-(1+monthly_interest)**(-Terms)))] * len(years)
        F['Extra Contributions'] = [extra_contributions]*len(years)
        F['Interest'] = [Start*interest_rate*time_factor]
        F['Term Amount'] = [F['Monthly Payment'][0]*12] * len(years)
        F['Term Amount'][0] = F['Term Amount'][0]*time_factor
        F['Deductions'] = [F['Term Amount'][0] - F['Interest'][0]]
        F['Residual Loan of ' + loan_name] = [Start - F['Deductions'][0] - extra_contributions*12*time_factor]

        for y in range(1, len(years)):
            F['Interest'].append(F['Residual Loan of ' + loan_name][y-1]*interest_rate)
            F['Deductions'].append(F['Term Amount'][y] - F['Interest'][y])
            F['Residual Loan of ' + loan_name].append(F['Residual Loan of ' + loan_name][y-1] - F['Deductions'][y] - extra_contributions*12)

        
        return F
    


    def calculate_Loan(self, Loan, start_time, Years, interest_rate, loan_name, serial_loan=False, extra_contributions=0):
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
            F = self.serial_loan(Loan, start_time, Years, interest_rate, loan_name, extra_contributions)
        else:
            F = self.annuity_loan(Loan, start_time, Years, interest_rate, loan_name, extra_contributions)
        
        years = np.arange(0, Years)
        ages = years + (start_time.year - self.birth_year)
        years += start_time.year 
        F['Age'] = ages
        F['Year'] = years
        df = pd.DataFrame(F)

        df.set_index('Year', inplace=True)
        df = df[['Age', 'Monthly Payment', 'Extra Contributions', 'Deductions', 'Interest', 'Term Amount', 'Residual Loan of ' + loan_name]]
        df.rename(columns = {'Extra Contributions': 'Extra Monthly Contributions', 'Deductions': 'Yearly Deductions', 'Interest': 'Yearly Interest', 'Term Amount': 'Yearly Term'}, inplace=True)

        # checking the element is < 0 
        df[df < 0] = 0
        df.loc[(df['Residual Loan of ' + loan_name] == 0), ['Monthly Payment', 'Extra Monthly Contributions', 'Yearly Deductions', 'Yearly Interest', 'Yearly Term']] = 0

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
            cont = Contributions*12 # Contributions for the year multiplied with a 5% increase every year
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
        #plt.show()
        plt.savefig('FIRE.png')

        return df

    
    def tax_calculator(self, df1, df2, df3):

        # Finding the time now, so the calculation can be adjusted to suit the time
        dt = datetime.datetime.today()
        month = dt.month
        months = {'1': 12, '2': 11, '3': 10, '4': 9, '5': 8, '6': 7, '7': 6, '8': 5,
        '9': 4, '10': 3, '11': 2, '12': 1}
        time_factor = (months[str(month)]/12)

        a = list(df1['Yearly Interest'])[:-1]
        b = list(df2['Yearly Interest'])[:-1]
        c = list(df3['Yearly Interest'])[:-1]
        
        l_df1, l_df2, l_df3 = len(df1), len(df2), len(df3)
        # now find the max
        max_len = max(l_df1, l_df2, l_df3)

        # Resize all according to the determined max length
        if not max_len == l_df1:
            a.extend([0]*(max_len - l_df1))
        if not max_len == l_df2:
            b.extend([0]*(max_len - l_df2))
        if not max_len == l_df3:
            c.extend([0]*(max_len - l_df3))
    

        max_len -= 1 # To make sure the length of arrays stay same length

        # Deductions
        minimun_deduction = [self.tax_info['min_deduction']]*max_len
        person_deduction = [self.tax_info['personal_deduction']]*max_len

        # Taxes in percentage
        social_security_tax = self.tax_info['social_security_tax'] # Off the gross inncome
        state_tax = self.tax_info['state_tax'] # On the income after all deductions have been deducted
        stage1_tax = self.tax_info['stage_tax'][0] # For income between 200k - 300k
        stage2_tax = self.tax_info['stage_tax'][1] # For income between 300k - 670k
        stage3_tax = self.tax_info['stage_tax'][2] # For income between 670k - 940k
        
        # Make the column names
        years = self.year + np.arange(0, max_len)
        ages = self.age + np.arange(0, max_len)
        col1 = df1.columns.tolist()[-1].split()[-1]
        col2 = df2.columns.tolist()[-1].split()[-2]
        col3 = df3.columns.tolist()[-1].split()[-2]

        # Now the all list is same length and create dataframe
        interest_df = pd.DataFrame({'Year': years, 'Age': ages, col1 + ' Interest': a, col2 + ' Interest': b, col3 + ' Interest': c}) 
        tax_df = pd.DataFrame()
        tax_df['Year'] = interest_df['Year']
        tax_df['Age'] = interest_df['Age']
        tax_df['Gross Salary'] = [self.gross]*max_len

        interest_df['Total Debt Interest'] = interest_df[col1 + ' Interest'] + interest_df[col2 + ' Interest'] + interest_df[col3 + ' Interest']
        tax_df['Debt Deduction'] = interest_df['Total Debt Interest']
        tax_df['Minimum Deduction'] = minimun_deduction
        tax_df['Personal Deduction'] = person_deduction
        tax_df['Social Security Tax'] = tax_df['Gross Salary']*social_security_tax
        tax_df['State Tax'] = (tax_df['Gross Salary'] - tax_df['Debt Deduction'] - tax_df['Minimum Deduction'] - tax_df['Personal Deduction'])*state_tax
        
        if self.gross <= 2.93E5:
            tax_df['Stage Tax'] = np.array([(8.54E5-self.gross)*stage1_tax]*max_len)
        elif self.gross <= 6.7E5:
            tax_df['Stage Tax'] = np.array([8.5E4*stage1_tax]*max_len) + np.array([(6.7E5-self.gross)*stage2_tax]*max_len)
        elif self.gross <= 9.38E5:
            tax_df['Stage Tax'] = np.array([8.5E4*stage1_tax]*max_len) + np.array([3.77E5*stage2_tax]*max_len) + np.array([(self.gross-6.7E5)*stage3_tax]*max_len)

        tax_df['Total Tax'] = tax_df['Social Security Tax'] + tax_df['State Tax'] + tax_df['Stage Tax']

        tax_df['Netto Salary'] = tax_df['Gross Salary'] - tax_df['Total Tax']

        self.tr = tax_df['Total Tax'].values[1]/self.gross

        return tax_df

    
    
    def net_Worth(self, total_debt, investment):
        time_frame = len(total_debt)
        house_asset = self.primary_residence(time_frame)
        total_assets = pd.DataFrame()
        
        min_time = 0
        if len(investment['Total Invested']) <= time_frame:
            min_time = len(investment['Total Invested'])
        else:
            min_time = time_frame

        total_assets['Total Assets'] = np.array(list(investment['Total Invested'])[0:min_time]) + np.array(list(house_asset['Primary Residence Asset'])[0:min_time]) - np.array(list(total_debt['Total Debt'])[0:min_time])
        assets_tax = []
        asset_tax_limit = 1.7E6
        for asset in total_assets['Total Assets']:
            if asset > 0 and asset > asset_tax_limit:
                assets_tax.append(asset*0.01)
            else:
                assets_tax.append(0)
        
        total_assets['Asset Tax'] = assets_tax

        return total_assets

    
    def primary_residence(self, time_frame):
        house_asset = [0] * time_frame
        house_asset[0] = (self.housing['Loan'] + self.other_debt['Loan']) * 0.25 # Primary residence is only 25% asset of the total value
        house_prices_increase = 0.01 # An educated guess
        for i in range(1, time_frame):
            house_asset[i] = house_asset[i-1] * (1 + house_prices_increase)
        
        house_asset_df = pd.DataFrame(
            {
                'Primary Residence Asset': house_asset
            }
        )
        return house_asset_df


        


if __name__ == '__main__':
    
    ch = 0
    while (ch != 3):
        print("--[ FIRE ]--")
        print("Vennligst velg et alternativ:\n 1. Skriv ut forhånds inputted økonomi detaljer\n 2. Legg inn nye økonomi detaljer\n 3. Avslutt")
        ch = int(input("Valg: "))

        if (ch == 1):
            life = Persons_Finance()
            life.living_expenses()
    
        elif (ch == 2):
            print("\n--[LEGG INN NY DATA]--")
            salary_income = float(input("Lønn: "))
            bonus_income = float(input("Bonus: "))
            saved = float(input("Spart: "))
            
            # Boliglån
            have_housing_loan = str(input("\nHar du boliglån (Ja/Nei): "))
            if have_housing_loan == "Ja":
                housing_loan = float(input("Boliglån: "))
                housing_interest = float(input("Boliglånsrente i %: "))/100
                housing_years = int(input("Boliglån Lengde i år: "))
                housing_shared_costs = float(input("Felleskostnader: "))
                housing_rent = float(input("Leieinntekter: "))
                housing_extra_contributions = int(input("Ekstra månedlige betalinger: "))
            else:
                housing_loan = 0
                housing_years = 2
                housing_interest = 0.056
                housing_shared_costs = 0
                housing_rent = 0
                housing_extra_contributions = 0
            
            housing={'Loan': housing_loan, 'Start Time': datetime.date.today(), 'Years': housing_years, 'Interest': housing_interest, 'Serial Loan': False, 'Shared Costs': housing_shared_costs, 'Rent': housing_rent, 'Extra contributions': housing_extra_contributions}
 
            # Student lån
            have_student_loan = str(input("\nHar du student lån (Ja/Nei): "))
            if have_student_loan == "Ja":
                student_loan = float(input("Studentlån: "))
                student_interest = float(input("Lånets rente i %: "))/100
                student_years = int(input("Lånets Lengde i år: "))
                student_extra_contributions = int(input("Ekstra månedlige betalinger: "))
            else:
                student_loan = 0
                student_years = 2
                student_interest = 0.0543
                student_extra_contributions = 0
            
            student={'Loan': student_loan, 'Start Time': datetime.date.today(), 'Years': student_years, 'Interest': student_interest, 'Serial Loan': False, 'Extra contributions': student_extra_contributions}
            
            # Annet lån
            have_other_loan = str(input("\nHar du annet lån (Ja/Nei): "))
            if have_other_loan == "Ja":
                other_loan = float(input("Annet Lån: "))
                other_interest = float(input("Lånets rente i %: "))/100
                other_years = int(input("Lånets Lengde i år: "))
                other_extra_contributions = int(input("Ekstra månedlige betalinger: "))
            else:
                other_loan = 0
                other_years = 2
                other_interest = 0.031
                other_extra_contributions = 0

        
            other={'Loan': other_loan, 'Start Time': datetime.date.today(), 'Years': other_years, 'Interest': other_interest, 'Serial Loan': False, 'Extra contributions': other_extra_contributions}
            
            
            life = Persons_Finance(salary_income=salary_income, bonus_income=bonus_income, saved=saved, housing=housing, student_loan=student, other_debt=other)
            life.living_expenses()

