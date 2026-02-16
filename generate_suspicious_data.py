import pandas as pd
import random
from datetime import datetime, timedelta
import faker

# Initialize Faker
fake = faker.Faker()

# Constants
NUM_TRANSACTIONS = 50
START_DATE = datetime(2025, 1, 1)

PATTERNS = [
    {
        "Type": "Cash Deposit",
        "Risk": "High",
        "Desc_Template": "Multiple cash deposits ({count}) at various branches. Total: ${total}."
    },
    {
        "Type": "Wire Transfer",
        "Risk": "Critical",
        "Desc_Template": "Outgoing Wire to {company} ({country}). Immediate pass-through."
    },
    {
        "Type": "Mixed Activity",
        "Risk": "High",
        "Desc_Template": "Rapid fund movement: Deposit via Check -> Immediate ATM Withdrawal."
    },
    {
        "Type": "Crypto Purchase",
        "Risk": "High",
        "Desc_Template": "High-value transfer to unregulated crypto exchange '{exchange}'."
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
        desc = pattern["Desc_Template"].format(
            count=3,
            total=round(amount, 2)
        )
    elif pattern["Type"] == "Wire Transfer":
        desc = pattern["Desc_Template"].format(
            company=random.choice(SHELL_COMPANIES),
            country=random.choice(HIGH_RISK_COUNTRIES)
        )
    elif pattern["Type"] == "Crypto Purchase":
        desc = pattern["Desc_Template"].format(
            exchange="Binance_Unverified"
        )
    else:
        desc = pattern["Desc_Template"]
    
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
