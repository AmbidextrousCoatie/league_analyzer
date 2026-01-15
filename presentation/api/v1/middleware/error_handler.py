"""
Error Handling Middleware.

Provides consistent error handling and HTTP response formatting
for API endpoints.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from infrastructure.logging import get_logger
from application.exceptions import (
    EntityNotFoundError,
    ValidationError,
    BusinessRuleViolationError
)

logger = get_logger(__name__)


async def handle_application_exceptions(request: Request, call_next):
    """
    Middleware to handle application layer exceptions and convert them
    to appropriate HTTP responses.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain
    
    Returns:
        HTTP response with appropriate status code and error message
    """
    try:
        response = await call_next(request)
        return response
    except EntityNotFoundError as e:
        logger.warning(f"Entity not found: {str(e)}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "EntityNotFoundError",
                "detail": str(e),
                "path": str(request.url.path)
            }
        )
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "ValidationError",
                "detail": str(e),
                "path": str(request.url.path)
            }
        )
    except BusinessRuleViolationError as e:
        logger.warning(f"Business rule violation: {str(e)}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "BusinessRuleViolationError",
                "detail": str(e),
                "path": str(request.url.path)
            }
        )
    except HTTPException:
        # Re-raise HTTPException to let FastAPI handle it
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "An unexpected error occurred. Please try again later.",
                "path": str(request.url.path)
            }
        )
