"""Intent-based natural language routing with LLM."""

import sys

from services.lms_api import get_lms_client, get_tool_definitions
from services.llm_client import get_llm_client


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. Use the available tools to fetch the data you need
2. Analyze the results
3. Provide a clear, helpful answer based on the data

If the user's message is a greeting or doesn't require data, respond directly without using tools.
If you don't understand the query, ask for clarification or suggest what you can help with.

Available capabilities:
- List available labs and tasks
- Show pass rates and scores for specific labs
- Compare group performance
- Find top students
- Show submission timelines
- Check completion rates
- Refresh data from autochecker

Always be specific and include numbers from the data when answering."""


def route_intent(
    message: str,
    lms_api_url: str,
    lms_api_key: str,
    llm_api_key: str,
    llm_api_base_url: str,
    llm_api_model: str,
) -> str:
    """Route a natural language message using LLM.
    
    Args:
        message: User's natural language message.
        lms_api_url: LMS API base URL.
        lms_api_key: LMS API key.
        llm_api_key: LLM API key.
        llm_api_base_url: LLM API base URL.
        llm_api_model: LLM model name.
        
    Returns:
        Response to the user.
    """
    try:
        # Initialize LMS client
        lms_client = get_lms_client(lms_api_url, lms_api_key)
        
        # Initialize LLM client
        llm_client = get_llm_client(llm_api_key, llm_api_base_url, llm_api_model)
        
        # Get tool definitions
        tools = get_tool_definitions()
        
        # Create conversation with system prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        
        # Chat with tools (pass LMS client for tool execution)
        response = llm_client.chat_with_tools(messages, tools, lms_client=lms_client)
        
        return response
        
    except Exception as e:
        print(f"[error] Intent routing failed: {e}", file=sys.stderr)
        return (
            f"🤔 I encountered an error processing your request: {str(e)}\n\n"
            f"Try using commands like /help, /labs, or /scores lab-04"
        )


def get_welcome_keyboard() -> list[list[tuple[str, str]]]:
    """Get inline keyboard buttons for welcome message.
    
    Returns:
        List of keyboard rows, each row is a list of (label, callback_data) tuples.
    """
    return [
        [
            ("📋 Labs", "/labs"),
            ("🏥 Health", "/health"),
        ],
        [
            ("📊 Scores lab-04", "/scores lab-04"),
            ("❓ Help", "/help"),
        ],
    ]


def format_keyboard_hint() -> str:
    """Get a hint about available quick actions.
    
    Returns:
        Text hint about keyboard buttons.
    """
    return (
        "\n\n💡 Quick actions available:\n"
        "• /labs — See all labs\n"
        "• /scores lab-XX — Get scores for a lab\n"
        "• /health — Check system status\n"
        "• Or just ask me a question!"
    )
