import logging
import os
import sys
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s::%(lineno)d - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    load_dotenv("backend/settings/.env", override=True)
    logger.info("Hello World!")
    
    # Test getting a token from backend
    backend_url = os.environ.get("BACKEND_URL")
    backend_username = os.environ.get("BACKEND_USERNAME")
    backend_password = os.environ.get("BACKEND_PASSWORD")
    logger.info(f"Backend URL: {backend_url}")
    logger.info(f"Backend Username: {backend_username}")
    
    # Get access token
    token_url = f"{backend_url}/token"
    token_data = {
        "username": backend_username,
        "password": backend_password
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
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
