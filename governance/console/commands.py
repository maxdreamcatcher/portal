"""
Governance Commands v1
Defines built-in governance commands.
"""

def cmd_rules(console, args):
    return console.lawbook.evaluate_rules(args or {})

def cmd_invariants(console, args):
    return console.lawbook.check_invariants(args or {})

def cmd_escalate(console, args):
    from umbrella.lawbook.lawbook import LawViolation
    violation = LawViolation(
        rule_name=args.get("rule", "unknown"),
        context=args,
        severity=args.get("severity", "low")
    )
    return console.lawbook.escalate(violation)

def cmd_describe(console, args):
    return console.lawbook.describe()
