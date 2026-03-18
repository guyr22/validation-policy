import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def send_to_elastic(schema_name: str, report: Dict[str, Any]) -> None:
    """Mock external service for observability logging."""
    logger.info(f"[ELASTIC_MOCK] Sending soft_launch report for {schema_name}: {report}")
