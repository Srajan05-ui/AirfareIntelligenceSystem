from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import logging

logger = logging.getLogger(__name__)

# In production, this comes from AWS Secrets Manager / environment variables
API_KEY_HEADER = APIKeyHeader(name="X-Government-API-Key", auto_error=False)
VALID_API_KEYS = {"mospi_admin_778899", "dgca_viewer_112233"}

def verify_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """
    Mock JWT/API Key validator.
    Ensures that ONLY authorized government dashboards (like the React portal) 
    can pull inflation metrics. Stops unauthorized public scraping of our API.
    """
    if api_key_header not in VALID_API_KEYS:
        logger.warning(f"Unauthorized API access attempt with key: {api_key_header}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Government API Key",
        )
    return api_key_header
