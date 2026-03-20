"""Handler for /help command."""


def handle_help() -> str:
    """Handle the /help command.
    
    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 Available Commands:\n\n"
        "/start — Start the bot and see welcome message\n"
        "/help — Show this help message\n"
        "/health — Check if the backend is running\n"
        "/labs — List all available labs\n"
        "/scores <lab_id> — Get your scores for a specific lab\n\n"
        "You can also ask questions in natural language, e.g.:\n"
        "• What labs are available?\n"
        "• Show my scores for lab-04"
    )
