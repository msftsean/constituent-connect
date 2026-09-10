from __future__ import annotations

import re

from ..models import ConstituentMessage, NormalizedInquiry, TraceEvent, new_id
from ..security import (
    contains_discriminatory_instruction,
    contains_prompt_injection,
    neutralize_untrusted_instructions,
    redact_pii,
)
from ..retention import RetentionPolicy


class SafetyPrivacyAgent:
    authoritative = True
    uses_generation = False
    EMERGENCY_TERMS = re.compile(
        r"\b(?:smoke|fire|trapped|shooting|gun|immediate danger|"
        r"cannot breathe|not breathing|overdose|medical emergency|"
        r"suicide|kill myself|active violence|bleeding badly)\b",
        re.IGNORECASE,
    )
    HISTORICAL_TERMS = re.compile(
        r"\b(?:last year|years ago|historically|old report|past incident)\b",
        re.IGNORECASE,
    )

    def assess(
        self,
        message: ConstituentMessage,
        intake_trace: TraceEvent,
        retention_policy: RetentionPolicy | None = None,
    ) -> NormalizedInquiry:
        original = message.raw_content
        policy = retention_policy or RetentionPolicy()
        redaction = redact_pii(original, marker=policy.redaction_marker)
        injection = contains_prompt_injection(original)
        discriminatory = contains_discriminatory_instruction(original)
        neutralized = neutralize_untrusted_instructions(redaction.text)
        emergency = bool(self.EMERGENCY_TERMS.search(original)) and not bool(
            self.HISTORICAL_TERMS.search(original)
        )
        language = self._detect_language(original, message.language)
        summary = self._summarize(neutralized)
        guidance = None
        urgency = "routine"
        if emergency:
            urgency = "emergency"
            guidance = (
                "If anyone is in immediate danger, call 911 now. "
                "This application cannot dispatch emergency services. "
                "A human contact-center escalation is required."
            )

        trace = [
            intake_trace,
            TraceEvent(
                stage="safety_privacy",
                outcome="emergency_exit" if emergency else "routine_allowed",
                details={
                    "emergency_signal": emergency,
                    "pii_categories": [item.category for item in redaction.findings],
                    "prompt_injection_detected": injection,
                    "discriminatory_instruction_detected": discriminatory,
                },
            ),
        ]
        return NormalizedInquiry(
            inquiry_id=new_id("inq"),
            message_id=message.message_id,
            summary=summary,
            redacted_content=neutralized,
            detected_language=language,
            intent_candidates=[],
            urgency=urgency,
            emergency_signal=emergency,
            pii_findings=redaction.findings,
            injection_detected=injection,
            discriminatory_instruction_detected=discriminatory,
            emergency_guidance=guidance,
            transformation_history=trace,
        )

    @staticmethod
    def _detect_language(text: str, declared: str) -> str:
        if declared and declared != "und":
            return declared
        spanish_markers = re.findall(
            r"\b(?:necesito|licencia|impuesto|ayuda|solicitud|permiso|gracias)\b",
            text,
            re.IGNORECASE,
        )
        return "es" if len(spanish_markers) >= 2 else "en"

    @staticmethod
    def _summarize(text: str) -> str:
        safe = re.sub(r"\[[^\]]*UNTRUSTED INSTRUCTION\]", "", text)
        safe = re.sub(r"\s+", " ", safe).strip()
        if not safe:
            return "No safe service request was identified."
        return safe[:277] + "..." if len(safe) > 280 else safe
