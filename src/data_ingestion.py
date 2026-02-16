import json
import pandas as pd
from typing import Dict, Any, List

class DataIngestion:
    def __init__(self, alerts_path: str, kyc_path: str):
        self.alerts_path = alerts_path
        self.kyc_path = kyc_path

    def load_alerts(self) -> List[Dict[str, Any]]:
        """Loads transaction alerts from a JSON file."""
        try:
            with open(self.alerts_path, 'r') as f:
                alerts = json.load(f)
            return alerts
        except FileNotFoundError:
            print(f"Error: Alert file not found at {self.alerts_path}")
            return []

    def load_kyc_data(self) -> Dict[str, Any]:
        """Loads customer KYC profiles from a JSON file."""
        try:
            with open(self.kyc_path, 'r') as f:
                kyc_data = json.load(f)
            return kyc_data
        except FileNotFoundError:
            print(f"Error: KYC file not found at {self.kyc_path}")
            return {}

    def get_enriched_alert(self, alert_id: str) -> Dict[str, Any]:
        """Combines alert data with customer KYC details."""
        alerts = self.load_alerts()
        kyc_data = self.load_kyc_data()

        target_alert = next((a for a in alerts if a['alert_id'] == alert_id), None)
        
        if not target_alert:
            return {}

        customer_id = target_alert.get('customer_id')
        customer_profile = kyc_data.get(customer_id, {})

        return {
            "alert_details": target_alert,
            "customer_profile": customer_profile
        }

if __name__ == "__main__":
    # Test execution
    ingestor = DataIngestion(
        alerts_path="data/transactions/mock_alerts.json",
        kyc_path="data/kyc/customer_profile.json"
    )
    enriched_data = ingestor.get_enriched_alert("ALT-2024-001")
    print(json.dumps(enriched_data, indent=2))
