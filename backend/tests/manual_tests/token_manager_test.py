import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from utils.token_manager import TokenManager

logger = logging.getLogger(__name__)


def make_authenticated_request(url: str, token_manager: TokenManager, method: str = "GET",
                               **kwargs) -> requests.Response:
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
    load_dotenv("backend/settings/.env", override=True)
    logger.info("Starting application")

    # Initialize token manager
    backend_url = os.environ.get("BACKEND_URL")
    backend_username = os.environ.get("BACKEND_USERNAME")
    backend_password = os.environ.get("BACKEND_PASSWORD")
    token_manager = TokenManager(backend_url, backend_username, backend_password)
    logger.info(f"backend_url: {backend_url}")
    logger.info(f"backend_username: {backend_username}")

    try:
        # Get initial tokens
        _, _ = token_manager.get_initial_tokens()

        while True:
            try:
                # Hit the protected resource endpoint
                protected_url = f"{backend_url}/protected-resource"
                response = make_authenticated_request(protected_url, token_manager)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully retrieved protected resource data: {data}")

                # Wait for 10 seconds before next request
                time.sleep(10)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error accessing protected resource: {e}")
                # Continue the loop even if there's an error
                time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
