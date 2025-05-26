import logging
import requests
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
        logger.info("Getting initial tokens using username/password")
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
        logger.info("Successfully obtained initial tokens")
        logger.info(f"access_token: {self.access_token}")
        logger.info(f"refresh_token: {self.refresh_token}")
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

        logger.info("Refreshing access token using refresh token")
        refresh_url = f"{self.backend_url}/refresh-token"
        data = {
            "token": self.refresh_token
        }
        
        response = requests.post(refresh_url, json=data)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        logger.info("Successfully refreshed access token")
        return self.access_token

    def get_valid_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            str: Valid access token
        """
        if not self.access_token:
            logger.info("No access token available, getting initial tokens")
            return self.get_initial_tokens()[0]

        try:
            # Test the current access token
            test_url = f"{self.backend_url}/users/me"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(test_url, headers=headers)
            response.raise_for_status()
            logger.info("Current access token is valid")
            return self.access_token
        except requests.exceptions.RequestException:
            try:
                # Try to refresh the access token
                logger.info("Access token is invalid, attempting to refresh")
                return self.refresh_access_token()
            except requests.exceptions.RequestException:
                # If refresh fails, get new tokens
                logger.info("Refresh token is invalid, getting new tokens")
                return self.get_initial_tokens()[0] 