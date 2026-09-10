from __future__ import annotations

import re

from ..models import ConstituentMessage, TraceEvent, new_id, now_iso


class ChannelIntakeAgent:
    SUPPORTED_CHANNELS = {"web", "chat", "email", "voice"}

    def normalize(
        self, content: str, channel: str, language: str | None = None
    ) -> ConstituentMessage:
        normalized_channel = channel.lower().strip()
        if normalized_channel not in self.SUPPORTED_CHANNELS:
            raise ValueError(
                f"Unsupported channel '{channel}'. Use web, chat, email, or voice."
            )
        cleaned = re.sub(r"\s+", " ", content).strip()
        if not cleaned:
            raise ValueError("Inquiry content is required.")
        return ConstituentMessage(
            message_id=new_id("msg"),
            channel=normalized_channel,
            received_at=now_iso(),
            language=language or "und",
            raw_content=cleaned,
        )

    @staticmethod
    def trace(message: ConstituentMessage) -> TraceEvent:
        return TraceEvent(
            stage="channel_intake",
            outcome="normalized",
            details={"channel": message.channel, "content_length": len(message.raw_content)},
        )
