import requests
from .token_manager import TokenManager

def make_authenticated_request(url: str, token_manager: TokenManager, method: str = "GET", **kwargs) -> requests.Response:
    """
    Make an authenticated request with automatic token refresh.
    
    Args:
        url: URL to make the request to
        token_manager: TokenManager instance
        method: HTTP method to use
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        requests.Response: Response from the request
    """
    access_token = token_manager.get_valid_access_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {access_token}"
    kwargs["headers"] = headers

    response = requests.request(method, url, **kwargs)
    return response 