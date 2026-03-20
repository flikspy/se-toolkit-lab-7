"""Handler for /labs command."""

import httpx

from services.lms_api import get_lms_client


def handle_labs(lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /labs command.
    
    Args:
        lms_api_url: The LMS API base URL.
        lms_api_key: The LMS API key for authentication.
        
    Returns:
        List of available labs.
    """
    try:
        client = get_lms_client(lms_api_url, lms_api_key)
        items = client.get_items()
        
        # Filter only labs
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "📋 No labs available."
        
        lines = ["📋 Available Labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            lines.append(f"• {title}")
        
        return "\n".join(lines)
        
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.HTTPError as e:
        return f"❌ Backend error: {str(e)}"
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
