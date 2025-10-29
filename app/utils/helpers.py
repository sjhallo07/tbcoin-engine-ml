"""Utility functions"""
import hashlib
import time
from typing import Any, Dict
import json


def generate_hash(data: str) -> str:
    """Generate SHA256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def get_timestamp() -> int:
    """Get current timestamp"""
    return int(time.time())


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format"""
    return bool(user_id and len(user_id) >= 3)


def format_currency(amount: float, decimals: int = 2) -> str:
    """Format amount as currency"""
    return f"{amount:,.{decimals}f}"


def serialize_json(data: Any) -> str:
    """Serialize data to JSON string"""
    return json.dumps(data, default=str)


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0
    return (value / total) * 100
