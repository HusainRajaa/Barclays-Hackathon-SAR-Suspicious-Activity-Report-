import pandas as pd
import json

def generate_regulatory_docs():
    """
    Generates synthetic regulatory documents (FCA/FinCEN style rules).
    Returns a list of strings (documents).
    """
    docs = [
        "Structuring (Smurfing): It is illegal to break down large cash deposits into smaller amounts to avoid the reporting threshold of $10,000. This practice is known as structuring.",
        "Layering: A money laundering stage involving complex layers of financial transactions to obscure the source of funds. Frequent transfers between multiple accounts without clear economic purpose is a red flag.",
        "High-Risk Jurisdictions: Transactions involving countries identified as high-risk by the FATF require Enhanced Due Diligence (EDD). Unexplained transfers to these regions are suspicious.",
        "Round Dollar Values: Frequent transactions in round dollar amounts (e.g., $5,000, $9,000) solely to avoid scrutiny or appear normal is a behavioral red flag.",
        "Rapid Movement of Funds: Funds deposited and immediately withdrawn or transferred (velocity of funds) indicates a pass-through account usage, often for laundering."
    ]
    return docs

def generate_mock_alerts():
    """
    Generates synthetic transaction alerts.
    Returns a DataFrame.
    """
    test_alerts = [
        {
            "AlertID": "ALT-001",
            "Customer Name": "John Doe",
            "Transaction Type": "Cash Deposit",
            "Amount": 9500.00,
            "Date": "2023-10-25",
            "Risk Score": "High",
            "Description": "Customer made 3 separate cash deposits of $9,500, $9,000, and $8,500 in consecutive days."
        },
        {
            "AlertID": "ALT-002",
            "Customer Name": "Acme Shell Corp",
            "Transaction Type": "Wire Transfer",
            "Amount": 250000.00,
            "Date": "2023-10-26",
            "Risk Score": "Critical",
            "Description": "Large wire transfer to 'Offshore Holdings Ltd' in Cayman Islands immediately after receipt of funds."
        }
    ]
    return pd.DataFrame(test_alerts)

if __name__ == "__main__":
    docs = generate_regulatory_docs()
    alerts = generate_mock_alerts()
    
    print(f"Generated {len(docs)} regulatory documents.")
    print(f"Generated {len(alerts)} test alerts.")
    
    # Save to files for inspection
    with open("regulatory_docs.json", "w") as f:
        json.dump(docs, f, indent=2)
    
    alerts.to_csv("test_alerts.csv", index=False)
    print("Saved to regulatory_docs.json and test_alerts.csv")
