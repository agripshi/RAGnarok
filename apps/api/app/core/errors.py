class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__("AUTHENTICATION_ERROR", message, 401)


class AccessDeniedError(AppError):
    def __init__(self, message: str = "Access restricted to members of the private HR Teams channel.") -> None:
        super().__init__("ACCESS_DENIED", message, 403)


class ConversationNotFoundError(AppError):
    def __init__(self, message: str = "Conversation not found.") -> None:
        super().__init__("CONVERSATION_NOT_FOUND", message, 404)


class AiBackendError(AppError):
    def __init__(self, message: str = "AI backend unavailable.") -> None:
        super().__init__("AI_BACKEND_ERROR", message, 502)
