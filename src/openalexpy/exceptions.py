class OpenAlexError(Exception):
    pass


class QueryError(OpenAlexError):
    pass


class RateLimitError(OpenAlexError):
    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class CreditsExhaustedError(OpenAlexError):
    def __init__(
        self,
        message: str,
        reset_at: str | None = None,
        remaining_usd: float = 0.0,
    ):
        super().__init__(message)
        self.reset_at = reset_at
        self.remaining_usd = remaining_usd


class NotFoundError(OpenAlexError):
    pass


class ContentUnavailableError(OpenAlexError):
    pass
