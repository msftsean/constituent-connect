from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .models import PiiFinding


PII_PATTERNS = {
    "social_security_number": re.compile(
        r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
    ),
    "email_address": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE
    ),
    "phone_number": re.compile(
        r"(?<!\d)(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}(?!\d)"
    ),
    "street_address": re.compile(
        r"\b\d{1,6}\s+(?:[A-Z0-9.'-]+\s+){1,6}"
        r"(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|"
        r"court|ct|place|pl|way|circle|cir|terrace|ter)\b(?:\s*(?:apt|unit|suite|#)\s*\w+)?",
        re.IGNORECASE,
    ),
    "date_of_birth": re.compile(
        r"\b(?:dob|date of birth|born)\s*(?:is|:|=)?\s*"
        r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Z][a-z]+\s+\d{1,2},\s+\d{4})\b",
        re.IGNORECASE,
    ),
    "driver_or_professional_license": re.compile(
        r"\b(?:driver'?s?|professional|occupational)?\s*(?:license|licence|dl)\s*"
        r"(?:number|#|id)?\s*(?:is|:|=)?\s*[A-Z]{1,4}[-\s]?\d{5,12}\b",
        re.IGNORECASE,
    ),
    "benefit_tax_case_account_identifier": re.compile(
        r"\b(?:benefit|tax|case|account|claim|client)\s*(?:number|#|id)?\s*"
        r"(?:is|:|=)?\s*[A-Z]{0,4}[-\s]?\d{6,16}\b",
        re.IGNORECASE,
    ),
    "payment_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "bank_information": re.compile(
        r"\b(?:routing|bank account|account)\s*(?:number|#)?\s*(?:is|:|=)?\s*\d{6,17}\b",
        re.IGNORECASE,
    ),
    "password": re.compile(
        r"\b(?:password|passcode|pin)\s*(?:is|:|=)\s*\S+", re.IGNORECASE
    ),
    "token_or_secret": re.compile(
        r"\b(?:token|api key|secret|credential|access key)\s*(?:is|:|=)\s*[A-Za-z0-9._~+/=-]{8,}\b",
        re.IGNORECASE,
    ),
    "one_time_code": re.compile(
        r"\b(?:one[-\s]?time code|otp|verification code|mfa code)\s*(?:is|:|=)?\s*\d{4,10}\b",
        re.IGNORECASE,
    ),
}

INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bignore (?:all |your )?(?:previous |prior )?(?:rules|instructions)\b",
        r"\b(system prompt|system instructions|hidden instructions)\b",
        r"\bdeveloper message\b",
        r"\boverride (?:the )?(?:policy|route|safety)\b",
        r"\broute .* executive queue\b",
        r"\bdo not follow\b.*\bpolicy\b",
    )
]

DISCRIMINATORY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:slower|faster|lower priority|deny)\s+queue\b.*\b(?:neighborhood|race|religion|sex|language)\b",
        r"\b(?:neighborhood|race|religion|sex|language)\b.*\b(?:slower|faster|lower priority|deny)\s+queue\b",
        r"\broute\b.*\bbased on\b.*\b(?:race|religion|sex|neighborhood|disability)\b",
    )
]


@dataclass(slots=True)
class RedactionResult:
    text: str
    findings: list[PiiFinding]
    sensitive_data_request: bool


def redact_pii(text: str, marker: str = "[REDACTED]") -> RedactionResult:
    redacted = text
    findings: list[PiiFinding] = []
    for category, pattern in PII_PATTERNS.items():
        replacement = (
            f"{marker} {category.upper()}" if marker.endswith("]") else marker
        )
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            findings.append(PiiFinding(category=category, count=count))

    sensitive_request = bool(
        re.search(
            r"\b(?:repeat|show|include|disclose).{0,35}"
            r"(?:social security|ssn|password|credential|passcode)",
            text,
            re.IGNORECASE,
        )
    )
    if sensitive_request and not findings:
        findings.append(PiiFinding(category="sensitive_data_request", count=1))
    return RedactionResult(redacted, findings, sensitive_request)


def contains_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def contains_discriminatory_instruction(text: str) -> bool:
    return any(pattern.search(text) for pattern in DISCRIMINATORY_PATTERNS)


def neutralize_untrusted_instructions(text: str) -> str:
    cleaned = text
    for pattern in INJECTION_PATTERNS:
        cleaned = pattern.sub("[IGNORED UNTRUSTED INSTRUCTION]", cleaned)
    return cleaned


def redact_for_trace(value: Any, *, include_raw: bool = False) -> Any:
    """Remove raw constituent content from structured trace payloads."""
    if isinstance(value, dict):
        return {
            key: (
                value[key]
                if include_raw and key in {"raw_content", "content"}
                else redact_for_trace(value[key], include_raw=include_raw)
            )
            for key in value
            if include_raw or key not in {"raw_content", "content"}
        }
    if isinstance(value, list):
        return [redact_for_trace(item, include_raw=include_raw) for item in value]
    if isinstance(value, str) and not include_raw:
        redacted = value
        for pattern in PII_PATTERNS.values():
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted
    return value
