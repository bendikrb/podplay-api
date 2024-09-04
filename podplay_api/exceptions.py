"""podplay_api exceptions."""


class PodPlayApiError(Exception):
    """Generic PodPlay exception."""


class PodPlayApiConnectionError(PodPlayApiError):
    """PodPlay connection exception."""


class PodPlayApiConnectionTimeoutError(PodPlayApiConnectionError):
    """PodPlay connection timeout exception."""


class PodPlayApiRateLimitError(PodPlayApiConnectionError):
    """PodPlay Rate Limit exception."""


class PodPlayAccessDeniedError(PodPlayApiError):
    """PodPlay access denied error."""
