import pytest
from datetime import datetime, timedelta
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert b"healthy" in response.data


def test_api_endpoint(client):
    """Test main API endpoint"""
    response = client.get("/api")
    assert response.status_code == 200


def test_add_entity(client):
    """Test adding a new entity"""
    entity_data = {
        "entity_id": "E001",
        "name": "John Doe",
        "entity_type": "person",
        "identifiers": {"ssn": "123-45-6789"},
        "risk_score": 0.0,
        "risk_level": "low",
    }
    response = client.post("/api/entities", json=entity_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["entity_id"] == "E001"


def test_add_transaction(client):
    """Test adding a new transaction"""
    # First add entities
    client.post(
        "/api/entities",
        json={
            "entity_id": "E002",
            "name": "Alice",
            "entity_type": "person",
        },
    )
    client.post(
        "/api/entities",
        json={
            "entity_id": "E003",
            "name": "Bob",
            "entity_type": "person",
        },
    )

    transaction_data = {
        "transaction_id": "T001",
        "timestamp": datetime.now().isoformat(),
        "amount": 5000.0,
        "currency": "USD",
        "sender_id": "E002",
        "receiver_id": "E003",
        "transaction_type": "wire_transfer",
    }
    response = client.post("/api/transactions", json=transaction_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"


def test_add_sar(client):
    """Test adding a Suspicious Activity Report"""
    # Add entities first
    client.post(
        "/api/entities",
        json={"entity_id": "E004", "name": "Suspicious User", "entity_type": "person"},
    )

    now = datetime.now()
    sar_data = {
        "sar_id": "SAR001",
        "filing_date": now.isoformat(),
        "activity_type": "structuring",
        "entities_involved": ["E004"],
        "transactions_involved": [],
        "narrative": (
            "Multiple transactions below reporting threshold to avoid detection"
        ),
        "risk_level": "high",
        "amount_involved": 50000.0,
        "time_period_start": (now - timedelta(days=7)).isoformat(),
        "time_period_end": now.isoformat(),
    }
    response = client.post("/api/sars", json=sar_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert "analysis" in data


def test_detect_patterns(client):
    """Test pattern detection for an entity"""
    # Add entity and transactions to create a pattern
    client.post(
        "/api/entities",
        json={"entity_id": "E005", "name": "Pattern Test", "entity_type": "person"},
    )

    # Add multiple transactions below threshold (structuring pattern)
    now = datetime.now()
    for i in range(5):
        client.post(
            "/api/transactions",
            json={
                "transaction_id": f"T_PAT_{i}",
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "amount": 9500.0,
                "currency": "USD",
                "sender_id": "E005",
                "receiver_id": "E999",
                "transaction_type": "wire_transfer",
            },
        )

    response = client.get("/api/patterns/detect/E005")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["entity_id"] == "E005"


def test_risk_analysis(client):
    """Test risk analysis for an entity"""
    # Add entity
    client.post(
        "/api/entities",
        json={"entity_id": "E006", "name": "Risk Test", "entity_type": "person"},
    )

    # Add some transactions
    now = datetime.now()
    for i in range(3):
        client.post(
            "/api/transactions",
            json={
                "transaction_id": f"T_RISK_{i}",
                "timestamp": now.isoformat(),
                "amount": 10000.0,
                "currency": "USD",
                "sender_id": "E006",
                "receiver_id": "E999",
                "transaction_type": "wire_transfer",
            },
        )

    response = client.get("/api/risk-analysis/E006")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "report" in data
    assert "risk_score" in data["report"]


def test_get_entity_graph(client):
    """Test getting graph data for an entity"""
    # Add entities and transactions
    client.post(
        "/api/entities",
        json={"entity_id": "E007", "name": "Graph Test", "entity_type": "person"},
    )
    client.post(
        "/api/entities",
        json={"entity_id": "E008", "name": "Connected", "entity_type": "person"},
    )

    client.post(
        "/api/transactions",
        json={
            "transaction_id": "T_GRAPH_1",
            "timestamp": datetime.now().isoformat(),
            "amount": 5000.0,
            "currency": "USD",
            "sender_id": "E007",
            "receiver_id": "E008",
            "transaction_type": "wire_transfer",
        },
    )

    response = client.get("/api/graph/E007")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "graph" in data
    assert "nodes" in data["graph"]
    assert "edges" in data["graph"]


def test_find_similar_sars(client):
    """Test finding similar SARs"""
    # Add entity
    client.post(
        "/api/entities",
        json={"entity_id": "E009", "name": "SAR Test", "entity_type": "person"},
    )

    # Add first SAR
    now = datetime.now()
    sar1_data = {
        "sar_id": "SAR002",
        "filing_date": now.isoformat(),
        "activity_type": "money_laundering",
        "entities_involved": ["E009"],
        "transactions_involved": [],
        "narrative": "Suspected money laundering through layering and placement",
        "risk_level": "high",
        "amount_involved": 100000.0,
        "time_period_start": (now - timedelta(days=30)).isoformat(),
        "time_period_end": now.isoformat(),
    }
    client.post("/api/sars", json=sar1_data)

    # Add similar SAR
    sar2_data = {
        "sar_id": "SAR003",
        "filing_date": now.isoformat(),
        "activity_type": "money_laundering",
        "entities_involved": ["E009"],
        "transactions_involved": [],
        "narrative": "Money laundering activity detected through integration",
        "risk_level": "high",
        "amount_involved": 80000.0,
        "time_period_start": (now - timedelta(days=20)).isoformat(),
        "time_period_end": now.isoformat(),
    }
    client.post("/api/sars", json=sar2_data)

    response = client.get("/api/sars/similar/SAR002")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"


def test_get_stats(client):
    """Test system statistics endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "stats" in data
    assert "total_entities" in data["stats"]
    assert "total_transactions" in data["stats"]
    assert "total_sars" in data["stats"]


def test_missing_required_fields(client):
    """Test error handling for missing required fields"""
    # Try to add entity without required fields
    response = client.post("/api/entities", json={"entity_id": "E010"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"


def test_invalid_sar_id(client):
    """Test error handling for invalid SAR ID"""
    response = client.get("/api/sars/similar/INVALID_SAR")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
