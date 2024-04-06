import streamlit as st
from datetime import date
import pandas as pd

def calculate_loan_repayment(loan_amount, annual_interest_rate, monthly_payment, start_year, start_month, term_years=None, annual_repayment=None):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    current_year, current_month = start_year, start_month
    total_interest_paid = 0
    payments_list = []

    if term_years:
        end_year = start_year + term_years 
        total_months = (end_year - start_year) * 12 + (4 - start_month)
    else:
        total_months = float('inf')

    month_count = 0
    while loan_amount > 0 and month_count < total_months:
        month_count += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

        is_april = current_month == 4 and current_year > start_year
        monthly_repayment = monthly_payment + (annual_repayment if is_april and annual_repayment else 0)
        interest_paid = loan_amount * monthly_interest_rate
        principal_paid = min(monthly_repayment - interest_paid, loan_amount)
        loan_amount -= principal_paid
        total_interest_paid += interest_paid
        payments_list.append([current_year, current_month, round(monthly_repayment, 2), round(interest_paid, 2), round(principal_paid, 2), round(loan_amount, 2)])

        current_month += 1

    return payments_list, total_interest_paid

# Streamlit app interface
st.title('Loan Repayment Calculator')

# Display instructions
st.write("Enter the loan details to calculate the repayment schedule and total interest paid.")

# User inputs
loan_amount = st.number_input('Loan Amount', min_value=0.01, value=10000.0)
annual_interest_rate = st.number_input('Annual Interest Rate (%)', min_value=0.01, value=5.0)
monthly_payment = st.number_input('Monthly Payment', min_value=0.01, value=200.0)
start_year = st.number_input('Start Year', min_value=date.today().year, value=date.today().year)
start_month = st.selectbox('Start Month', range(1, 13), index=date.today().month - 1)
term_years = st.number_input('Term in Years (optional)', min_value=0, value=0, format='%d')
annual_repayment = st.number_input('Annual Repayment Starting the Second April (optional)', min_value=0.0, value=0.0)

# Adjusting input to function requirements
term_years = None if term_years == 0 else term_years
annual_repayment = None if annual_repayment == 0.0 else annual_repayment

# Trigger calculations
if st.button('Calculate Repayments'):
    payments, total_interest = calculate_loan_repayment(loan_amount, annual_interest_rate, monthly_payment, start_year, start_month, term_years, annual_repayment)
    
    # Convert payments list to DataFrame
    payments_df = pd.DataFrame(payments, columns=["Year", "Month", "Payment", "Interest Paid", "Principal Paid", "Remaining Balance"])
    
    # Calculate annual summaries
    annual_summaries = payments_df.groupby('Year').agg({'Payment': 'sum', 'Interest Paid': 'sum', 'Principal Paid': 'sum'}).reset_index()
    annual_summaries['Remaining Balance'] = payments_df.groupby('Year')['Remaining Balance'].last().reset_index(drop=True)
    
    # Display yearly data and summaries
    for year in payments_df['Year'].unique():
        with st.expander(f"Year {year}", expanded=(year == start_year)):
            year_data = payments_df[payments_df['Year'] == year]
            st.dataframe(year_data.style.format("{:.2f}"))
            
            # Display annual summary for the year
            summary = annual_summaries[annual_summaries['Year'] == year].iloc[0]
            st.markdown(f"**Year {year} Summary:**")
            st.markdown(f"- Total Payments: ${summary['Payment']:.2f}")
            st.markdown(f"- Total Interest Paid: ${summary['Interest Paid']:.2f}")
            st.markdown(f"- Principal Repaid: ${summary['Principal Paid']:.2f}")
            st.markdown(f"- Remaining Loan Balance: ${summary['Remaining Balance']:.2f}")

    # Final summary
    st.write(f"### Total Loan Summary:")
    st.write(f"- Total Interest Paid: ${total_interest:.2f}")
    st.write(f"- Total Loan Paid: ${payments_df['Principal Paid'].sum():.2f}")
    st.write(f"- Final Remaining Balance: ${payments_df['Remaining Balance'].iloc[-1]:.2f}")