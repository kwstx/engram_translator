class EngramSDKError(Exception):
    """Base class for SDK errors."""


class EngramAuthError(EngramSDKError):
    """Raised when authentication fails or tokens are missing."""


class EngramRequestError(EngramSDKError):
    """Raised when an HTTP request fails."""


class EngramResponseError(EngramSDKError):
    """Raised when an HTTP response cannot be parsed."""
