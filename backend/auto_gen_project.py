import logging
import os
import sys
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def get_access_token(backend_url: str, username: str, password: str) -> str:
    """
    Get an access token from the backend using username and password.
    
    Args:
        backend_url: Base URL of the backend
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        str: Access token
        
    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    token_url = f"{backend_url}/token"
    token_data = {
        "username": username,
        "password": password
    }

    token_response = requests.post(token_url, data=token_data)
    token_response.raise_for_status()
    return token_response.json()["access_token"]


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv("/settings/.env", override=True)
    logger.info("Hello World!")

    # Test getting a token from backend
    backend_url = os.environ.get("BACKEND_URL")
    backend_username = os.environ.get("BACKEND_USERNAME")
    backend_password = os.environ.get("BACKEND_PASSWORD")

    try:
        # Get access token
        access_token = get_access_token(backend_url, backend_username, backend_password)
        logger.info("Successfully obtained access token")

        # Hit the /users/me endpoint
        me_url = f"{backend_url}/users/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = requests.get(me_url, headers=headers)
        me_response.raise_for_status()
        user_data = me_response.json()
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
