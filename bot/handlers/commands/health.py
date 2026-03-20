"""Handler for /health command."""

import httpx

from services.lms_api import get_lms_client


def handle_health(lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /health command.
    
    Args:
        lms_api_url: The LMS API base URL.
        lms_api_key: The LMS API key for authentication.
        
    Returns:
        Backend health status.
    """
    try:
        client = get_lms_client(lms_api_url, lms_api_key)
        result = client.health_check()
        return f"🏥 Backend is healthy. {result['item_count']} items available."
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"❌ Backend error: {str(e)}"
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
