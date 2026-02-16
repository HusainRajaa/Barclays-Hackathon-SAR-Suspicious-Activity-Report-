
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, average_precision_score
import joblib
import os

class FraudModelTrainer:
    def __init__(self, data_path: str = "data/model_features.csv", model_dir: str = "models"):
        self.data_path = data_path
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
    def load_data(self):
        self.df = pd.read_csv(self.data_path)
        self.X = self.df.drop('is_fraud', axis=1)
        self.y = self.df['is_fraud']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, stratify=self.y, random_state=42
        )
        
    def train_supervised(self):
        print("Training Random Forest...")
        from sklearn.ensemble import RandomForestClassifier
        self.clf = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        self.clf.fit(self.X_train, self.y_train)
        
        # Evaluate
        preds = self.clf.predict(self.X_test)
        probas = self.clf.predict_proba(self.X_test)[:, 1]
        
        print("\n--- Supervised Model Report ---")
        print(classification_report(self.y_test, preds))
        print(f"PR-AUC: {average_precision_score(self.y_test, probas):.4f}")
        
        joblib.dump(self.clf, f"{self.model_dir}/xgb_fraud.pkl") # Keeping name for compatibility or change it? Better change it.
        joblib.dump(self.clf, f"{self.model_dir}/rf_fraud.pkl")
        
    def train_unsupervised(self):
        print("\nTraining Isolation Forest...")
        # Train only on normal data usually, or all if we assume fraud is rare
        self.iso_forest = IsolationForest(contamination=0.05, random_state=42)
        self.iso_forest.fit(self.X)  # Unsupervised
        
        joblib.dump(self.iso_forest, f"{self.model_dir}/iso_forest.pkl")

if __name__ == "__main__":
    trainer = FraudModelTrainer()
    trainer.load_data()
    trainer.train_supervised()
    trainer.train_unsupervised()
    print("Models saved to models/")
