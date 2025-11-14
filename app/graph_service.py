"""
Graph-based service for pattern detection using GraphRAG concepts
"""
import networkx as nx
from typing import List, Dict, Set, Optional
from datetime import datetime
from collections import defaultdict  # noqa: F401

from app.models import (
    Entity,
    Transaction,
    SAR,
    Pattern,
    RiskLevel,
)


class GraphRAGService:
    """
    Service for managing entity-relationship graph and detecting suspicious patterns
    using Graph-based Retrieval Augmented Generation concepts
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.sars: Dict[str, SAR] = {}

    def add_entity(self, entity: Entity):
        """Add an entity to the graph"""
        self.entities[entity.entity_id] = entity
        self.graph.add_node(
            entity.entity_id,
            type="entity",
            name=entity.name,
            entity_type=entity.entity_type,
            risk_score=entity.risk_score,
        )

    def add_transaction(self, transaction: Transaction):
        """Add a transaction and create edges between entities"""
        self.transactions[transaction.transaction_id] = transaction

        # Ensure entities exist
        if transaction.sender_id not in self.graph:
            self.graph.add_node(transaction.sender_id, type="entity")
        if transaction.receiver_id not in self.graph:
            self.graph.add_node(transaction.receiver_id, type="entity")

        # Add edge representing the transaction
        self.graph.add_edge(
            transaction.sender_id,
            transaction.receiver_id,
            transaction_id=transaction.transaction_id,
            amount=transaction.amount,
            timestamp=transaction.timestamp,
            transaction_type=transaction.transaction_type,
        )

    def add_sar(self, sar: SAR):
        """Add a SAR and update risk scores"""
        self.sars[sar.sar_id] = sar

        # Update risk scores for involved entities
        for entity_id in sar.entities_involved:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                # Increase risk score based on SAR risk level
                risk_increase = {
                    RiskLevel.LOW: 0.1,
                    RiskLevel.MEDIUM: 0.25,
                    RiskLevel.HIGH: 0.5,
                    RiskLevel.CRITICAL: 0.8,
                }
                entity.risk_score = min(
                    1.0, entity.risk_score + risk_increase.get(sar.risk_level, 0.1)
                )

                # Update risk level
                if entity.risk_score >= 0.8:
                    entity.risk_level = RiskLevel.CRITICAL
                elif entity.risk_score >= 0.6:
                    entity.risk_level = RiskLevel.HIGH
                elif entity.risk_score >= 0.3:
                    entity.risk_level = RiskLevel.MEDIUM
                else:
                    entity.risk_level = RiskLevel.LOW

                # Update node in graph
                self.graph.nodes[entity_id]["risk_score"] = entity.risk_score

    def find_connected_entities(
        self, entity_id: str, max_depth: int = 3
    ) -> Set[str]:
        """Find all entities connected to a given entity within max_depth"""
        if entity_id not in self.graph:
            return set()

        connected = set()
        # Use BFS to find connected nodes
        visited = {entity_id}
        queue = [(entity_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            # Add neighbors (both directions)
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    connected.add(neighbor)
                    queue.append((neighbor, depth + 1))

            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    connected.add(predecessor)
                    queue.append((predecessor, depth + 1))

        return connected

    def detect_structuring_pattern(
        self, entity_id: str, time_window_days: int = 7, threshold: float = 10000.0
    ) -> Optional[Pattern]:
        """
        Detect structuring: multiple transactions just below reporting threshold
        """
        if entity_id not in self.graph:
            return None

        # Get all transactions involving this entity
        entity_transactions = []
        for trans_id, trans in self.transactions.items():
            if trans.sender_id == entity_id or trans.receiver_id == entity_id:
                entity_transactions.append(trans)

        # Group by time windows
        now = datetime.now()
        recent_trans = [
            t
            for t in entity_transactions
            if (now - t.timestamp).days <= time_window_days
        ]

        # Check for structuring pattern
        small_transactions = [
            t for t in recent_trans if 9000 <= t.amount < threshold
        ]

        if len(small_transactions) >= 3:
            total_amount = sum(t.amount for t in small_transactions)
            confidence = min(1.0, len(small_transactions) / 10.0)

            return Pattern(
                pattern_id=f"structuring_{entity_id}_{now.timestamp()}",
                pattern_type="structuring",
                entities_involved=[entity_id],
                transactions_involved=[t.transaction_id for t in small_transactions],
                sars_involved=[],
                confidence_score=confidence,
                risk_level=RiskLevel.HIGH if confidence > 0.7 else RiskLevel.MEDIUM,
                description=(
                    f"Detected {len(small_transactions)} transactions "
                    f"totaling ${total_amount: .2f} in {time_window_days} days, "
                    "potentially to avoid reporting thresholds"
                ),
            )
        return None

    def detect_circular_transactions(self, min_cycle_length: int = 3) -> List[Pattern]:
        """Detect circular transaction patterns (money laundering indicator)"""
        patterns = []

        # Find all simple cycles
        try:
            cycles = list(nx.simple_cycles(self.graph))
        except Exception:
            return patterns

        for cycle in cycles:
            if len(cycle) >= min_cycle_length:
                # Get transactions in the cycle
                cycle_transactions = []
                for i in range(len(cycle)):
                    src = cycle[i]
                    dst = cycle[(i + 1) % len(cycle)]
                    edge_data = self.graph.get_edge_data(src, dst)
                    if edge_data and "transaction_id" in edge_data:
                        cycle_transactions.append(edge_data["transaction_id"])

                if cycle_transactions:
                    confidence = min(1.0, len(cycle) / 10.0)
                    patterns.append(
                        Pattern(
                            pattern_id=(
                                f"circular_{hash(tuple(cycle))}_"
                                f"{datetime.now().timestamp()}"
                            ),
                            pattern_type="circular_transactions",
                            entities_involved=cycle,
                            transactions_involved=cycle_transactions,
                            sars_involved=[],
                            confidence_score=confidence,
                            risk_level=(
                                RiskLevel.CRITICAL
                                if confidence > 0.8
                                else RiskLevel.HIGH
                            ),
                            description=(
                                "Detected circular transaction pattern "
                                f"involving {len(cycle)} entities"
                            ),
                        )
                    )

        return patterns

    def detect_rapid_movement(
        self, entity_id: str, time_window_hours: int = 24
    ) -> Optional[Pattern]:
        """Detect rapid movement of funds (layering indicator)"""
        if entity_id not in self.graph:
            return None

        # Get recent transactions
        now = datetime.now()
        recent_trans = []
        for trans_id, trans in self.transactions.items():
            if trans.sender_id == entity_id or trans.receiver_id == entity_id:
                time_diff = now - trans.timestamp
                if time_diff.total_seconds() / 3600 <= time_window_hours:
                    recent_trans.append(trans)

        # Check for rapid succession of transactions
        if len(recent_trans) >= 5:
            total_amount = sum(t.amount for t in recent_trans)
            confidence = min(1.0, len(recent_trans) / 15.0)

            return Pattern(
                pattern_id=f"rapid_movement_{entity_id}_{now.timestamp()}",
                pattern_type="rapid_movement",
                entities_involved=[entity_id],
                transactions_involved=[t.transaction_id for t in recent_trans],
                sars_involved=[],
                confidence_score=confidence,
                risk_level=RiskLevel.HIGH if confidence > 0.6 else RiskLevel.MEDIUM,
                description=(
                    f"Detected {len(recent_trans)} transactions "
                    f"totaling ${total_amount: .2f} "
                    f"in {time_window_hours} hours"
                ),
            )
        return None

    def find_related_sars(self, entity_id: str) -> List[SAR]:
        """Find all SARs related to an entity or its connected entities"""
        connected = self.find_connected_entities(entity_id, max_depth=2)
        connected.add(entity_id)

        related_sars = []
        for sar_id, sar in self.sars.items():
            if any(e in connected for e in sar.entities_involved):
                related_sars.append(sar)

        return related_sars

    def compute_entity_risk_score(self, entity_id: str) -> float:
        """Compute comprehensive risk score for an entity"""
        if entity_id not in self.entities:
            return 0.0

        entity = self.entities[entity_id]
        risk_score = entity.risk_score

        # Factor in connected high-risk entities
        connected = self.find_connected_entities(entity_id, max_depth=2)
        high_risk_connections = sum(
            1
            for e_id in connected
            if e_id in self.entities
            and self.entities[e_id].risk_score > 0.5
        )
        risk_score += min(0.3, high_risk_connections * 0.05)

        # Factor in related SARs
        related_sars = self.find_related_sars(entity_id)
        risk_score += min(0.3, len(related_sars) * 0.1)

        return min(1.0, risk_score)

    def get_entity_graph_data(self, entity_id: str, depth: int = 2) -> Dict:
        """Get graph data for visualization"""
        if entity_id not in self.graph:
            return {"nodes": [], "edges": []}

        # Get connected entities
        connected = self.find_connected_entities(entity_id, max_depth=depth)
        connected.add(entity_id)

        # Build nodes
        nodes = []
        for node_id in connected:
            node_data = self.graph.nodes.get(node_id, {})
            entity_data = self.entities.get(node_id)
            nodes.append(
                {
                    "id": node_id,
                    "name": entity_data.name if entity_data else node_id,
                    "type": node_data.get("entity_type", "unknown"),
                    "risk_score": node_data.get("risk_score", 0.0),
                }
            )

        # Build edges
        edges = []
        for src in connected:
            for dst in connected:
                if self.graph.has_edge(src, dst):
                    edge_data = self.graph.get_edge_data(src, dst)
                    edges.append(
                        {
                            "source": src,
                            "target": dst,
                            "amount": edge_data.get("amount", 0.0),
                            "transaction_id": edge_data.get("transaction_id"),
                        }
                    )

        return {"nodes": nodes, "edges": edges}
