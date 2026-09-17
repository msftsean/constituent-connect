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
        r"\b(?:heart attack|stroke|fire|smoke|burning|cannot breathe|can't breathe|"
        r"not breathing|breathing crisis|drowning|overdose|violence|violent|"
        r"domestic violence|shooting|active shooter|stabbed|assault|self[-\s]?harm|"
        r"suicide|kill myself|trapped|immediate danger|medical emergency|"
        r"bleeding badly|unconscious|choking|seizure|ataque al corazon|derrame cerebral|"
        r"incendio|humo|no puede respirar|sobredosis|violencia|peligro inmediato|"
        r"atrapad[oa]s?)\b",
        re.IGNORECASE,
    )
    CURRENT_MARKERS = re.compile(
        r"\b(?:now|right now|currently|ongoing|active|happening|there is|there's|"
        r"someone is|someone's|i am|i'm|my .* is|in my|inside my|at my|here|today|"
        r"just|help|ayuda|ahora|alguien|esta|estoy|en mi)\b",
        re.IGNORECASE,
    )
    NON_CURRENT_TERMS = re.compile(
        r"\b(?:last year|last month|yesterday|years ago|historically|old report|"
        r"past incident|resolved|was resolved|is out|put out|no longer|training|"
        r"drill|policy|report|historical|hypothetical|what if|if someone|"
        r"used to|previously|not currently|not now|false alarm|simulacro|historico)\b",
        re.IGNORECASE,
    )
    NEGATED_EMERGENCY = re.compile(
        r"\b(?:no|not|never|without|isn't|is not|wasn't|was not|no hay|sin)\b.{0,45}"
        r"\b(?:heart attack|stroke|fire|smoke|violence|overdose|danger|emergency|"
        r"suicide|self[-\s]?harm|trapped|breathing|incendio|humo|violencia)\b",
        re.IGNORECASE,
    )
    FALSE_POSITIVE_CONTEXT = re.compile(
        r"\b(?:gun license|fire inspection|fire code|fire department inspection|"
        r"violence prevention|emergency training|historical report|policy question|"
        r"smoke detector permit|fire permit)\b",
        re.IGNORECASE,
    )
    CRITICAL_NEGATION_PHRASES = re.compile(
        r"\b(?:not breathing|can't breathe|cannot breathe|no puede respirar)\b",
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
        emergency = self._has_current_emergency(original)
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

    @classmethod
    def _has_current_emergency(cls, text: str) -> bool:
        if cls.FALSE_POSITIVE_CONTEXT.search(text) and not cls.CURRENT_MARKERS.search(text):
            return False
        clauses = [
            clause.strip()
            for clause in re.split(r"[.;!?]\s+|\n+", text)
            if clause.strip()
        ] or [text]
        for clause in clauses:
            if not cls.EMERGENCY_TERMS.search(clause):
                continue
            if cls.CRITICAL_NEGATION_PHRASES.search(clause):
                return True
            if cls.NEGATED_EMERGENCY.search(clause):
                continue
            non_current = cls.NON_CURRENT_TERMS.search(clause)
            current = cls.CURRENT_MARKERS.search(clause)
            if current or not non_current:
                return True
        return False
