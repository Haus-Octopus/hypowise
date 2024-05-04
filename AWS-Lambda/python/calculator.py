import json
from datetime import datetime

def calculate_loan_repayment(loan_amount, annual_interest_rate, monthly_payment, start_year, start_month, term_years, annual_repayment):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    current_year, current_month = start_year, start_month
    payments_list = []

    final_year = start_year + term_years
    stop_month = 3  # March

    for _ in range(term_years * 12):
        if current_year == final_year and current_month > stop_month:
            break  # Stop calculations after March in the final year

        adjusted_monthly_payment = monthly_payment
        if current_month == 4 and current_year > start_year:
            adjusted_monthly_payment += annual_repayment  # Add annual repayment in April, except the first year

        interest_paid = loan_amount * monthly_interest_rate
        principal_paid = min(adjusted_monthly_payment - interest_paid, loan_amount)
        loan_amount -= principal_paid

        payments_list.append({
            "year": current_year,
            "month": datetime(current_year, current_month, 1).strftime("%B"),
            "payment": round(adjusted_monthly_payment, 2),
            "interestPaid": round(interest_paid, 2),
            "principalPaid": round(principal_paid, 2),
            "remainingBalance": round(loan_amount, 2)
        })

        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return organize_data_by_year(payments_list)

def organize_data_by_year(payments_list):
    years = {}
    total_interest = 0.0
    total_principal = 0.0
    total_payment = 0.0

    for payment in payments_list:
        year = payment['year']
        if year not in years:
            years[year] = {
                "year": str(year),
                "months": [],
                "totalInterestPaid": 0.0,
                "totalPrincipalRepaid": 0.0,
                "totalPayment": 0.0,
                "remainingBalance": 0.0
            }
        years[year]['months'].append(payment)
        years[year]['totalInterestPaid'] += payment['interestPaid']
        years[year]['totalPrincipalRepaid'] += payment['principalPaid']
        years[year]['totalPayment'] += payment['payment']
        years[year]['remainingBalance'] = payment['remainingBalance']  # Last remaining balance for the year

    final_balance = payments_list[-1]['remainingBalance'] if payments_list else 0

    year_list = sorted(years.values(), key=lambda x: int(x['year']))
    for year in year_list:
        total_interest += year['totalInterestPaid']
        total_principal += year['totalPrincipalRepaid']
        total_payment += year['totalPayment']

    offer_details = {
        "offerId": "1",
        "details": {
            "years": year_list,
            "totalInterestPaid": round(total_interest, 2),
            "totalPrincipalRepaid": round(total_principal, 2),
            "totalPayment": round(total_payment, 2),
            "remainingBalance": round(final_balance, 2)  # The overall final remaining balance
        }
    }

    return offer_details

def lambda_handler(event, context):
    data = json.loads(event.get('body', '{}'))
    loan_amount = data.get('loanAmount')
    annual_interest_rate = data.get('annualInterestRate')
    monthly_payment = data.get('monthlyPayment')
    start_year = data.get('startYear')
    start_month = data.get('startMonth')
    term_years = data.get('term')
    annual_repayment = data.get('annualRepayment', 0)  # Default to 0 if not provided

    response = calculate_loan_repayment(
        loan_amount, annual_interest_rate, monthly_payment,
        start_year, start_month, term_years, annual_repayment
    )

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json",
                     "Access-Control-Allow-Headers": "Content-Type",
                     "Access-Control-Allow-Origin": "*", 
                     "Access-Control-Allow-Methods": ["OPTIONS", "POST"]}
    }
