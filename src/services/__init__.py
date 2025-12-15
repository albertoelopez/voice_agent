"""Service integrations for voice agent providers."""

from .fallback import FallbackLLM, FallbackSTT

__all__ = ["FallbackLLM", "FallbackSTT"]
