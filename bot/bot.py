#!/usr/bin/env python3
"""Telegram bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
    uv run bot.py --test "what labs are available"  # NL query test mode
"""

import argparse
import sys

from config import get_config
from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_intent,
    get_welcome_keyboard,
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


def handle_command(command: str, argument: str | None = None, config=None) -> str:
    """Route a command to the appropriate handler.

    Args:
        command: The command name (e.g., "/start", "/scores").
        argument: Optional argument for the command.
        config: Optional config object with API credentials.

    Returns:
        The handler's response text.
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        if config:
            return handle_health(config.lms_api_url, config.lms_api_key)
        return handle_health("http://localhost:42002", "my-secret-api-key")
    elif command == "/labs":
        if config:
            return handle_labs(config.lms_api_url, config.lms_api_key)
        return handle_labs("http://localhost:42002", "my-secret-api-key")
    elif command == "/scores":
        if config:
            return handle_scores(argument, config.lms_api_url, config.lms_api_key)
        return handle_scores(argument, "http://localhost:42002", "my-secret-api-key")
    else:
        return f"❓ Unknown command: {command}\nSend /help to see available commands."


def run_test_mode(command_text: str) -> None:
    """Run the bot in test mode (no Telegram connection).

    Calls the handler directly and prints the response to stdout.

    Args:
        command_text: The command to test (e.g., "/start" or "/scores lab-04").
    """
    # Try to load config, but use defaults if not available
    try:
        config = get_config()
    except ValueError:
        config = None
    
    # Check if this is a natural language query (doesn't start with /)
    text = command_text.strip()
    if not text.startswith("/"):
        # Natural language query - use intent routing
        if config:
            response = route_intent(
                text,
                config.lms_api_url,
                config.lms_api_key,
                config.llm_api_key,
                config.llm_api_base_url,
                config.llm_api_model,
            )
        else:
            response = "LLM routing requires configuration. Please set up .env.bot.secret"
        print(response)
        return
    
    # Command - use regular routing
    command, argument = parse_command(text)
    response = handle_command(command, argument, config)
    print(response)


def run_telegram_bot() -> None:
    """Start the Telegram bot client.
    
    Connects to Telegram using the bot token from .env.bot.secret.
    """
    from telegram import Update
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
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

        response = handle_command(command, argument, config)
        
        # Add inline keyboard for /start command
        if command == "/start":
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = get_welcome_keyboard()
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(label, callback_data=cb_data) for label, cb_data in row]
                for row in keyboard
            ])
            await update.message.reply_text(response, reply_markup=reply_markup)
        else:
            await update.message.reply_text(response)

    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle plain text messages with LLM intent routing."""
        message = update.message.text
        
        # Route through LLM
        response = route_intent(
            message,
            config.lms_api_url,
            config.lms_api_key,
            config.llm_api_key,
            config.llm_api_base_url,
            config.llm_api_model,
        )
        
        await update.message.reply_text(response)
    
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button callbacks."""
        query = update.callback_query
        await query.answer()
        
        # Execute the command associated with the button
        command_data = query.data
        if command_data.startswith("/"):
            # It's a command - execute it
            command, argument = parse_command(command_data)
            response = handle_command(command, argument, config)
            await query.edit_message_text(response)
    
    # Create application
    application = Application.builder().token(config.bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", handle_telegram_command))
    application.add_handler(CommandHandler("help", handle_telegram_command))
    application.add_handler(CommandHandler("health", handle_telegram_command))
    application.add_handler(CommandHandler("labs", handle_telegram_command))
    application.add_handler(CommandHandler("scores", handle_telegram_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
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
