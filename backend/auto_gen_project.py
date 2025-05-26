import logging
import os
import sys
import requests
from dotenv import load_dotenv
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self, backend_url: str, username: str, password: str):
        self.backend_url = backend_url
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def get_initial_tokens(self) -> Tuple[str, str]:
        """
        Get initial access and refresh tokens using username and password.
        
        Returns:
            Tuple[str, str]: Access token and refresh token
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        token_url = f"{self.backend_url}/token"
        token_data = {
            "username": self.username,
            "password": self.password
        }

        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        return self.access_token, self.refresh_token

    def refresh_access_token(self) -> str:
        """
        Get a new access token using the refresh token.
        
        Returns:
            str: New access token
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        refresh_url = f"{self.backend_url}/token/refresh"
        headers = {"Authorization": f"Bearer {self.refresh_token}"}
        
        response = requests.post(refresh_url, headers=headers)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return self.access_token

    def get_valid_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            str: Valid access token
        """
        if not self.access_token:
            return self.get_initial_tokens()[0]

        try:
            # Test the current access token
            test_url = f"{self.backend_url}/users/me"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(test_url, headers=headers)
            response.raise_for_status()
            return self.access_token
        except requests.exceptions.RequestException:
            try:
                # Try to refresh the access token
                return self.refresh_access_token()
            except requests.exceptions.RequestException:
                # If refresh fails, get new tokens
                return self.get_initial_tokens()[0]

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

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv("/settings/.env", override=True)
    logger.info("Hello World!")

    # Initialize token manager
    backend_url = os.environ.get("BACKEND_URL")
    backend_username = os.environ.get("BACKEND_USERNAME")
    backend_password = os.environ.get("BACKEND_PASSWORD")

    try:
        token_manager = TokenManager(backend_url, backend_username, backend_password)
        
        # Get initial tokens
        access_token, refresh_token = token_manager.get_initial_tokens()
        logger.info("Successfully obtained initial tokens")

        # Hit the /users/me endpoint using the token manager
        me_url = f"{backend_url}/users/me"
        response = make_authenticated_request(me_url, token_manager)
        response.raise_for_status()
        user_data = response.json()
        logger.info(f"Successfully retrieved user data: {user_data}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
