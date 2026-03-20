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
