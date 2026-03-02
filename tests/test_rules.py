from email_mcp.normalize import NormalizedMessage
from email_mcp.rules.rules_engine import apply_rules
from email_mcp.rules.rules_models import RuleSpec, RuleField


def test_rules_apply():
    rules = [
        RuleSpec(name="bank", field=RuleField.subject, pattern="statement", label="finance"),
        RuleSpec(name="alerts", field=RuleField.from_addr, pattern="alerts@", label="alerts"),
    ]
    message = NormalizedMessage(
        subject="Monthly Statement",
        from_addr="alerts@example.com",
        to_addrs="me@example.com",
        date="",
        text="",
    )
    labels = apply_rules(message, rules)
    assert "finance" in labels
    assert "alerts" in labels


def test_rules_disabled():
    rules = [
        RuleSpec(name="disabled", field=RuleField.subject, pattern="hello", label="x", enabled=False),
    ]
    message = NormalizedMessage(
        subject="hello",
        from_addr="a@example.com",
        to_addrs="b@example.com",
        date="",
        text="",
    )
    labels = apply_rules(message, rules)
    assert labels == []
