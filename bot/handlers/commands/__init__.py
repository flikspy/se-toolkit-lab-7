"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram — same function works from --test mode,
unit tests, or the Telegram bot.
"""

from .start import handle_start
from .help import handle_help
from .health import handle_health
from .labs import handle_labs
from .scores import handle_scores
from .intent import route_intent, get_welcome_keyboard, format_keyboard_hint

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "route_intent",
    "get_welcome_keyboard",
    "format_keyboard_hint",
]
