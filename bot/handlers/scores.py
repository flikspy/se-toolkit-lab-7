"""Handler for /scores command."""


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.
    
    Args:
        lab_id: The lab ID to get scores for (e.g., "lab-04").
        
    Returns:
        Student scores for the specified lab (placeholder for Task 1).
    """
    if lab_id is None:
        return "❌ Please specify a lab ID. Example: /scores lab-04"
    
    return (
        f"📊 Scores for {lab_id}:\n\n"
        f"Status: Placeholder (will fetch from API in Task 2)\n\n"
        f"Example response:\n"
        f"• Task 1: 10/10\n"
        f"• Task 2: 8/10\n"
        f"• Total: 18/20"
    )
