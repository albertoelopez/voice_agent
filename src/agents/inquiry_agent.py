"""
Inquiry Voice Agent - Handles customer inquiries via voice.

This is the main voice agent implementation using LiveKit Agents.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
)
from livekit.plugins import groq, silero, cartesia

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("inquiry-agent")
logger.setLevel(logging.DEBUG)


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

Start by greeting the user warmly and asking how you can help them today.
"""


def prewarm(proc: JobProcess):
    """Prewarm the agent process for faster cold starts."""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("Agent prewarmed and ready")


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the voice agent."""
    logger.info(f"========== NEW SESSION ==========")
    logger.info(f"Room: {ctx.room.name}")
    logger.info(f"Job ID: {ctx.job.id if ctx.job else 'N/A'}")

    # Connect to the room
    logger.info("Connecting to room...")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("Connected to room successfully")

    # Log participants
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Remote participants: {len(participants)}")
    for p in participants:
        logger.info(f"  - Participant: {p.identity}")

    # Get prewarmed VAD or load new one
    logger.info("Loading VAD...")
    vad = ctx.proc.userdata.get("vad") or silero.VAD.load()
    logger.info("VAD loaded")

    # Create components with logging
    logger.info("Creating STT (Groq Whisper)...")
    stt = groq.STT(model="whisper-large-v3-turbo")
    logger.info("STT created")

    logger.info("Creating LLM (Groq Llama)...")
    llm = groq.LLM(model="llama-3.3-70b-versatile")
    logger.info("LLM created")

    logger.info("Creating TTS (Cartesia)...")
    tts = cartesia.TTS()
    logger.info("TTS created")

    # Create the agent with instructions and components
    logger.info("Creating Agent...")
    agent = Agent(
        instructions=SYSTEM_PROMPT,
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
    )
    logger.info("Agent created")

    # Create and start the session
    logger.info("Starting AgentSession...")
    session = AgentSession()
    await session.start(agent, room=ctx.room)
    logger.info("========== READY ==========")
    logger.info("Voice assistant is now listening for speech...")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
