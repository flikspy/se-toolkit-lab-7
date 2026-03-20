#!/usr/bin/env python3
"""Telegram bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
"""

import argparse
import sys

from config import get_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into command and argument.
    
    Args:
        text: The command text (e.g., "/scores lab-04" or "/start").
        
    Returns:
        Tuple of (command, argument). Argument is None if not provided.
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


def handle_command(command: str, argument: str | None = None) -> str:
    """Route a command to the appropriate handler.
    
    Args:
        command: The command name (e.g., "/start", "/scores").
        argument: Optional argument for the command.
        
    Returns:
        The handler's response text.
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command == "/scores":
        return handle_scores(argument)
    else:
        return f"❓ Unknown command: {command}\nSend /help to see available commands."


def run_test_mode(command_text: str) -> None:
    """Run the bot in test mode (no Telegram connection).
    
    Calls the handler directly and prints the response to stdout.
    
    Args:
        command_text: The command to test (e.g., "/start" or "/scores lab-04").
    """
    command, argument = parse_command(command_text)
    response = handle_command(command, argument)
    print(response)


def run_telegram_bot() -> None:
    """Start the Telegram bot client.
    
    Connects to Telegram using the bot token from .env.bot.secret.
    """
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
    )
    
    config = get_config()
    
    async def handle_telegram_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle a Telegram command message."""
        command = f"/{update.message.text.split()[0][1:].lower()}"
        
        # Extract argument if present
        parts = update.message.text.split(maxsplit=1)
        argument = parts[1] if len(parts) > 1 else None
        
        response = handle_command(command, argument)
        await update.message.reply_text(response)
    
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle plain text messages (for Task 3 - LLM routing)."""
        # For now, just suggest using commands
        await update.message.reply_text(
            "🤔 I understand commands like /start, /help, /labs, /scores.\n\n"
            "In Task 3, I'll also understand natural language questions!"
        )
    
    # Create application
    application = Application.builder().token(config.bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", handle_telegram_command))
    application.add_handler(CommandHandler("help", handle_telegram_command))
    application.add_handler(CommandHandler("health", handle_telegram_command))
    application.add_handler(CommandHandler("labs", handle_telegram_command))
    application.add_handler(CommandHandler("scores", handle_telegram_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Start polling
    print("🤖 Bot is starting... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command without Telegram connection (e.g., '/start')",
    )
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode: call handler directly and print response
        run_test_mode(args.test)
        sys.exit(0)
    else:
        # Production mode: start Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
