"""
Umbrella Lawbook Escalation Paths v1
Defines escalation handlers for rule violations.
"""

def handle_low_severity(violation):
    return {
        "action": "log",
        "violation": violation.describe(),
        "status": "logged"
    }


def handle_medium_severity(violation):
    return {
        "action": "audit",
        "violation": violation.describe(),
        "status": "audit_triggered"
    }


def handle_high_severity(violation):
    return {
        "action": "halt",
        "violation": violation.describe(),
        "status": "system_halt_triggered"
    }
