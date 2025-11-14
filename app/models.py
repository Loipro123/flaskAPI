"""
Data models for Suspicious Activity Detection System
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class ActivityType(Enum):
    """Types of suspicious activities"""

    STRUCTURING = "structuring"
    MONEY_LAUNDERING = "money_laundering"
    FRAUD = "fraud"
    TERRORIST_FINANCING = "terrorist_financing"
    UNUSUAL_TRANSACTION = "unusual_transaction"
    MULTIPLE_ACCOUNTS = "multiple_accounts"
    HIGH_RISK_JURISDICTION = "high_risk_jurisdiction"


class RiskLevel(Enum):
    """Risk levels for entities and transactions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Entity:
    """Represents a person or organization involved in transactions"""

    entity_id: str
    name: str
    entity_type: str  # "person" or "organization"
    identifiers: Dict[str, str] = field(default_factory=dict)
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    metadata: Dict = field(default_factory=dict)


@dataclass
class Transaction:
    """Represents a financial transaction"""

    transaction_id: str
    timestamp: datetime
    amount: float
    currency: str
    sender_id: str
    receiver_id: str
    transaction_type: str
    description: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SAR:
    """Suspicious Activity Report"""

    sar_id: str
    filing_date: datetime
    activity_type: ActivityType
    entities_involved: List[str]
    transactions_involved: List[str]
    narrative: str
    risk_level: RiskLevel
    amount_involved: float
    time_period_start: datetime
    time_period_end: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class Relationship:
    """Represents a relationship between two entities"""

    source_id: str
    target_id: str
    relationship_type: str
    strength: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Pattern:
    """Represents a detected suspicious pattern"""

    pattern_id: str
    pattern_type: str
    entities_involved: List[str]
    transactions_involved: List[str]
    sars_involved: List[str]
    confidence_score: float
    risk_level: RiskLevel
    description: str
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
