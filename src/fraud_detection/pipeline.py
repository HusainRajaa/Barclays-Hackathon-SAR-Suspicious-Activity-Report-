
import json
import os
import random
import uuid
from datetime import datetime
from typing import List, Dict
from src.fraud_detection.detector import FraudDetector
from src.fraud_detection.data_generator import FraudDataGenerator

class FraudPipeline:
    def __init__(self, alerts_output_path: str = "data/generated_alerts.json"):
        self.detector = FraudDetector()
        self.alerts_output_path = alerts_output_path
        
    def run_simulation(self, num_transactions: int = 50):
        """
        Simulates live transactions, detects fraud, and saves alerts.
        """
        print(f"Running simulation for {num_transactions} transactions...")
        
        # Load existing valid customers to generate realistic transactions
        with open("data/kyc_data.json", 'r') as f:
            customers = json.load(f)
            
        generated_alerts = []
        
        # Simple simulation: Pick random customers and generate a transaction
        for _ in range(num_transactions):
            customer = random.choice(customers)
            
            # 10% chance of being high risk transaction
            is_risky = random.random() < 0.1
            amount = round(random.uniform(10, 5000) if not is_risky else random.uniform(9000, 20000), 2)
            
            tx = {
                "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
                "customer_id": customer['customer_id'],
                "timestamp": datetime.now().isoformat(),
                "amount": amount,
                "currency": "USD",
                "merchant": "Simulated Merchant",
                "category": "General",
                "is_fraud": 0 # Unknown in reality
            }
            
            # Predict
            # In a real system, we'd fetch history from a DB
            history = [] 
            result = self.detector.predict_transaction(tx, history)
            
            if result['alert']:
                print(f"ALARM! Transaction {tx['transaction_id']} flagged. Probability: {result['fraud_probability']:.2f}")
                
                alert_record = {
                    "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    "transaction_id": tx['transaction_id'],
                    "customer_id": tx['customer_id'],
                    "alert_date": datetime.now().isoformat().split('T')[0],
                    "risk_score": result['fraud_probability'],
                    "anomaly_detected": result['is_anomaly'],
                    "reasons": result['reasons'],
                    "transaction_details": tx
                }
                generated_alerts.append(alert_record)
        
        # Save alerts
        with open(self.alerts_output_path, 'w') as f:
            json.dump(generated_alerts, f, indent=2)
            
        print(f"\nSimulation complete. {len(generated_alerts)} alerts generated and saved to {self.alerts_output_path}")

if __name__ == "__main__":
    pipeline = FraudPipeline()
    pipeline.run_simulation(100)
