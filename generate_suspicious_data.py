import pandas as pd
import random
from datetime import datetime, timedelta
import faker

# Initialize Faker
fake = faker.Faker()

# Constants
NUM_TRANSACTIONS = 50
START_DATE = datetime(2025, 1, 1)

# Suspicious Patterns
PATTERNS = [
    {
        "Type": "Cash Deposit",
        "Risk": "High",
        "Desc_Template": "Customer made {count} cash deposits of ${amt1}, ${amt2}, and ${amt3} at different branches. Total exceeds reporting threshold but individual amounts do not."
    },
    {
        "Type": "Wire Transfer",
        "Risk": "Critical",
        "Desc_Template": "Large wire transfer of ${amount} to '{company}' in {country} (High Risk Jurisdiction) immediately after deposit cleared."
    },
    {
        "Type": "Mixed Activity",
        "Risk": "High",
        "Desc_Template": "Account shows rapid movement of funds. ${amount} deposited via check and immediately withdrawn via ATM in small increments."
    },
    {
        "Type": "Crypto Purchase",
        "Risk": "High",
        "Desc_Template": "Multiple transactions to unregistered crypto exchange '{exchange}'. Source of funds unclear."
    }
]

HIGH_RISK_COUNTRIES = ["Cayman Islands", "Panama", "Seychelles", "North Korea"]
SHELL_COMPANIES = ["Global Holdings Ltd", "Oceanic Imports", "Apex Consulting", "Quantum Trade"]

data = []

for _ in range(NUM_TRANSACTIONS):
    # Random Date
    days_offset = random.randint(0, 365)
    date = (START_DATE + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    
    # Customer
    customer = fake.name()
    
    # Pattern
    pattern = random.choice(PATTERNS)
    
    # Generate Amounts
    amount = round(random.uniform(9000, 50000), 2)
    
    # Build Description
    if pattern["Type"] == "Cash Deposit":
        d_amount = amount / 3
        desc = pattern["Desc_Template"].format(
            count=3,
            amt1=round(d_amount - random.uniform(10, 100), 2),
            amt2=round(d_amount + random.uniform(10, 100), 2),
            amt3=round(d_amount, 2)
        )
    elif pattern["Type"] == "Wire Transfer":
        desc = pattern["Desc_Template"].format(
            amount=amount,
            company=random.choice(SHELL_COMPANIES),
            country=random.choice(HIGH_RISK_COUNTRIES)
        )
    elif pattern["Type"] == "Crypto Purchase":
        desc = pattern["Desc_Template"].format(
            exchange="Binance_Unverified"
        )
    else:
        desc = pattern["Desc_Template"].format(amount=amount)
    
    # Generate AlertID
    alert_id = f"ALT-{random.randint(10000, 99999)}"
    
    data.append({
        "AlertID": alert_id,
        "Customer Name": customer,
        "Transaction Type": pattern["Type"],
        "Amount": amount,
        "Date": date,
        "Risk Score": pattern["Risk"],
        "Description": desc
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save
output_path = "suspicious_transactions.csv"
df.to_csv(output_path, index=False)

print(f"Generated {NUM_TRANSACTIONS} suspicious records to {output_path}")
