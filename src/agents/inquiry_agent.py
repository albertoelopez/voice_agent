"""
Inquiry Voice Agent - Handles customer inquiries via voice.

This is the main voice agent implementation using LiveKit Agents.
"""

import logging
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import groq, silero

from config.settings import settings

logger = logging.getLogger("inquiry-agent")
logger.setLevel(settings.log_level)


class InquiryAgent:
    """Voice agent for handling customer inquiries."""

    SYSTEM_PROMPT = """You are a helpful voice assistant that handles customer inquiries.

Your communication style:
- Be concise and clear - this is voice, not text
- Keep responses under 2-3 sentences when possible
- Ask clarifying questions if needed
- Be friendly and professional

Your capabilities:
- Answer general questions
- Help with product information
- Provide support guidance
- Escalate complex issues to human agents

Important:
- If you don't know something, say so honestly
- For sensitive topics (billing, personal data), recommend speaking with a human
- Always confirm understanding before taking actions
"""

    def __init__(self):
        self.vad = silero.VAD.load()
        self.stt = self._create_stt()
        self.llm = self._create_llm()
        self.tts = self._create_tts()

    def _create_stt(self):
        """Create STT service based on settings."""
        if settings.stt_provider == "groq":
            return groq.STT(model=settings.stt_model)
        # Add other providers here
        raise ValueError(f"Unknown STT provider: {settings.stt_provider}")

    def _create_llm(self):
        """Create LLM service with fallback support."""
        if settings.llm_provider == "groq":
            return groq.LLM(model=settings.llm_model)
        # Add other providers here
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

    def _create_tts(self):
        """Create TTS service based on settings."""
        # Import based on provider to avoid unnecessary dependencies
        if settings.tts_provider == "cartesia":
            from livekit.plugins import cartesia
            return cartesia.TTS(voice=settings.tts_voice)
        elif settings.tts_provider == "openai":
            from livekit.plugins import openai
            return openai.TTS(voice="alloy")
        raise ValueError(f"Unknown TTS provider: {settings.tts_provider}")

    def create_assistant(self) -> VoiceAssistant:
        """Create and configure the voice assistant."""
        initial_ctx = llm.ChatContext().append(
            role="system",
            text=self.SYSTEM_PROMPT,
        )

        return VoiceAssistant(
            vad=self.vad,
            stt=self.stt,
            llm=self.llm,
            tts=self.tts,
            chat_ctx=initial_ctx,
            allow_interruptions=settings.allow_interruptions,
            interrupt_speech_duration=settings.interrupt_speech_duration,
        )


def prewarm(proc: JobProcess):
    """Prewarm the agent process for faster cold starts."""
    proc.userdata["agent"] = InquiryAgent()
    logger.info("Agent prewarmed and ready")


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the voice agent."""
    logger.info(f"Connecting to room: {ctx.room.name}")

    # Get prewarmed agent or create new one
    agent_instance = ctx.proc.userdata.get("agent") or InquiryAgent()
    assistant = agent_instance.create_assistant()

    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Start the assistant
    assistant.start(ctx.room)

    # Greet the user
    await assistant.say(
        "Hello! I'm here to help with your inquiry. What can I assist you with today?",
        allow_interruptions=True,
    )

    logger.info("Voice assistant started and ready")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
