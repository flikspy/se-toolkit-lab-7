"""Handler for /scores command."""

import httpx

from services.lms_api import get_lms_client


def handle_scores(lab_id: str | None, lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /scores command.
    
    Args:
        lab_id: The lab ID to get scores for (e.g., "lab-04").
        lms_api_url: The LMS API base URL.
        lms_api_key: The LMS API key for authentication.
        
    Returns:
        Student scores for the specified lab.
    """
    if lab_id is None:
        return "❌ Please specify a lab ID. Example: /scores lab-04"
    
    try:
        client = get_lms_client(lms_api_url, lms_api_key)
        pass_rates = client.get_pass_rates(lab_id)
        
        if not pass_rates:
            return f"📊 No scores found for {lab_id}."
        
        lines = [f"📊 Pass rates for {lab_id}:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown task")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"• {task_name}: {avg_score}% ({attempts} attempts)")
        
        return "\n".join(lines)
        
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.HTTPError as e:
        return f"❌ Backend error: {str(e)}"
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
