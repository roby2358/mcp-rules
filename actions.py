"""
Example actions module for MCP Rules Engine

This module demonstrates how to define actions that can be executed
when rules match. Actions are defined as class methods and referenced
by their class.method specification.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationActions:
    """Example notification actions"""
    
    def send_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        logger.info(f"Sending email notification with data: {data}")
        return {
            "action": "send_email",
            "recipient": data.get("email", "unknown@example.com"),
            "subject": f"Rule triggered for {data.get('user', 'unknown user')}",
            "status": "sent"
        }
    
    def send_sms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification"""
        logger.info(f"Sending SMS notification with data: {data}")
        return {
            "action": "send_sms",
            "phone": data.get("phone", "+1234567890"),
            "message": f"Alert: Rule triggered for {data.get('user', 'unknown user')}",
            "status": "sent"
        }
    
    def log_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log event to system"""
        logger.info(f"Logging event with data: {data}")
        return {
            "action": "log_event",
            "event_type": "rule_triggered",
            "data": data,
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "logged"
        }


class SecurityActions:
    """Example security actions"""
    
    def block_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Block user account"""
        user_id = data.get("user_id", "unknown")
        logger.info(f"Blocking user: {user_id}")
        return {
            "action": "block_user",
            "user_id": user_id,
            "reason": "Rule violation detected",
            "status": "blocked"
        }
    
    def require_mfa(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Require multi-factor authentication"""
        user_id = data.get("user_id", "unknown")
        logger.info(f"Requiring MFA for user: {user_id}")
        return {
            "action": "require_mfa",
            "user_id": user_id,
            "mfa_method": "sms",
            "status": "required"
        }
    
    def create_incident(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create security incident"""
        logger.info(f"Creating security incident with data: {data}")
        return {
            "action": "create_incident",
            "incident_id": "INC-001",
            "severity": "high",
            "description": f"Security rule triggered for {data.get('user', 'unknown user')}",
            "status": "created"
        }


class BusinessActions:
    """Example business actions"""
    
    def apply_discount(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply discount to order"""
        order_id = data.get("order_id", "unknown")
        discount_percent = data.get("discount_percent", 10)
        logger.info(f"Applying {discount_percent}% discount to order: {order_id}")
        return {
            "action": "apply_discount",
            "order_id": order_id,
            "discount_percent": discount_percent,
            "status": "applied"
        }
    
    def escalate_support(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate support ticket"""
        ticket_id = data.get("ticket_id", "unknown")
        logger.info(f"Escalating support ticket: {ticket_id}")
        return {
            "action": "escalate_support",
            "ticket_id": ticket_id,
            "escalation_level": "manager",
            "status": "escalated"
        }
    
    def update_inventory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update inventory levels"""
        product_id = data.get("product_id", "unknown")
        quantity = data.get("quantity", 0)
        logger.info(f"Updating inventory for product {product_id}: {quantity}")
        return {
            "action": "update_inventory",
            "product_id": product_id,
            "quantity": quantity,
            "status": "updated"
        } 