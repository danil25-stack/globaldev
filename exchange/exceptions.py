

class ExchangeServiceError(Exception):
    """Base exception for exchange service errors."""
    pass


class NotEnoughBalance(ExchangeServiceError):
    """Exception raised when a user has insufficient balance."""
    pass


class ExternalAPIError(ExchangeServiceError):
    """Exception raised for errors occurring in external API calls."""
    pass
