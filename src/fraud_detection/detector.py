
import pandas as pd
import joblib
import json
from typing import Dict, Any, List
from .features import FeatureEngineer

class FraudDetector:
    def __init__(self, model_dir: str = "models", kyc_path: str = "data/kyc_data.json"):
        self.xgb_model = joblib.load(f"{model_dir}/rf_fraud.pkl") # Renamed for consistency in code logic, keeping var name to avoid huge refactor
        self.iso_forest = joblib.load(f"{model_dir}/iso_forest.pkl")
        self.kyc_path = kyc_path
        # In a real system, KYC data would be in a DB
        with open(kyc_path, 'r') as f:
            self.kyc_data = json.load(f)
        self.kyc_df = pd.DataFrame(self.kyc_data)

    def predict_transaction(self, transaction: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predicts if a single transaction is fraudulent.
        Requires history to compute features like velocity.
        """
        # Combine current transaction with history
        all_tx = history + [transaction]
        
        # Create temporary DataFrame
        df = pd.DataFrame(all_tx)
        
        # Feature Engineering (We reuse the logic, though inefficient for single prediction)
        # In production: Use a Feature Store
        fe = FeatureEngineer(transactions_path=None, kyc_path=None) # Mock init
        fe.transactions = df
        fe.kyc = self.kyc_df
        
        # We need to adapt the FE class to work with in-memory DF
        # For this prototype, let's assume we can use the class methods
        # Hack: overwrite the load methods or pass DFs directly if we modified the class
        # Let's use a simplified feature extraction here for the single row
        
        # ... actually, let's use the bulk processing for simplicity in this POC
        # Re-initializing FE efficiently
        fe.df = fe.transactions.merge(fe.kyc, on='customer_id', how='left')
        fe.df['timestamp'] = pd.to_datetime(fe.df['timestamp'])
        fe.df = fe.df.sort_values(by=['customer_id', 'timestamp'])
        
        fe._create_transaction_features()
        fe._create_customer_features()
        
        # Extract features for the LAST transaction (the current one)
        features = [
            'amount', 'time_since_last_tx', 'velocity_1h', 'velocity_24h', 
            'vol_1h', 'amount_zscore', 'risk_rating_encoded', 'is_senior', 
            'age', 'annual_income'
        ]
        
        current_features = fe.df.iloc[[-1]][features]
        
        # Predict
        prob_fraud = self.xgb_model.predict_proba(current_features)[0][1]
        is_anomaly = self.iso_forest.predict(current_features)[0] # -1 for outlier
        
        is_flagged = prob_fraud > 0.7 or is_anomaly == -1
        
        result = {
            "transaction_id": transaction['transaction_id'],
            "fraud_probability": float(prob_fraud),
            "is_anomaly": bool(is_anomaly == -1),
            "alert": bool(is_flagged),
            "reasons": []
        }
        
        if prob_fraud > 0.7:
            result['reasons'].append(f"High fraud probability model score: {prob_fraud:.2f}")
        if is_anomaly == -1:
            result['reasons'].append("Detected as anomaly by Isolation Forest")
            
        return result

if __name__ == "__main__":
    # Test
    detector = FraudDetector()
    
    # Mock data
    customer_id = "CUST-MOCK"
    history = [] # Empty history for now
    tx = {
        "transaction_id": "TX-TEST",
        "customer_id": "CUST-8AF29240", # Needs to match a real customer from training for KYC merge
        "timestamp": "2024-01-01T12:00:00",
        "amount": 5000.00
    }
    
    # We need to pick a valid customer ID from the files
    import json
    with open("data/kyc_data.json") as f:
        cust = json.load(f)[0]
        tx['customer_id'] = cust['customer_id']
        
    print(f"Testing transaction for {tx['customer_id']}...")
    res = detector.predict_transaction(tx, [])
    print(res)
