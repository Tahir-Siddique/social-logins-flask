from flask import Blueprint, render_template, session, redirect, url_for, flash
from src.app.services.oauth import oauth_service
import logging
from src.utils import get_provider

# Initialize Blueprint for authentication routes
auth_bp = Blueprint("auth", __name__)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@auth_bp.route("/", methods=["GET"])
def index():
    """
    Display the index page. If the user is logged in, their data is shown.

    Returns:
        Rendered HTML page with user data if available.
    """
    user_data = session.get("user")
    return render_template("index.html", user=user_data)

@auth_bp.route("/auth/<provider>")
async def social_login(provider):
    """
    Start the social login process by redirecting to the provider's authorization page.

    Args:
        provider (str): The OAuth provider (Google, Facebook, LinkedIn).

    Returns:
        RedirectResponse: Redirects to the provider's authorization URL.
    """
    try:
        redirect_url = oauth_service.initiate_social_login(get_provider(provider))
        return redirect_url
    except Exception as e:
        logger.error(f"Error during social login: {str(e)}")
        flash("Failed to initiate social login.")
        return redirect(url_for("auth.index"))

@auth_bp.route("/auth/<provider>/callback")
def auth_callback(provider):
    """
    Handle the OAuth callback and fetch user data.

    Args:
        provider (str): The OAuth provider.

    Returns:
        RedirectResponse: Redirects to success or failure page based on login result.
    """
    try:
        oauth_service.handle_oauth_callback(get_provider(provider))
        user_data = session["user_data"]
        if user_data:
            return redirect(url_for("auth.success"))
        else:
            return redirect(url_for("auth.failure"))
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        return redirect(url_for("auth.failure"))

@auth_bp.route("/success")
def success():
    """
    Display the success page after successful login.

    Returns:
        Rendered HTML page with user data if available, otherwise redirects to failure.
    """
    user_data = session.get("user_data")
    if not user_data:
        return redirect(url_for("auth.failure"))
    return render_template("success.html", user=user_data)

@auth_bp.route("/failure")
def failure():
    """
    Display the failure page if login fails.

    Returns:
        Rendered HTML failure page.
    """
    return render_template("failure.html")

@auth_bp.route("/logout")
def logout():
    """
    Log out the user by clearing session data.

    Returns:
        RedirectResponse: Redirects to the homepage after logging out.
    """
    session.clear()
    logger.info("User logged out successfully.")
    return redirect(url_for("auth.index"))
