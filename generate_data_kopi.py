import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# Constants
BRANCHES = ['BR001', 'BR002', 'BR003', 'BR004', 'BR005', 'BR006', 'BR007', 'BR008']
ITEMS = {
    'Americano': 30_000,
    'Latte': 38_000,
    'Cappuccino': 38_000,
    'Es Kopi Susu': 25_000,
    'Matcha Latte': 42_000,
    'Croissant': 35_000,
    'Sandwich': 65_000
}
PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'Cash']
PLATFORM_NAMES = ['Midtrans', 'ShopeePay', 'DANA']
SUPPLIERS = ['Supplier A', 'Supplier B']

# Generate sales transactions data
num_transactions = 100_000
sales_pos_data = []
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)

for _ in range(num_transactions):
    branch_id = random.choice(BRANCHES)
    timestamp = start_date + (end_date - start_date) * np.random.rand()
    item_name = random.choices(list(ITEMS.keys()), weights=list(ITEMS.values()))[0]
    qty = np.random.randint(1, 4)
    price = ITEMS[item_name] * qty
    payment_method = random.choice(PAYMENT_METHODS)
    gross_sales = price
    pb1_tax = gross_sales * 0.1
    sales_pos_data.append([f'TR{_+1:06d}', branch_id, timestamp, item_name, qty, price, payment_method, gross_sales, pb1_tax])

sales_pos_df = pd.DataFrame(sales_pos_data, columns=['Transaction_ID', 'Branch_ID', 'Timestamp', 'Item_Name', 'Qty', 'Price', 'Payment_Method', 'Gross_Sales', 'PB1_Tax'])

# Generate settlement report data
settlement_report_data = []
for index, row in sales_pos_df.iterrows():
    transaction_id = row['Transaction_ID']
    if np.random.rand() < 0.95:  # 5% of transactions will not have a matching row in settlement_report (leakage)
        net_amount = row['Gross_Sales'] * (1 - 0.002) if index % 200 == 0 else row['Gross_Sales']
        settlement_date = row['Timestamp'] + timedelta(days=np.random.randint(1, 3))
        reconciliation_status = 'Reconciled' if np.random.rand() < 0.98 else 'Pending'
        settlement_report_data.append([f'SET{_+1:06d}', transaction_id, random.choice(PLATFORM_NAMES), net_amount, settlement_date, reconciliation_status])

settlement_report_df = pd.DataFrame(settlement_report_data, columns=['Settlement_ID', 'Transaction_ID', 'Platform_Name', 'Net_Amount', 'Settlement_Date', 'Reconciliation_Status'])

# Generate bank mutation data
bank_mutation_data = []
start_bal = 1_000_000
for index, row in sales_pos_df.iterrows():
    if np.random.rand() < 0.9:  # Simulating only a portion of transactions affecting the bank balance due to PB1 tax
        date = row['Timestamp']
        description = f'Sales {row["Transaction_ID"]}'
        debit = row['Price'] * (1 - 0.002) if index % 200 == 0 else row['Price']
        credit = 0
        start_bal += debit
        bank_mutation_data.append([date, description, debit, credit, start_bal])

bank_mutation_df = pd.DataFrame(bank_mutation_data, columns=['Date', 'Description', 'Debit', 'Credit', 'Balance'])

# Generate inventory AP data
inventory_ap_data = []
for branch_id in BRANCHES:
    for item_name, price in ITEMS.items():
        date = start_date + (end_date - start_date) * np.random.rand()
        qty_purchased = np.random.randint(10, 50)
        unit_price = price
        total_cost = qty_purchased * unit_price
        supplier = random.choice(SUPPLIERS)
        inventory_ap_data.append([branch_id, date, item_name, qty_purchased, unit_price, total_cost, supplier])
    # Simulate shrinkage for BR002 and BR005
    if branch_id in ['BR002', 'BR005']:
        shortage = int(qty_purchased * 0.04)
        inventory_ap_data.append([branch_id, date, random.choice(list(ITEMS.keys())), -shortage, unit_price, total_cost, supplier])

inventory_ap_df = pd.DataFrame(inventory_ap_data, columns=['Branch_ID', 'Date', 'Item', 'Qty_Purchased', 'Unit_Price', 'Total_Cost', 'Supplier'])

# Export data to Excel
with pd.ExcelWriter('Kopi_Senja_Audit_Raw.xlsx', engine='xlsxwriter') as writer:
    sales_pos_df.to_excel(writer, sheet_name='sales_pos', index=False)
    settlement_report_df.to_excel(writer, sheet_name='settlement_report', index=False)
    bank_mutation_df.to_excel(writer, sheet_name='bank_mutation', index=False)
    inventory_ap_df.to_excel(writer, sheet_name='inventory_ap', index=False)

print("Synthetic dataset generated successfully.")