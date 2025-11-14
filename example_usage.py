#!/usr/bin/env python3
"""
Example script demonstrating the Suspicious Activity Detection API

This script shows how to:
1. Add entities (persons/organizations)
2. Record transactions
3. File Suspicious Activity Reports (SARs)
4. Detect suspicious patterns
5. Perform risk analysis
6. Visualize entity relationships
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://127.0.0.1:5000"


def print_response(title, response):
    """Pretty print API responses"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)
    print(json.dumps(response.json(), indent=2))


def main():
    """Run example scenarios"""
    
    print("Suspicious Activity Detection API - Example Usage")
    print("=" * 60)
    
    # 1. Add entities
    print("\n1. Adding entities...")
    
    entities = [
        {
            "entity_id": "E001",
            "name": "Alice Johnson",
            "entity_type": "person",
            "identifiers": {"ssn": "123-45-6789", "account": "ACC001"}
        },
        {
            "entity_id": "E002",
            "name": "Bob Smith",
            "entity_type": "person",
            "identifiers": {"ssn": "987-65-4321", "account": "ACC002"}
        },
        {
            "entity_id": "E003",
            "name": "Charlie Corp",
            "entity_type": "organization",
            "identifiers": {"ein": "12-3456789"}
        }
    ]
    
    for entity in entities:
        response = requests.post(f"{BASE_URL}/api/entities", json=entity)
        print(f"  Added {entity['name']}: {response.json()['status']}")
    
    # 2. Record transactions (structuring pattern)
    print("\n2. Recording transactions (potential structuring)...")
    
    now = datetime.now()
    transactions = []
    
    # Create pattern: multiple transactions just below $10k threshold
    for i in range(5):
        transaction = {
            "transaction_id": f"T00{i+1}",
            "timestamp": (now - timedelta(days=i)).isoformat(),
            "amount": 9500.0 + (i * 100),  # Varying amounts but all below 10k
            "currency": "USD",
            "sender_id": "E001",
            "receiver_id": "E002",
            "transaction_type": "wire_transfer",
            "description": f"Payment {i+1}"
        }
        response = requests.post(f"{BASE_URL}/api/transactions", json=transaction)
        print(f"  Transaction {transaction['transaction_id']}: "
              f"${transaction['amount']:.2f} - {response.json()['status']}")
        transactions.append(transaction)
    
    # 3. Add circular transaction pattern
    print("\n3. Adding circular transaction pattern...")
    
    circular_transactions = [
        {"transaction_id": "TC01", "sender_id": "E001", "receiver_id": "E002",
         "amount": 15000.0},
        {"transaction_id": "TC02", "sender_id": "E002", "receiver_id": "E003",
         "amount": 14500.0},
        {"transaction_id": "TC03", "sender_id": "E003", "receiver_id": "E001",
         "amount": 14000.0},
    ]
    
    for trans in circular_transactions:
        trans.update({
            "timestamp": now.isoformat(),
            "currency": "USD",
            "transaction_type": "wire_transfer",
            "description": "Business payment"
        })
        response = requests.post(f"{BASE_URL}/api/transactions", json=trans)
        print(f"  {trans['transaction_id']}: "
              f"{trans['sender_id']} → {trans['receiver_id']} "
              f"${trans['amount']:.2f}")
    
    # 4. File a SAR
    print("\n4. Filing a Suspicious Activity Report...")
    
    sar = {
        "sar_id": "SAR001",
        "filing_date": now.isoformat(),
        "activity_type": "structuring",
        "entities_involved": ["E001"],
        "transactions_involved": [t["transaction_id"] for t in transactions],
        "narrative": (
            "Subject made multiple wire transfers just below $10,000 reporting "
            "threshold over a 5-day period. Total amount: $47,500. Pattern "
            "consistent with structuring to avoid Currency Transaction Report "
            "filing requirements. Multiple transactions to same beneficiary."
        ),
        "risk_level": "high",
        "amount_involved": sum(t["amount"] for t in transactions),
        "time_period_start": (now - timedelta(days=7)).isoformat(),
        "time_period_end": now.isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/api/sars", json=sar)
    print_response("SAR Filing Result", response)
    
    # 5. Detect patterns
    print("\n5. Detecting suspicious patterns for E001...")
    response = requests.get(f"{BASE_URL}/api/patterns/detect/E001")
    print_response("Pattern Detection Results", response)
    
    # 6. Risk analysis
    print("\n6. Performing risk analysis for E001...")
    response = requests.get(f"{BASE_URL}/api/risk-analysis/E001")
    print_response("Risk Analysis Report", response)
    
    # 7. Get entity graph
    print("\n7. Retrieving entity relationship graph...")
    response = requests.get(f"{BASE_URL}/api/graph/E001?depth=2")
    data = response.json()
    
    print("\n" + "=" * 60)
    print("Entity Relationship Graph")
    print("=" * 60)
    print(f"Nodes: {len(data['graph']['nodes'])}")
    for node in data['graph']['nodes']:
        print(f"  - {node['name']} ({node['id']}): "
              f"Risk={node['risk_score']:.2f}")
    
    print(f"\nEdges: {len(data['graph']['edges'])}")
    for edge in data['graph']['edges']:
        print(f"  - {edge['source']} → {edge['target']}: "
              f"${edge['amount']:.2f}")
    
    # 8. System statistics
    print("\n8. System statistics...")
    response = requests.get(f"{BASE_URL}/api/stats")
    print_response("System Statistics", response)
    
    # 9. Find similar SARs
    print("\n9. Finding similar SARs...")
    
    # Add another SAR for comparison
    sar2 = {
        "sar_id": "SAR002",
        "filing_date": now.isoformat(),
        "activity_type": "structuring",
        "entities_involved": ["E002"],
        "transactions_involved": ["TC01"],
        "narrative": (
            "Multiple transactions below reporting threshold detected. "
            "Subject appears to be structuring transactions to avoid detection."
        ),
        "risk_level": "medium",
        "amount_involved": 25000.0,
        "time_period_start": (now - timedelta(days=5)).isoformat(),
        "time_period_end": now.isoformat()
    }
    requests.post(f"{BASE_URL}/api/sars", json=sar2)
    
    response = requests.get(f"{BASE_URL}/api/sars/similar/SAR001?threshold=0.4")
    print_response("Similar SARs", response)
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API.")
        print("Please make sure the Flask server is running:")
        print("  python -m app")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
