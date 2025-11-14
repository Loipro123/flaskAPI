# Flask API - Suspicious Activity Detection System

An advanced Flask-based API for detecting suspicious financial activities using AI and GraphRAG (Graph-based Retrieval Augmented Generation).

## Features

### Core Capabilities

- **Advanced Suspicious Activity Detection**: Identify complex patterns across transactions and reports
- **GraphRAG Integration**: Use graph-based algorithms to connect patterns across entities
- **AI-Powered Analysis**: Semantic analysis to find similar suspicious activities
- **Real-time Pattern Detection**: Automatic detection of:
  - Structuring (transactions designed to avoid reporting thresholds)
  - Circular transactions (potential money laundering)
  - Rapid fund movement (layering indicators)
  - Unusual transaction patterns

### Key Features

1. **Entity Management**: Track individuals and organizations with risk scoring
2. **Transaction Monitoring**: Record and analyze financial transactions in real-time
3. **SAR Integration**: File and analyze Suspicious Activity Reports
4. **Pattern Recognition**: Automated detection of financial crime patterns
5. **Risk Analysis**: Comprehensive risk scoring based on multiple factors
6. **Graph Visualization**: Interactive entity relationship mapping
7. **Semantic Search**: Find similar cases using AI-powered analysis

## Technology Stack

- **Framework**: Flask 2.3.3
- **Graph Processing**: NetworkX 3.2.1 - For entity relationship graphs
- **AI/ML**: NumPy 1.26.0, scikit-learn 1.3.2 - For pattern analysis
- **Testing**: pytest, pytest-cov, pytest-xdist
- **Code Quality**: flake8, black, isort, autopep8
- **Security**: bandit, safety

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Loipro123/flaskAPI.git
cd flaskAPI

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Development mode
python -m app

# Production mode with Gunicorn
gunicorn app:app
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

### Quick Example

```python
# Add an entity
POST /api/entities
{
  "entity_id": "E001",
  "name": "John Doe",
  "entity_type": "person"
}

# Add transactions
POST /api/transactions
{
  "transaction_id": "T001",
  "timestamp": "2024-01-15T14:30:00",
  "amount": 9500.0,
  "sender_id": "E001",
  "receiver_id": "E002",
  "transaction_type": "wire_transfer"
}

# Detect patterns
GET /api/patterns/detect/E001

# Get risk analysis
GET /api/risk-analysis/E001
```

## Architecture

### GraphRAG Pattern Detection

The system uses a graph-based approach to detect suspicious patterns:

1. **Graph Construction**: Entities (nodes) and transactions (edges) form a directed graph
2. **Pattern Detection**: 
   - Graph traversal algorithms identify circular patterns
   - Statistical analysis detects structuring
   - Temporal analysis finds rapid movement
3. **Risk Propagation**: Risk scores propagate through connected entities
4. **AI Analysis**: Semantic embeddings identify similar suspicious activities

### Data Models

- **Entity**: Represents persons or organizations
- **Transaction**: Financial transactions between entities
- **SAR**: Suspicious Activity Reports with narratives
- **Pattern**: Detected suspicious patterns
- **Relationship**: Connections between entities

## Use Cases

### 1. Anti-Money Laundering (AML)

Detect money laundering indicators:
- Layering through rapid fund movement
- Integration through circular transactions
- Structuring to avoid reporting

### 2. Fraud Detection

Identify fraudulent patterns:
- Unusual transaction volumes
- Suspicious entity relationships
- High-risk connections

### 3. Compliance Monitoring

Support regulatory compliance:
- Automated SAR analysis
- Risk-based entity monitoring
- Pattern-based alerting

## Development

### Code Quality

```bash
# Linting
flake8 app/ tests/

# Formatting
black app/ tests/
isort app/ tests/

# Security scanning
bandit -r app/
safety check
```

### Project Structure

```
flaskAPI/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Data models
│   ├── graph_service.py     # GraphRAG pattern detection
│   ├── ai_service.py        # AI-powered analysis
│   └── routes.py            # API endpoints
├── tests/
│   ├── test_api.py          # Basic API tests
│   └── test_suspicious_activity.py  # Feature tests
├── requirements.txt         # Dependencies
├── API_DOCUMENTATION.md     # API reference
└── README.md               # This file
```

## Security Considerations

⚠️ **Important**: This is a prototype for demonstration purposes.

For production deployment:
- Implement authentication and authorization
- Encrypt sensitive data at rest and in transit
- Add audit logging for all operations
- Follow financial regulations (e.g., FinCEN, GDPR)
- Implement rate limiting and DDoS protection
- Use secure database solutions
- Regular security audits

## Performance

- Handles thousands of entities and transactions
- Real-time pattern detection
- Efficient graph traversal algorithms
- Optimized for financial data volumes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is for educational and demonstration purposes.

## Contact

Developer: Loi
Goal: Senior Developer with $200k salary in 2 years!

---

**Note**: This is an advanced prototype demonstrating GraphRAG concepts for financial crime detection. It is not intended for production use without proper security hardening and regulatory compliance measures.
