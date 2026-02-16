import pandas as pd
import random
from datetime import datetime, timedelta
import faker

# Initialize Faker
fake = faker.Faker()

# Constants
NUM_TRANSACTIONS = 500
START_DATE = datetime(2025, 1, 1)

# Normal Transaction Types
TYPES = [
    "POS Purchase", 
    "Direct Debit", 
    "Salary Credit", 
    "ATM Withdrawal", 
    "Online Transfer", 
    "Bill Payment", 
    "Dividend Credit"
]

# Descriptions for normal activity
DESCRIPTIONS = {
    "POS Purchase": ["Grocery store purchase", "Department store", "Restaurant payment", "Gas station", "Online subscription"],
    "Direct Debit": ["Utility bill payment", "Mortgage payment", "Insurance premium", "Gym membership"],
    "Salary Credit": ["Monthly salary credit", "Bonus payment", "Reimbursement"],
    "ATM Withdrawal": ["Cash withdrawal", "Petty cash withdrawal"],
    "Online Transfer": ["Transfer to savings", "Gift to family", "Payment to friend"],
    "Bill Payment": ["Credit card bill", "Internet bill"],
    "Dividend Credit": ["Quarterly dividend payment"]
}

data = []

for _ in range(NUM_TRANSACTIONS):
    # Random Date
    days_offset = random.randint(0, 365)
    date = (START_DATE + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    
    # Customer
    customer = fake.name()
    
    # Type
    t_type = random.choice(TYPES)
    
    # Amount (Normal ranges)
    if t_type == "Salary Credit":
        amount = round(random.uniform(3000, 8000), 2)
    elif t_type in ["Direct Debit", "Bill Payment"]:
        amount = round(random.uniform(50, 500), 2)
    elif t_type == "ATM Withdrawal":
        amount = round(random.choice([20, 50, 100, 200]), 2)
    else:
        amount = round(random.uniform(10, 150), 2)
        
    # Description
    base_desc = random.choice(DESCRIPTIONS[t_type])
    desc = f"{base_desc}. Normal activity consistent with customer profile."
    
    # Generate AlertID
    alert_id = f"ALT-{random.randint(10000, 99999)}"
    
    data.append({
        "AlertID": alert_id,
        "Customer Name": customer,
        "Transaction Type": t_type,
        "Amount": amount,
        "Date": date,
        "Description": desc
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save
output_path = "huge_normal_transactions.csv"
df.to_csv(output_path, index=False)

print(f"Generated {NUM_TRANSACTIONS} clean records to {output_path}")
