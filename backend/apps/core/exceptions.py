from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": "You do not have permission to perform this action.",
                }
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation error.",
                    "details": exc.message_dict if hasattr(exc, "message_dict") else str(exc),
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, IntegrityError):
        return Response(
            {
                "error": {
                    "code": "INTEGRITY_ERROR",
                    "message": "A database integrity error occurred. This record may already exist.",
                }
            },
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class APIError(Exception):
    def __init__(self, code, message, details=None, status_code=400):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self):
        result = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class NotFoundError(APIError):
    def __init__(self, resource="Resource", resource_id=None):
        message = f"{resource} not found."
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found."
        super().__init__("NOT_FOUND", message, status_code=404)


class ConflictError(APIError):
    def __init__(self, message="A conflict occurred with the current state of the resource."):
        super().__init__("CONFLICT", message, status_code=409)


class BusinessRuleError(APIError):
    def __init__(self, message="A business rule validation failed."):
        super().__init__("BUSINESS_RULE_VIOLATION", message, status_code=422)


class UnauthorizedError(APIError):
    def __init__(self, message="Authentication is required."):
        super().__init__("UNAUTHORIZED", message, status_code=401)


class ForbiddenError(APIError):
    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__("FORBIDDEN", message, status_code=403)


class RateLimitError(APIError):
    def __init__(self, message="Rate limit exceeded. Please try again later."):
        super().__init__("RATE_LIMITED", message, status_code=429)
