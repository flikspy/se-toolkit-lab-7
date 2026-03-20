"""LMS API client with Bearer token authentication."""

import httpx


class LMSAPIClient:
    """Client for the LMS backend API.

    Uses Bearer token authentication with credentials from config.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the API client.

        Args:
            base_url: The base URL of the LMS API (e.g., http://localhost:42002).
            api_key: The API key for Bearer token authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict]:
        """Get all items (labs and tasks).

        Returns:
            List of items with their metadata.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list[dict]:
        """Get all enrolled learners.

        Returns:
            List of learners with their metadata.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict]:
        """Get score distribution for a lab.

        Args:
            lab: The lab ID (e.g., "lab-04").

        Returns:
            List of score buckets with counts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Get pass rates for a specific lab.

        Args:
            lab: The lab ID (e.g., "lab-04").

        Returns:
            List of task pass rates with avg_score and attempts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: str) -> list[dict]:
        """Get submission timeline for a lab.

        Args:
            lab: The lab ID (e.g., "lab-04").

        Returns:
            List of daily submission counts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict]:
        """Get per-group performance for a lab.

        Args:
            lab: The lab ID (e.g., "lab-04").

        Returns:
            List of groups with avg scores and student counts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 5) -> list[dict]:
        """Get top learners for a lab.

        Args:
            lab: The lab ID (e.g., "lab-04").
            limit: Number of top learners to return.

        Returns:
            List of top learners with their scores.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab.

        Args:
            lab: The lab ID (e.g., "lab-04").

        Returns:
            Dict with completion rate percentage.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger ETL pipeline sync.

        Returns:
            Dict with items_loaded and logs_loaded counts.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check if the backend is healthy.

        Returns:
            Dict with 'healthy' status and 'item_count'.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()


# Global client instance (lazy-loaded)
_client: LMSAPIClient | None = None


def get_lms_client(base_url: str, api_key: str) -> LMSAPIClient:
    """Get or create the global LMS API client.

    Args:
        base_url: The base URL of the LMS API.
        api_key: The API key for authentication.

    Returns:
        LMSAPIClient instance.
    """
    global _client
    if _client is None:
        _client = LMSAPIClient(base_url, api_key)
    return _client


def get_tools_registry() -> dict:
    """Get the registry of all LLM tools.
    
    Returns:
        Dict mapping tool names to functions.
    """
    # Use global client
    global _client
    if _client is None:
        # Will be initialized by LLMClient when needed
        return {}
    
    return {
        "get_items": _client.get_items,
        "get_learners": _client.get_learners,
        "get_scores": lambda lab: _client.get_scores(lab),
        "get_pass_rates": lambda lab: _client.get_pass_rates(lab),
        "get_timeline": lambda lab: _client.get_timeline(lab),
        "get_groups": lambda lab: _client.get_groups(lab),
        "get_top_learners": lambda lab, limit=5: _client.get_top_learners(lab, limit),
        "get_completion_rate": lambda lab: _client.get_completion_rate(lab),
        "trigger_sync": _client.trigger_sync,
    }


def get_tool_definitions() -> list[dict]:
    """Get tool definitions for LLM tool calling.
    
    Returns:
        List of tool definitions in OpenAI function calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks. Use this to find available labs or when user asks about what's available.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of all enrolled students and their groups. Use when user asks about enrollment or students.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets: 0-24%, 25-49%, 50-74%, 75-100%) for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab. Use when user asks about scores, pass rates, or task difficulty.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline (submissions per day) for a lab. Use when user asks about activity over time or submission patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group average scores and student counts for a lab. Use when user asks about group performance or compares groups.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use when user asks about best students or leaderboard.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                        "limit": {"type": "integer", "description": "Number of top learners to return (default: 5)"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab. Use when user asks about completion or how many students finished.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL pipeline to sync data from autochecker. Use when user asks to refresh or update data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]
