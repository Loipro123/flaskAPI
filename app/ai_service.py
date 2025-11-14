"""
AI service for semantic analysis and pattern matching
"""
from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime

from app.models import SAR, Transaction, RiskLevel


class AIAnalysisService:
    """
    Service for AI-powered analysis of SARs and transactions
    Uses semantic similarity for pattern matching
    """

    def __init__(self):
        self.sar_embeddings: Dict[str, np.ndarray] = {}
        self.transaction_embeddings: Dict[str, np.ndarray] = {}
        # Simple keyword-based embedding for prototype
        # (would use sentence-transformers in production)
        self.keywords = {
            "structuring": [
                "multiple",
                "transactions",
                "below",
                "threshold",
                "avoid",
            ],
            "money_laundering": ["layering", "placement", "integration", "wash"],
            "fraud": ["false", "fake", "deception", "misrepresentation"],
            "terrorist_financing": ["terrorism", "extremist", "funding"],
            "unusual_transaction": [
                "unusual",
                "abnormal",
                "irregular",
                "suspicious",
            ],
        }

    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """
        Create a simple embedding based on keyword presence
        In production, this would use sentence-transformers
        """
        text_lower = text.lower()
        embedding = np.zeros(len(self.keywords))

        for idx, (pattern_type, keywords) in enumerate(self.keywords.items()):
            # Count keyword occurrences
            count = sum(1 for keyword in keywords if keyword in text_lower)
            embedding[idx] = count / len(keywords)  # Normalize

        return embedding

    def analyze_sar_narrative(self, sar: SAR) -> Dict:
        """Analyze SAR narrative for patterns and risk indicators"""
        embedding = self._create_simple_embedding(sar.narrative)
        self.sar_embeddings[sar.sar_id] = embedding

        # Determine primary activity type based on embedding
        max_idx = np.argmax(embedding)
        pattern_types = list(self.keywords.keys())

        analysis = {
            "sar_id": sar.sar_id,
            "primary_pattern": (
                pattern_types[max_idx] if embedding[max_idx] > 0 else "unknown"
            ),
            "confidence": float(embedding[max_idx]),
            "secondary_patterns": [
                pattern_types[i]
                for i, score in enumerate(embedding)
                if 0 < score < embedding[max_idx]
            ],
            "risk_indicators": self._extract_risk_indicators(sar.narrative),
        }

        return analysis

    def _extract_risk_indicators(self, text: str) -> List[str]:
        """Extract risk indicators from text"""
        indicators = []
        text_lower = text.lower()

        risk_keywords = {
            "high_value": [
                "large amount",
                "significant sum",
                "million",
                "thousands",
            ],
            "cross_border": [
                "international",
                "foreign",
                "overseas",
                "cross-border",
            ],
            "shell_company": ["shell company", "front", "nominee"],
            "cash_intensive": ["cash", "currency", "physical money"],
            "rapid_movement": ["rapid", "quick", "immediate", "frequent"],
            "anonymous": ["anonymous", "unknown", "unidentified"],
        }

        for indicator, keywords in risk_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                indicators.append(indicator)

        return indicators

    def find_similar_sars(
        self, sar: SAR, all_sars: List[SAR], threshold: float = 0.5
    ) -> List[Tuple[SAR, float]]:
        """Find SARs with similar patterns using semantic similarity"""
        if sar.sar_id not in self.sar_embeddings:
            self.analyze_sar_narrative(sar)

        query_embedding = self.sar_embeddings[sar.sar_id]
        similar_sars = []

        for other_sar in all_sars:
            if other_sar.sar_id == sar.sar_id:
                continue

            if other_sar.sar_id not in self.sar_embeddings:
                self.analyze_sar_narrative(other_sar)

            other_embedding = self.sar_embeddings[other_sar.sar_id]

            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, other_embedding)

            if similarity >= threshold:
                similar_sars.append((other_sar, float(similarity)))

        # Sort by similarity descending
        similar_sars.sort(key=lambda x: x[1], reverse=True)
        return similar_sars

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def analyze_transaction_pattern(self, transactions: List[Transaction]) -> Dict:
        """Analyze a sequence of transactions for patterns"""
        if not transactions:
            return {"pattern_detected": False}

        # Sort by timestamp
        sorted_trans = sorted(transactions, key=lambda t: t.timestamp)

        analysis = {
            "transaction_count": len(transactions),
            "total_amount": sum(t.amount for t in transactions),
            "avg_amount": np.mean([t.amount for t in transactions]),
            "std_amount": np.std([t.amount for t in transactions]),
            "time_span_hours": (
                (
                    sorted_trans[-1].timestamp - sorted_trans[0].timestamp
                ).total_seconds()
                / 3600
            )
            if len(sorted_trans) > 1
            else 0,
            "pattern_detected": False,
            "patterns": [],
        }

        # Detect patterns
        patterns = []

        # Pattern 1: Uniform amounts (structuring indicator)
        if analysis["std_amount"] < analysis["avg_amount"] * 0.1:
            patterns.append("uniform_amounts")

        # Pattern 2: Rapid succession
        if analysis["time_span_hours"] < 24 and len(transactions) > 5:
            patterns.append("rapid_succession")

        # Pattern 3: Round numbers (suspicious indicator)
        round_numbers = sum(1 for t in transactions if t.amount % 1000 == 0)
        if round_numbers / len(transactions) > 0.7:
            patterns.append("round_numbers")

        analysis["patterns"] = patterns
        analysis["pattern_detected"] = len(patterns) > 0

        return analysis

    def compute_risk_score(
        self,
        entity_connections: int,
        sar_count: int,
        transaction_volume: float,
        pattern_count: int,
    ) -> Tuple[float, RiskLevel]:
        """Compute overall risk score based on multiple factors"""
        # Weighted scoring
        score = 0.0

        # Factor 1: SAR count (0-0.3)
        score += min(0.3, sar_count * 0.1)

        # Factor 2: Entity connections (0-0.2)
        score += min(0.2, entity_connections * 0.02)

        # Factor 3: Transaction volume (0-0.3)
        if transaction_volume > 1000000:
            score += 0.3
        elif transaction_volume > 100000:
            score += 0.2
        elif transaction_volume > 10000:
            score += 0.1

        # Factor 4: Pattern count (0-0.2)
        score += min(0.2, pattern_count * 0.05)

        # Determine risk level
        if score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return min(1.0, score), risk_level

    def generate_risk_report(self, entity_id: str, analysis_data: Dict) -> Dict:
        """Generate a comprehensive risk report"""
        return {
            "entity_id": entity_id,
            "generated_at": datetime.now().isoformat(),
            "risk_score": analysis_data.get("risk_score", 0.0),
            "risk_level": analysis_data.get("risk_level", "low"),
            "findings": analysis_data.get("findings", []),
            "related_sars": analysis_data.get("related_sars", []),
            "detected_patterns": analysis_data.get("patterns", []),
            "recommendations": self._generate_recommendations(analysis_data),
        }

    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        risk_score = analysis_data.get("risk_score", 0.0)

        if risk_score >= 0.8:
            recommendations.append(
                "CRITICAL: Immediate investigation required. "
                "Consider filing SAR if not already done."
            )
            recommendations.append("Enhanced due diligence recommended")
            recommendations.append("Review all recent transactions")

        elif risk_score >= 0.6:
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Review transaction patterns")

        elif risk_score >= 0.3:
            recommendations.append("Continue standard monitoring")
            recommendations.append("Document findings for future reference")

        patterns = analysis_data.get("patterns", [])
        if "structuring" in str(patterns):
            recommendations.append(
                "Investigate for potential structuring activity"
            )
        if "circular_transactions" in str(patterns):
            recommendations.append(
                "Analyze circular transaction pattern for "
                "money laundering indicators"
            )
        if "rapid_movement" in str(patterns):
            recommendations.append(
                "Review rapid fund movement for layering activity"
            )

        return recommendations
