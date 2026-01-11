from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, re
from typing import Dict, List, Tuple

ALLOWED_VERBS = {
    "observed","recorded","stated","disclosed","referenced","shifted","coincided","remained"
}

FORBIDDEN_SUBSTRINGS_DEFAULT = [
    "diagnose","diagnosis","archetype","trauma","predict","prediction","verdict slant",
    "personality type","enneagram","mbti"
]

@dataclass(frozen=True)
class Ruleset:
    name: str
    version: str
    rules: Dict

    def sha256(self) -> str:
        blob = json.dumps(self.rules, sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

class JurisdictionRulesEngine:
    """
    Machine-enforced permission set. This is the chassis.
    """
    def __init__(self, ruleset: Ruleset):
        self.ruleset = ruleset

    def is_contact_allowed(self) -> bool:
        return False  # hard-coded: MAAT never permits contact

    def platform_allowed(self, platform: str) -> Tuple[bool, str]:
        p = self.ruleset.rules.get("platforms", {}).get(platform, None)
        if not p:
            return (False, "platform_not_configured")

        # Judge override: block platforms with notification risk
        if self.ruleset.rules.get("judge_overrides", {}).get("block_platforms_with_notifications", False):
            if p.get("notification_risk") in ("medium","high"):
                return (False, "blocked_by_judge_override_notification_risk")

        if not p.get("passive_view_public", False):
            return (False, "passive_view_disabled")

        if p.get("notification_risk") in ("medium","high") and not p.get("allow_if_notification_possible", False):
            return (False, "blocked_notification_possible")

        return (True, "ok")

class OutputLanguageFirewall:
    """
    Ensures MAAT outputs stay court-survivable: document conditions, avoid diagnosis/prediction.
    """
    def __init__(self, forbidden_substrings: List[str] | None = None):
        self.forbidden = forbidden_substrings or FORBIDDEN_SUBSTRINGS_DEFAULT

    def validate(self, text: str) -> List[str]:
        issues = []
        lower = text.lower()
        for s in self.forbidden:
            if s in lower:
                issues.append(f"forbidden_term:{s}")
        # crude causation flagging
        if re.search(r"\bcaused\b|\bintended\b|\bmanipulated\b", lower):
            issues.append("forbidden_causation_language")
        return issues
