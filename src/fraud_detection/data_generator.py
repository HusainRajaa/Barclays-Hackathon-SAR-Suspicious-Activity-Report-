
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import pandas as pd
import numpy as np

fake = Faker()

# Configuration
NUM_CUSTOMERS = 100
START_DATE = datetime.now() - timedelta(days=90)
END_DATE = datetime.now()

class FraudDataGenerator:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.customers = []
        self.transactions = []
        
    def generate_customers(self, num: int = NUM_CUSTOMERS):
        """Generates synthetic KYC profiles."""
        risk_categories = ['Low', 'Medium', 'High']
        occupations = ['Engineer', 'Doctor', 'Student', 'Artist', 'Business Owner', 'Unemployed']
        
        for _ in range(num):
            customer = {
                "customer_id": f"CUST-{uuid.uuid4().hex[:8].upper()}",
                "name": fake.name(),
                "age": random.randint(18, 90),
                "occupation": random.choice(occupations),
                "annual_income": round(random.uniform(10000, 200000), 2),
                "risk_rating": random.choice(risk_categories),
                "country": fake.country(),
                "account_created": fake.date_between(start_date='-5y', end_date='today').isoformat()
            }
            self.customers.append(customer)
        
        print(f"Generated {len(self.customers)} customers.")
        return self.customers

    def generate_transactions(self):
        """Generates transactions for existing customers, injecting fraud patterns."""
        if not self.customers:
            raise ValueError("No customers found. Generate customers first.")

        for customer in self.customers:
            # Randomly decide if this customer is a fraudster (5% chance)
            is_fraudster = random.random() < 0.05
            
            if is_fraudster:
                self._generate_fraud_patterns(customer)
            else:
                self._generate_normal_behavior(customer)
        
        print(f"Generated {len(self.transactions)} transactions.")
        return self.transactions

    def _generate_normal_behavior(self, customer: Dict):
        """Generates normal spending patterns."""
        num_tx = random.randint(5, 50)
        curr_date = START_DATE
        
        for _ in range(num_tx):
            # Advance time randomly
            curr_date += timedelta(hours=random.randint(1, 120))
            if curr_date > END_DATE:
                break
                
            amount = round(random.uniform(10, 2000), 2)
            
            tx = {
                "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
                "customer_id": customer['customer_id'],
                "timestamp": curr_date.isoformat(),
                "amount": amount,
                "currency": "USD",
                "merchant": fake.company(),
                "category": random.choice(['Retail', 'Food', 'Travel', 'Utilities']),
                "is_fraud": 0
            }
            self.transactions.append(tx)

    def _generate_fraud_patterns(self, customer: Dict):
        """Injects specific fraud scenarios."""
        scenario = random.choice(['structuring', 'velocity', 'high_value'])
        
        curr_date = START_DATE + timedelta(days=random.randint(0, 60))
        
        if scenario == 'structuring':
            # Many small transactions just below $10,000 threshold
            for _ in range(random.randint(5, 10)):
                curr_date += timedelta(minutes=random.randint(10, 60))
                amount = round(random.uniform(9000, 9900), 2)
                self._add_tx(customer, curr_date, amount, 1, "Structuring")
                
        elif scenario == 'velocity':
            # Many transactions in a very short time
            for _ in range(random.randint(10, 20)):
                curr_date += timedelta(seconds=random.randint(30, 300))
                amount = round(random.uniform(100, 500), 2)
                self._add_tx(customer, curr_date, amount, 1, "High Velocity")
                
        elif scenario == 'high_value':
            # Sudden massive transaction
            curr_date += timedelta(days=1)
            amount = round(random.uniform(50000, 200000), 2)
            self._add_tx(customer, curr_date, amount, 1, "High Value Anomaly")

    def _add_tx(self, customer, date, amount, is_fraud, pattern=None):
        tx = {
            "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
            "customer_id": customer['customer_id'],
            "timestamp": date.isoformat(),
            "amount": amount,
            "currency": "USD",
            "merchant": fake.company(),
            "category": "Fraudulent",
            "is_fraud": is_fraud,
            "fraud_pattern": pattern
        }
        self.transactions.append(tx)

    def save_data(self):
        """Saves generated data to JSON and CSV."""
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save Customers
        with open(f"{self.output_dir}/kyc_data.json", 'w') as f:
            json.dump(self.customers, f, indent=2)
            
        # Save Transactions
        with open(f"{self.output_dir}/transactions.json", 'w') as f:
            json.dump(self.transactions, f, indent=2)
            
        # Also save as CSV for ML training
        pd.DataFrame(self.transactions).to_csv(f"{self.output_dir}/transactions.csv", index=False)
        print(f"Data saved to {self.output_dir}/")

if __name__ == "__main__":
    gen = FraudDataGenerator()
    gen.generate_customers(200)
    gen.generate_transactions()
    gen.save_data()
