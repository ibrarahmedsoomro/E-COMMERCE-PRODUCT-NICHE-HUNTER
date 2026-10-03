"""
Prompt Injection Defense & Untrusted Input Sanitization Layer.
Rule: External content (reviews, supplier pages, competitor listings, social text) is DATA ONLY.
It can NEVER grant permissions, alter policy, or issue system commands.
"""

import re
from typing import Dict, Any, Tuple


class PromptDefenseFilter:
    """
    Sanitizes untrusted external text and wraps it in strong boundary markers
    to prevent prompt injection and system jailbreaks.
    """

    SUSPICIOUS_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
        re.compile(r"system\s*:\s*you\s+are\s+now", re.IGNORECASE),
        re.compile(r"override\s+(policy|gate|rules|constitution)", re.IGNORECASE),
        re.compile(r"reveal\s+(api\s*key|secret|credentials|password)", re.IGNORECASE),
        re.compile(r"publish\s+(immediately|now|without\s+gates)", re.IGNORECASE),
        re.compile(r"transfer\s+(funds|money|payout)", re.IGNORECASE)
    ]

    @classmethod
    def sanitize_external_text(cls, raw_text: str, source_label: str = "EXTERNAL_DATA") -> Tuple[str, bool]:
        """
        Scans and sanitizes untrusted external strings.
        Returns: (safe_fenced_content, was_injection_detected)
        """
        if not raw_text:
            return ("", False)

        was_injected = False
        cleaned = raw_text

        for pattern in cls.SUSPICIOUS_PATTERNS:
            if pattern.search(cleaned):
                was_injected = True
                cleaned = pattern.sub("[BLOCKED_INJECTION_ATTEMPT]", cleaned)

        # Strongly fence the data to prevent LLM execution bleed
        fenced_content = f"<{source_label}_UNTRUSTED_RAW_DATA>\n{cleaned.strip()}\n</{source_label}_UNTRUSTED_RAW_DATA>"
        return (fenced_content, was_injected)


# Global helper instance
prompt_defense = PromptDefenseFilter()
