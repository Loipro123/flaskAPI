"""
API routes for Suspicious Activity Detection System
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from app.models import (
    Entity,
    Transaction,
    SAR,
    RiskLevel,
    ActivityType,
)
from app.graph_service import GraphRAGService
from app.ai_service import AIAnalysisService

# Create blueprint
suspicious_activity_bp = Blueprint("suspicious_activity", __name__)

# Initialize services
graph_service = GraphRAGService()
ai_service = AIAnalysisService()


@suspicious_activity_bp.route("/api/entities", methods=["POST"])
def add_entity():
    """Add a new entity to the system"""
    try:
        data = request.get_json()

        entity = Entity(
            entity_id=data["entity_id"],
            name=data["name"],
            entity_type=data["entity_type"],
            identifiers=data.get("identifiers", {}),
            risk_score=data.get("risk_score", 0.0),
            risk_level=RiskLevel[data.get("risk_level", "LOW").upper()],
            metadata=data.get("metadata", {}),
        )

        graph_service.add_entity(entity)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Entity added successfully",
                    "entity_id": entity.entity_id,
                }
            ),
            201,
        )
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/transactions", methods=["POST"])
def add_transaction():
    """Add a new transaction to the system"""
    try:
        data = request.get_json()

        transaction = Transaction(
            transaction_id=data["transaction_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            amount=float(data["amount"]),
            currency=data.get("currency", "USD"),
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            transaction_type=data["transaction_type"],
            description=data.get("description"),
            location=data.get("location"),
            metadata=data.get("metadata", {}),
        )

        graph_service.add_transaction(transaction)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Transaction added successfully",
                    "transaction_id": transaction.transaction_id,
                }
            ),
            201,
        )
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/sars", methods=["POST"])
def add_sar():
    """Add a Suspicious Activity Report"""
    try:
        data = request.get_json()

        sar = SAR(
            sar_id=data["sar_id"],
            filing_date=datetime.fromisoformat(data["filing_date"]),
            activity_type=ActivityType[data["activity_type"].upper()],
            entities_involved=data["entities_involved"],
            transactions_involved=data["transactions_involved"],
            narrative=data["narrative"],
            risk_level=RiskLevel[data["risk_level"].upper()],
            amount_involved=float(data["amount_involved"]),
            time_period_start=datetime.fromisoformat(data["time_period_start"]),
            time_period_end=datetime.fromisoformat(data["time_period_end"]),
            metadata=data.get("metadata", {}),
        )

        graph_service.add_sar(sar)

        # Perform AI analysis
        analysis = ai_service.analyze_sar_narrative(sar)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "SAR added successfully",
                    "sar_id": sar.sar_id,
                    "analysis": analysis,
                }
            ),
            201,
        )
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/patterns/detect/<entity_id>", methods=["GET"])
def detect_patterns(entity_id):
    """Detect suspicious patterns for a specific entity"""
    try:
        patterns = []

        # Detect structuring
        structuring_pattern = graph_service.detect_structuring_pattern(entity_id)
        if structuring_pattern:
            patterns.append(
                {
                    "pattern_id": structuring_pattern.pattern_id,
                    "type": structuring_pattern.pattern_type,
                    "confidence": structuring_pattern.confidence_score,
                    "risk_level": structuring_pattern.risk_level.value,
                    "description": structuring_pattern.description,
                }
            )

        # Detect rapid movement
        rapid_pattern = graph_service.detect_rapid_movement(entity_id)
        if rapid_pattern:
            patterns.append(
                {
                    "pattern_id": rapid_pattern.pattern_id,
                    "type": rapid_pattern.pattern_type,
                    "confidence": rapid_pattern.confidence_score,
                    "risk_level": rapid_pattern.risk_level.value,
                    "description": rapid_pattern.description,
                }
            )

        # Detect circular transactions
        circular_patterns = graph_service.detect_circular_transactions()
        for pattern in circular_patterns:
            if entity_id in pattern.entities_involved:
                patterns.append(
                    {
                        "pattern_id": pattern.pattern_id,
                        "type": pattern.pattern_type,
                        "confidence": pattern.confidence_score,
                        "risk_level": pattern.risk_level.value,
                        "description": pattern.description,
                    }
                )

        return (
            jsonify(
                {
                    "status": "success",
                    "entity_id": entity_id,
                    "patterns_detected": len(patterns),
                    "patterns": patterns,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/risk-analysis/<entity_id>", methods=["GET"])
def get_risk_analysis(entity_id):
    """Get comprehensive risk analysis for an entity"""
    try:
        # Get related SARs
        related_sars = graph_service.find_related_sars(entity_id)

        # Get connected entities
        connected_entities = list(
            graph_service.find_connected_entities(entity_id, max_depth=2)
        )

        # Get transactions
        entity_transactions = [
            trans
            for trans_id, trans in graph_service.transactions.items()
            if trans.sender_id == entity_id or trans.receiver_id == entity_id
        ]

        # Analyze transaction patterns
        transaction_analysis = ai_service.analyze_transaction_pattern(
            entity_transactions
        )

        # Compute overall risk
        overall_risk_score, risk_level = ai_service.compute_risk_score(
            entity_connections=len(connected_entities),
            sar_count=len(related_sars),
            transaction_volume=sum(t.amount for t in entity_transactions),
            pattern_count=len(transaction_analysis.get("patterns", [])),
        )

        analysis_data = {
            "risk_score": overall_risk_score,
            "risk_level": risk_level.value,
            "related_sars": [
                {
                    "sar_id": sar.sar_id,
                    "activity_type": sar.activity_type.value,
                    "risk_level": sar.risk_level.value,
                }
                for sar in related_sars
            ],
            "patterns": transaction_analysis.get("patterns", []),
            "findings": [
                f"Connected to {len(connected_entities)} entities",
                f"Involved in {len(related_sars)} SARs",
                (
                    "Total transaction volume: "
                    f"${sum(t.amount for t in entity_transactions): .2f}"
                ),
            ],
        }

        # Generate report
        report = ai_service.generate_risk_report(entity_id, analysis_data)

        return jsonify({"status": "success", "report": report}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/graph/<entity_id>", methods=["GET"])
def get_entity_graph(entity_id):
    """Get graph visualization data for an entity"""
    try:
        depth = int(request.args.get("depth", 2))
        graph_data = graph_service.get_entity_graph_data(entity_id, depth)

        return (
            jsonify({"status": "success", "entity_id": entity_id, "graph": graph_data}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/sars/similar/<sar_id>", methods=["GET"])
def find_similar_sars(sar_id):
    """Find SARs with similar patterns"""
    try:
        if sar_id not in graph_service.sars:
            return jsonify({"status": "error", "message": "SAR not found"}), 404

        sar = graph_service.sars[sar_id]
        all_sars = list(graph_service.sars.values())

        threshold = float(request.args.get("threshold", 0.5))
        similar_sars = ai_service.find_similar_sars(sar, all_sars, threshold)

        results = [
            {
                "sar_id": similar_sar.sar_id,
                "similarity": similarity,
                "activity_type": similar_sar.activity_type.value,
                "risk_level": similar_sar.risk_level.value,
                "narrative": (
                    similar_sar.narrative[: 200] + "..."
                ),
            }
            for similar_sar, similarity in similar_sars
        ]

        return (
            jsonify(
                {
                    "status": "success",
                    "sar_id": sar_id,
                    "similar_count": len(results),
                    "similar_sars": results,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@suspicious_activity_bp.route("/api/stats", methods=["GET"])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            "total_entities": len(graph_service.entities),
            "total_transactions": len(graph_service.transactions),
            "total_sars": len(graph_service.sars),
            "graph_nodes": graph_service.graph.number_of_nodes(),
            "graph_edges": graph_service.graph.number_of_edges(),
            "high_risk_entities": sum(
                1
                for entity in graph_service.entities.values()
                if entity.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            ),
        }

        return jsonify({"status": "success", "stats": stats}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
