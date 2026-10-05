class ZenkaiError(Exception):
    user_message = "Zenkai could not complete that request."

    def __init__(self, message: str, *, user_message: str | None = None) -> None:
        super().__init__(message)
        if user_message:
            self.user_message = user_message


class ConfigurationError(ZenkaiError):
    user_message = "Zenkai is not configured correctly."


class DatabaseError(ZenkaiError):
    user_message = "Zenkai could not reach its database. Please try again shortly."


class CacheError(ZenkaiError):
    user_message = "Zenkai could not reach its cache. Please try again shortly."


class ProviderUnavailableError(ZenkaiError):
    user_message = "Zenkai could not reach that service. Please try again shortly."


class PermissionDeniedError(ZenkaiError):
    user_message = "You do not have permission to use that action."


class InteractionNotReadyError(ZenkaiError):
    user_message = "Zenkai is still preparing that response. Please try again."
