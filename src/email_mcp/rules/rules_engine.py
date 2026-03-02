from __future__ import annotations

import re
from typing import Iterable

from ..db.models import Rule
from ..normalize import NormalizedMessage
from .rules_models import RuleSpec, RuleField


def apply_rules(message: NormalizedMessage, rules: Iterable[RuleSpec]) -> list[str]:
    labels: list[str] = []
    for rule in rules:
        if not rule.enabled:
            continue
        field_value = getattr(message, rule.field.value, "")
        if not field_value:
            continue
        if re.search(rule.pattern, field_value, flags=re.IGNORECASE):
            labels.append(rule.label)
    return labels


def load_rules(rows: Iterable[Rule]) -> list[RuleSpec]:
    specs: list[RuleSpec] = []
    for row in rows:
        specs.append(
            RuleSpec(
                name=row.name,
                field=RuleField(row.field),
                pattern=row.pattern,
                label=row.label,
                enabled=row.enabled,
            )
        )
    return specs
