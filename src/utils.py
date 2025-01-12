from src.app.services.oauth import OAuthProvider


def get_provider(provider_name):
    if provider_name == OAuthProvider.GOOGLE.value:
        return OAuthProvider.GOOGLE
    elif provider_name == OAuthProvider.LINKEDIN.value:
        return OAuthProvider.LINKEDIN
    elif provider_name == OAuthProvider.FACEBOOK.value:
        return OAuthProvider.FACEBOOK
    return None