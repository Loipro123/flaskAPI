# Suspicious Activity Detection API Documentation

## Overview

This API provides advanced suspicious activity detection capabilities using AI and GraphRAG (Graph-based Retrieval Augmented Generation) to identify patterns across Suspicious Activity Reports (SARs) and transaction data.

## Features

- **Entity Management**: Track individuals and organizations
- **Transaction Monitoring**: Record and analyze financial transactions
- **SAR Integration**: File and analyze Suspicious Activity Reports
- **Pattern Detection**: Automatically detect suspicious patterns including:
  - Structuring (multiple transactions below reporting threshold)
  - Circular transactions (money laundering indicator)
  - Rapid fund movement (layering indicator)
- **Risk Analysis**: Comprehensive risk scoring and analysis
- **Graph Visualization**: Entity relationship mapping
- **AI-Powered Similarity**: Find related SARs using semantic analysis

## API Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### System Statistics

**GET** `/api/stats`

Get overall system statistics.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_entities": 150,
    "total_transactions": 1200,
    "total_sars": 45,
    "graph_nodes": 150,
    "graph_edges": 1200,
    "high_risk_entities": 12
  }
}
```

### Entity Management

#### Add Entity

**POST** `/api/entities`

Add a new entity (person or organization) to the system.

**Request Body:**
```json
{
  "entity_id": "E001",
  "name": "John Doe",
  "entity_type": "person",
  "identifiers": {
    "ssn": "123-45-6789",
    "account": "ACC001"
  },
  "risk_score": 0.0,
  "risk_level": "low",
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Entity added successfully",
  "entity_id": "E001"
}
```

### Transaction Management

#### Add Transaction

**POST** `/api/transactions`

Record a new financial transaction.

**Request Body:**
```json
{
  "transaction_id": "T001",
  "timestamp": "2024-01-15T14:30:00",
  "amount": 9500.0,
  "currency": "USD",
  "sender_id": "E001",
  "receiver_id": "E002",
  "transaction_type": "wire_transfer",
  "description": "Payment for services",
  "location": "New York, NY",
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Transaction added successfully",
  "transaction_id": "T001"
}
```

### SAR Management

#### Add SAR

**POST** `/api/sars`

File a Suspicious Activity Report.

**Request Body:**
```json
{
  "sar_id": "SAR001",
  "filing_date": "2024-01-15T10:00:00",
  "activity_type": "structuring",
  "entities_involved": ["E001"],
  "transactions_involved": ["T001", "T002", "T003"],
  "narrative": "Multiple transactions below $10,000 threshold to avoid reporting",
  "risk_level": "high",
  "amount_involved": 50000.0,
  "time_period_start": "2024-01-01T00:00:00",
  "time_period_end": "2024-01-15T00:00:00",
  "metadata": {}
}
```

**Activity Types:**
- `structuring`
- `money_laundering`
- `fraud`
- `terrorist_financing`
- `unusual_transaction`
- `multiple_accounts`
- `high_risk_jurisdiction`

**Risk Levels:**
- `low`
- `medium`
- `high`
- `critical`

**Response:**
```json
{
  "status": "success",
  "message": "SAR added successfully",
  "sar_id": "SAR001",
  "analysis": {
    "sar_id": "SAR001",
    "primary_pattern": "structuring",
    "confidence": 0.8,
    "secondary_patterns": [],
    "risk_indicators": ["high_value", "rapid_movement"]
  }
}
```

### Pattern Detection

#### Detect Patterns for Entity

**GET** `/api/patterns/detect/{entity_id}`

Detect suspicious patterns for a specific entity.

**Response:**
```json
{
  "status": "success",
  "entity_id": "E001",
  "patterns_detected": 2,
  "patterns": [
    {
      "pattern_id": "structuring_E001_1705329600.0",
      "type": "structuring",
      "confidence": 0.7,
      "risk_level": "high",
      "description": "Detected 5 transactions totaling $47,500.00 in 7 days, potentially to avoid reporting thresholds"
    },
    {
      "pattern_id": "rapid_movement_E001_1705329600.0",
      "type": "rapid_movement",
      "confidence": 0.6,
      "risk_level": "medium",
      "description": "Detected 8 transactions totaling $80,000.00 in 24 hours"
    }
  ]
}
```

### Risk Analysis

#### Get Risk Analysis

**GET** `/api/risk-analysis/{entity_id}`

Get comprehensive risk analysis for an entity.

**Response:**
```json
{
  "status": "success",
  "report": {
    "entity_id": "E001",
    "generated_at": "2024-01-15T15:00:00",
    "risk_score": 0.75,
    "risk_level": "high",
    "findings": [
      "Connected to 15 entities",
      "Involved in 3 SARs",
      "Total transaction volume: $500,000.00"
    ],
    "related_sars": [
      {
        "sar_id": "SAR001",
        "activity_type": "structuring",
        "risk_level": "high"
      }
    ],
    "detected_patterns": ["uniform_amounts", "rapid_succession"],
    "recommendations": [
      "Enhanced monitoring recommended",
      "Review transaction patterns",
      "Investigate for potential structuring activity"
    ]
  }
}
```

### Graph Visualization

#### Get Entity Graph

**GET** `/api/graph/{entity_id}?depth=2`

Get graph visualization data for an entity and its connections.

**Query Parameters:**
- `depth` (optional): How many levels deep to traverse (default: 2)

**Response:**
```json
{
  "status": "success",
  "entity_id": "E001",
  "graph": {
    "nodes": [
      {
        "id": "E001",
        "name": "John Doe",
        "type": "person",
        "risk_score": 0.75
      },
      {
        "id": "E002",
        "name": "Jane Smith",
        "type": "person",
        "risk_score": 0.3
      }
    ],
    "edges": [
      {
        "source": "E001",
        "target": "E002",
        "amount": 9500.0,
        "transaction_id": "T001"
      }
    ]
  }
}
```

### SAR Similarity

#### Find Similar SARs

**GET** `/api/sars/similar/{sar_id}?threshold=0.5`

Find SARs with similar patterns using AI semantic analysis.

**Query Parameters:**
- `threshold` (optional): Similarity threshold 0.0-1.0 (default: 0.5)

**Response:**
```json
{
  "status": "success",
  "sar_id": "SAR001",
  "similar_count": 3,
  "similar_sars": [
    {
      "sar_id": "SAR005",
      "similarity": 0.85,
      "activity_type": "structuring",
      "risk_level": "high",
      "narrative": "Pattern of transactions below reporting threshold..."
    }
  ]
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request
- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Error description here"
}
```

## Use Cases

### 1. Detecting Structuring Activity

```python
# Add multiple transactions below threshold
for i in range(5):
    POST /api/transactions
    {
      "transaction_id": f"T{i}",
      "amount": 9500.0,
      "sender_id": "E001",
      ...
    }

# Detect patterns
GET /api/patterns/detect/E001
```

### 2. Analyzing Entity Risk

```python
# Get comprehensive risk analysis
GET /api/risk-analysis/E001

# Visualize connections
GET /api/graph/E001?depth=3
```

### 3. Finding Related Cases

```python
# File a SAR
POST /api/sars
{
  "sar_id": "SAR001",
  "narrative": "Suspicious layering activity...",
  ...
}

# Find similar cases
GET /api/sars/similar/SAR001?threshold=0.7
```

## GraphRAG Concepts

This API leverages GraphRAG for advanced pattern detection:

1. **Graph Construction**: Entities and transactions form a directed graph
2. **Pattern Detection**: Graph algorithms identify suspicious structures
3. **Risk Propagation**: Risk scores flow through connected entities
4. **Semantic Analysis**: AI identifies similar narratives across SARs

## Security Notes

- This is a prototype system for demonstration purposes
- In production, implement proper authentication and authorization
- Encrypt sensitive data at rest and in transit
- Follow financial regulations and data protection laws
- Maintain audit logs for all operations

## Technical Stack

- **Framework**: Flask 2.3.3
- **Graph Processing**: NetworkX 3.2.1
- **ML/AI**: NumPy 1.26.0, scikit-learn 1.3.2
- **Pattern Detection**: Custom algorithms for financial crime detection
