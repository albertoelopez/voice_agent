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
    Agent,
    AgentSession,
    ChatContext,
    ChatMessage,
    ChatRole,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
)
from livekit.agents.voice import Agent as VoiceAgent
from livekit.plugins import groq, silero

logger = logging.getLogger("inquiry-agent")


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


def prewarm(proc: JobProcess):
    """Prewarm the agent process for faster cold starts."""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Agent prewarmed and ready")


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the voice agent."""
    logger.info(f"Connecting to room: {ctx.room.name}")

    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Get prewarmed VAD or load new one
    vad = ctx.proc.userdata.get("vad") or silero.VAD.load()

    # Create the voice agent
    agent = VoiceAgent(
        instructions=SYSTEM_PROMPT,
        vad=vad,
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(),  # Use Groq TTS or swap with another provider
    )

    # Start the agent session
    session = AgentSession(agent)
    await session.start(
        room=ctx.room,
        room_input_options=RoomInputOptions(),
        room_output_options=RoomOutputOptions(),
    )

    # Greet the user
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help them today."
    )

    logger.info("Voice assistant started and ready")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
