"""podplay_api constants."""
import logging

PODPLAY_USER_AGENT = "podplay_api python/3.8.5 aiohttp/3.8.3"

PODPLAY_API_URL = "https://api.podplay.com/v1"
PODPLAY_AUTH_CLIENT_ID = "6e1a23e7-71ec-4483-918a-25c33852c9c9"
PODPLAY_AUTH_TENANT = "reacthello"
PODPLAY_AUTH_LOGIN_USER_FLOW = "B2C_1_web_combined_login"
PODPLAY_AUTH_URL = f"https://{PODPLAY_AUTH_TENANT}.b2clogin.com"
PODPLAY_AUTH_TOKEN_URL = "https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{login_user_flow}".format(
    tenant=PODPLAY_AUTH_TENANT,
    login_user_flow=PODPLAY_AUTH_LOGIN_USER_FLOW,
)
PODPLAY_AUTH_REDIRECT_URI = "https://podplay.com/static/redirect.html"

PODPLAY_SCHIBSTED_AUTH_DOMAIN = "https://payment.schibsted.no"
PODPLAY_SCHIBSTED_AUTH_URL_BASE = f"{PODPLAY_SCHIBSTED_AUTH_DOMAIN}/oauth/authorize"
PODPLAY_SCHIBSTED_AUTH_CLIENT_ID = "626bcf5e1332f10a4997c29a"
PODPLAY_SCHIBSTED_AUTH_REDIRECT = "https://podplay.com/auth/handleSchibstedLogin"
PODPLAY_SCHIBSTED_AUTH_RETURN_URL = "https://podplay.com/no/oppdag"
PODPLAY_SCHIBSTED_AUTH_SCOPE = "openid email"
PODPLAY_SCHIBSTED_AUTH_RESPONSE_TYPE = "code"
PODPLAY_SCHIBSTED_AUTH_CSRF_URL = f"{PODPLAY_SCHIBSTED_AUTH_DOMAIN}/authn/api/settings/csrf"
PODPLAY_SCHIBSTED_AUTH_LOGIN_URL = f"{PODPLAY_SCHIBSTED_AUTH_DOMAIN}/authn/api/identity/login/"
PODPLAY_SCHIBSTED_AUTH_FINISH_URL = f"{PODPLAY_SCHIBSTED_AUTH_DOMAIN}/authn/identity/finish/"

TIMEOUT = 10

LOGGER = logging.getLogger(__package__)
