
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

class FeatureEngineer:
    def __init__(self, transactions: Optional[pd.DataFrame] = None, kyc: Optional[pd.DataFrame] = None, 
                 transactions_path: Optional[str] = None, kyc_path: Optional[str] = None):
        """
        Initializes FeatureEngineer. Can accept dataframes directly (Real-time) or paths (Batch).
        """
        if transactions is not None:
            self.transactions = transactions
        elif transactions_path:
            self.transactions = pd.read_json(transactions_path)
        else:
            self.transactions = pd.DataFrame()

        if kyc is not None:
            self.kyc = kyc
        elif kyc_path:
            self.kyc = pd.read_json(kyc_path)
        else:
            self.kyc = pd.DataFrame()

        self.df = pd.DataFrame()

    def _preprocess(self):
        """Merges and cleans data."""
        if self.transactions.empty:
            return

        # Convert timestamp if string
        if self.transactions['timestamp'].dtype == 'O':
            self.transactions['timestamp'] = pd.to_datetime(self.transactions['timestamp'])

        # Merge with KYC
        if not self.kyc.empty:
            self.df = self.transactions.merge(self.kyc, on='customer_id', how='left')
        else:
            self.df = self.transactions.copy()

        # Sort by customer and time
        self.df = self.df.sort_values(by=['customer_id', 'timestamp'])

    def _create_transaction_features(self):
        """Creates velocity and pattern features."""
        if self.df.empty:
            return

        # Time since last transaction
        self.df['time_since_last_tx'] = self.df.groupby('customer_id')['timestamp'].diff().dt.total_seconds().fillna(0)

        # Velocity Features (rolling windows)
        # We need to set timestamp as index for rolling features
        temp_df = self.df.set_index('timestamp')
        
        # Group by customer and compute rolling counts and sums
        grouped = temp_df.groupby('customer_id')['amount']
        
        # Velocity: Count of transactions
        self.df['velocity_1h'] = grouped.rolling('1h').count().values
        self.df['velocity_24h'] = grouped.rolling('24h').count().values
        
        # Volume: Sum of amounts
        self.df['vol_1h'] = grouped.rolling('1h').sum().values
        self.df['vol_24h'] = grouped.rolling('24h').sum().values

    def _create_customer_features(self):
        """Encodes customer profile features."""
        if self.df.empty:
            return

        # Normalize amount by customer's history (z-score)
        # In batch: use transform. In real-time: this is an approximation or needs external state.
        # Here we use expanding window for a robust approximation that works in both.
        means = self.df.groupby('customer_id')['amount'].expanding().mean().reset_index(0, drop=True)
        stds = self.df.groupby('customer_id')['amount'].expanding().std().fillna(1).reset_index(0, drop=True)
        
        # Align indexes
        self.df['amount_mean_hist'] = means
        self.df['amount_std_hist'] = stds
        
        # Avoid division by zero
        self.df['amount_zscore'] = (self.df['amount'] - self.df['amount_mean_hist']) / (self.df['amount_std_hist'] + 1e-9)

        # Encode Risk Rating
        if 'risk_rating' in self.df.columns:
            risk_map = {'Low': 0, 'Medium': 1, 'High': 2}
            self.df['risk_rating_encoded'] = self.df['risk_rating'].map(risk_map).fillna(0)
        else:
            self.df['risk_rating_encoded'] = 1 # Default Medium

        # Age bucket
        if 'age' in self.df.columns:
            self.df['is_senior'] = (self.df['age'] > 60).astype(int)
        else:
            self.df['is_senior'] = 0

    def create_features(self) -> pd.DataFrame:
        self._preprocess()
        self._create_transaction_features()
        self._create_customer_features()

        # Select columns for model
        feature_cols = [
            'amount', 'time_since_last_tx', 'velocity_1h', 'velocity_24h', 
            'vol_1h', 'amount_zscore', 'risk_rating_encoded', 'is_senior', 
            'age', 'annual_income'
        ]
        
        # Ensure all columns exist, fill with 0 if missing (robustness)
        for col in feature_cols:
            if col not in self.df.columns:
                self.df[col] = 0
                
        # Add target if present
        if 'is_fraud' in self.df.columns:
            feature_cols.append('is_fraud')

        # Drop NaNs created by rolling windows/diff (first records)
        # Or fill them with valid defaults
        return self.df[feature_cols].fillna(0)

if __name__ == "__main__":
    fe = FeatureEngineer(transactions_path="data/transactions.json", kyc_path="data/kyc_data.json")
    df_features = fe.create_features()
    df_features.to_csv("data/model_features.csv", index=False)
    print("Features saved to data/model_features.csv")
