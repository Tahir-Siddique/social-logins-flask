import os
import logging
from enum import Enum
from typing import Optional, Dict, Any
from flask import session, url_for, request, redirect
import httpx
from werkzeug.exceptions import BadRequest, InternalServerError

from src.config import settings
from src.app import oauth

# Initialize logger for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class OAuthProvider(str, Enum):
    """Enum representing supported OAuth providers."""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


class OAuthService:
    """Service class for handling OAuth-based authentication with multiple providers."""

    def __init__(self):
        """Initialize OAuth clients and log the initialization."""
        self.clients = self._initialize_clients()
        logger.info("OAuth clients initialized successfully.")

    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize OAuth clients for Google, Facebook, and LinkedIn."""
        logger.debug("Initializing OAuth clients.")
        return {
            OAuthProvider.GOOGLE: self._create_google_client(),
            OAuthProvider.FACEBOOK: self._create_facebook_client(),
            OAuthProvider.LINKEDIN: self._create_linkedin_client()
        }

    def _create_google_client(self):
        """Create and register an OAuth client for Google."""
        return oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={"scope": "openid email profile"}
        )

    def _create_facebook_client(self):
        """Create and register an OAuth client for Facebook."""
        return oauth.register(
            name="facebook",
            client_id=settings.FACEBOOK_CLIENT_ID,
            client_secret=settings.FACEBOOK_CLIENT_SECRET,
            access_token_url="https://graph.facebook.com/oauth/access_token",
            authorize_url="https://www.facebook.com/dialog/oauth",
            api_base_url="https://graph.facebook.com/v12.0/",
            client_kwargs={"scope": "email public_profile"}
        )

    def _create_linkedin_client(self):
        """Create and register an OAuth client for LinkedIn."""
        return oauth.register(
            name="linkedin",
            client_id=settings.LINKEDIN_CLIENT_ID,
            client_secret=settings.LINKEDIN_CLIENT_SECRET,
            access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
            authorize_url="https://www.linkedin.com/oauth/v2/authorization",
            api_base_url="https://api.linkedin.com/v2/",
            client_kwargs={"scope": "openid profile email"}
        )

    def initiate_social_login(self, provider: OAuthProvider):
        """Initiate the OAuth login process for a given provider.

        Args:
            provider (OAuthProvider): The OAuth provider to use.

        Returns:
            Response: A redirect response to the provider's authorization page.

        Raises:
            BadRequest: If the provider is unsupported.
        """
        oauth_client = self.clients.get(provider)
        if not oauth_client:
            raise BadRequest(f"Unsupported provider: {provider}")

        
        redirect_uri = url_for(
            "auth.auth_callback", 
            provider=provider.value, 
            _external=True, 
            _scheme="https" if not settings.DEBUG else "http"
        )

        session["redirect_path"] = redirect_uri
        state = os.urandom(16).hex()
        session["oauth_state"] = state

        logger.info(f"Initiating login with provider: {provider}")
        return oauth_client.authorize_redirect(redirect_uri, state=state)

    def get_token(self, provider: OAuthProvider):
        """Fetch the access token for a given provider.

        Args:
            provider (OAuthProvider): The OAuth provider to use.

        Returns:
            Dict[str, Any]: The access token data.

        Raises:
            BadRequest: If token retrieval fails.
        """
        oauth_client = self.clients.get(provider)

        if provider == OAuthProvider.LINKEDIN:
            authorization_code = request.args.get("code")
            redirect_uri = str(
                url_for(
                    "auth.auth_callback", 
                    provider=provider.value, 
                    _external=True,
                    _scheme="https" if not settings.DEBUG else "http"
                )
            )
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            }

            with httpx.Client() as client:
                token_response = client.post("https://www.linkedin.com/oauth/v2/accessToken", data=token_data)
                if token_response.status_code != 200:
                    raise BadRequest(
                        f"Failed to fetch access token: {token_response.text}"
                    )
                return token_response.json()
        else:
            return oauth_client.authorize_access_token()

    def handle_oauth_callback(self, provider: OAuthProvider):
        """Handle the OAuth callback after the user authorizes the application.

        Args:
            provider (OAuthProvider): The OAuth provider handling the callback.

        Returns:
            Response: A redirect response to the success page.

        Raises:
            BadRequest: If the state parameter is invalid.
            InternalServerError: If user data retrieval fails.
        """
        stored_state = session.get("oauth_state")
        received_state = request.args.get("state")
        if not stored_state or stored_state != received_state:
            logger.warning("Invalid state parameter during OAuth callback.")
            raise BadRequest("Invalid state parameter.")

        session.pop("oauth_state", None)

        token = self.get_token(provider)
        user_data = self.fetch_user_data(provider, token)

        if not user_data:
            logger.error("Failed to fetch user data.")
            raise InternalServerError("Failed to fetch user data.")

        session["user_data"] = user_data
        redirect_path = session.pop("redirect_path", url_for("auth.success"))
        logger.info(f"User authenticated successfully with provider: {provider}")
        return redirect(redirect_path)

    def fetch_user_data(self, provider: str, token: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch user data from the OAuth provider using the access token.

        Args:
            provider (str): The OAuth provider to fetch user data from.
            token (Dict[str, Any]): The access token data.

        Returns:
            Optional[Dict[str, Any]]: The user data if successful, otherwise None.
        """
        try:
            logger.info(f"Fetching user data from provider: {provider}")
            oauth_client = self.clients.get(provider)

            if provider == OAuthProvider.LINKEDIN:
                response = oauth_client.get("https://api.linkedin.com/v2/userinfo", token=token)
            elif provider == OAuthProvider.FACEBOOK:
                response = oauth_client.get(
                    "https://graph.facebook.com/v12.0/me?fields=id,name,email,picture", token=token
                )
            else:  # Google
                response = oauth_client.get("https://www.googleapis.com/oauth2/v1/userinfo", token=token)

            if response.status_code == 200:
                logger.debug("User data fetched successfully.")
                return response.json()
            else:
                logger.error(f"Failed to fetch user data: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Error fetching user data: {str(e)}")
            return None


# Instantiate the OAuthService
oauth_service = OAuthService()
