"""Preconfigured regular-expression scanning for email subject and body text."""

from dataclasses import dataclass
import re
from typing import Literal


TextSource = Literal["subject", "body"]


@dataclass(frozen=True)
class RegexRule:
    rule_id: str
    name: str
    category: str
    pattern: re.Pattern[str]
    explanation: str


@dataclass(frozen=True)
class RegexMatch:
    rule_id: str
    name: str
    category: str
    source: TextSource
    matched_text: str
    start_index: int
    end_index: int
    explanation: str


@dataclass(frozen=True)
class RegexScanResult:
    matches: list[RegexMatch]

    @property
    def matched(self) -> bool:
        return bool(self.matches)


# These expressions are application configuration, never supplied by users.
REGEX_RULES = (
    RegexRule(
        rule_id="RULE-URL",
        name="HTTP/HTTPS URL Recognition",
        category="url",
        pattern=re.compile(
            r"https?://[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?",
            re.IGNORECASE,
        ),
        explanation=(
            "Links are recorded for review because both legitimate and deceptive "
            "emails can contain them; a URL alone is not proof of phishing."
        ),
    ),
    RegexRule(
        rule_id="RULE-EMAIL",
        name="Email Address Recognition",
        category="email_address",
        pattern=re.compile(
            r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
            re.IGNORECASE,
        ),
        explanation=(
            "Email addresses are extracted as reviewable indicators, but ordinary "
            "messages also contain legitimate addresses."
        ),
    ),
    RegexRule(
        rule_id="RULE-PHRASE-WIN",
        name="Suspicious Phrase: WIN PRIZE NOW",
        category="urgency_phrase",
        pattern=re.compile(r"\bWIN\s+PRIZE\s+NOW\b", re.IGNORECASE),
        explanation="This prize-and-urgency wording is a configured social-engineering cue.",
    ),
    RegexRule(
        rule_id="RULE-PHRASE-CLAIM",
        name="Suspicious Phrase: CLAIM REWARD NOW",
        category="urgency_phrase",
        pattern=re.compile(r"\bCLAIM\s+REWARD\s+NOW\b", re.IGNORECASE),
        explanation="This immediate reward claim is a configured urgency cue.",
    ),
    RegexRule(
        rule_id="RULE-PHRASE-VERIFY",
        name="Suspicious Phrase: ACCOUNT VERIFY IMMEDIATELY",
        category="urgency_phrase",
        pattern=re.compile(
            r"\bACCOUNT\s+VERIFY\s+IMMEDIATELY\b", re.IGNORECASE
        ),
        explanation="This account-verification wording is a configured urgency cue.",
    ),
    RegexRule(
        rule_id="RULE-EXCLAMATION",
        name="Repeated Exclamation Marks",
        category="urgency_punctuation",
        pattern=re.compile(r"!{2,}"),
        explanation=(
            "Repeated exclamation marks can signal urgency, but are also common in "
            "benign informal messages."
        ),
    ),
)


class ConfiguredRegexEngine:
    """Scan text with only the fixed rules declared in ``REGEX_RULES``."""

    def __init__(self, rules: tuple[RegexRule, ...] = REGEX_RULES) -> None:
        self.rules = rules

    def scan(self, subject: str, body: str) -> RegexScanResult:
        matches: list[RegexMatch] = []
        # Offsets are relative to the source field, not concatenated email text.
        for source, text in (("subject", subject), ("body", body)):
            for rule in self.rules:
                for match in rule.pattern.finditer(text):
                    matches.append(
                        RegexMatch(
                            rule_id=rule.rule_id,
                            name=rule.name,
                            category=rule.category,
                            source=source,
                            matched_text=match.group(0),
                            start_index=match.start(),
                            end_index=match.end(),
                            explanation=rule.explanation,
                        )
                    )
        return RegexScanResult(matches=matches)


configured_regex_engine = ConfiguredRegexEngine()
