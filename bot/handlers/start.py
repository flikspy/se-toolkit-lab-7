"""Handler for /start command."""


def handle_start() -> str:
    """Handle the /start command.
    
    Returns:
        Welcome message for the user.
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check your scores, view available labs, and monitor your progress.\n\n"
        "Send /help to see all available commands."
    )
