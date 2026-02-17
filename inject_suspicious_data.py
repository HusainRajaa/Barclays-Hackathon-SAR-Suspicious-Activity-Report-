import pandas as pd
import random
from datetime import datetime, timedelta
import faker
import os

# Initialize Faker
fake = faker.Faker()

# Constants
EXISTING_FILE = "huge_normal_transactions.csv"
NUM_SUSPICIOUS = 15  # Inject 15 suspicious records

PATTERNS = [
    {
        "Type": "Cash Deposit",
        "Risk": "High",
        "Desc_Template": "Structuring: Multiple cash deposits ({count}) under reporting threshold. Total: ${total}."
    },
    {
        "Type": "Wire Transfer",
        "Risk": "Critical",
        "Desc_Template": "Layering: Outgoing Wire to {company} ({country}) with no economic rationale."
    },
    {
        "Type": "Crypto Purchase",
        "Risk": "High",
        "Desc_Template": "High-value transfer to unregulated crypto exchange '{exchange}'."
    },
    {
        "Type": "Round Dollar",
        "Risk": "Medium",
        "Desc_Template": "Large round dollar transfer: ${amount}. Potential integration."
    }
]

HIGH_RISK_COUNTRIES = ["Cayman Islands", "Panama", "Seychelles", "North Korea", "Russia"]
SHELL_COMPANIES = ["Global Holdings Ltd", "Oceanic Imports", "Apex Consulting", "Quantum Trade", "DarkWeb LLC"]

def generate_suspicious_records(base_date, num_records):
    data = []
    for _ in range(num_records):
        # Random Date within the last year
        days_offset = random.randint(0, 365)
        date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Customer
        customer = fake.name()
        
        # Pattern
        pattern = random.choice(PATTERNS)
        
        # Generate Amounts - Suspiciously high or structured
        if pattern["Type"] == "Cash Deposit":
             # Structuring usually just below 10k
            amount = round(random.uniform(9000, 9900), 2)
            desc = pattern["Desc_Template"].format(
                count=random.randint(3, 8),
                total=amount
            )
        elif pattern["Type"] == "Wire Transfer":
            amount = round(random.uniform(50000, 500000), 2)
            desc = pattern["Desc_Template"].format(
                company=random.choice(SHELL_COMPANIES),
                country=random.choice(HIGH_RISK_COUNTRIES)
            )
        elif pattern["Type"] == "Crypto Purchase":
            amount = round(random.uniform(10000, 100000), 2)
            desc = pattern["Desc_Template"].format(
                exchange="Binance_Unverified"
            )
        elif pattern["Type"] == "Round Dollar":
            amount = float(random.choice([50000, 100000, 250000, 1000000]))
            desc = pattern["Desc_Template"].format(amount=amount)
        else:
            amount = round(random.uniform(10000, 50000), 2)
            desc = pattern["Desc_Template"]
        
        # Generate AlertID
        alert_id = f"ALT-{random.randint(10000, 99999)}"
        
        data.append({
            "AlertID": alert_id,
            "Customer Name": customer,
            "Transaction Type": pattern["Type"],
            "Amount": amount,
            "Date": date,
            "Description": desc
        })
    return pd.DataFrame(data)

def main():
    if not os.path.exists(EXISTING_FILE):
        print(f"Error: {EXISTING_FILE} not found.")
        return

    print(f"Loading {EXISTING_FILE}...")
    df_normal = pd.read_csv(EXISTING_FILE)
    initial_count = len(df_normal)
    print(f"Initial record count: {initial_count}")

    print(f"Generating {NUM_SUSPICIOUS} suspicious records...")
    df_suspicious = generate_suspicious_records(datetime(2025, 1, 1), NUM_SUSPICIOUS)
    
    # Combine
    df_combined = pd.concat([df_normal, df_suspicious], ignore_index=True)
    
    # Shuffle
    df_combined = df_combined.sample(frac=1).reset_index(drop=True)
    
    # Save
    df_combined.to_csv(EXISTING_FILE, index=False)
    print(f"Successfully injected data. New record count: {len(df_combined)}")
    print("Sample suspicious records injected:")
    print(df_suspicious[["Transaction Type", "Description"]].head())

if __name__ == "__main__":
    main()
