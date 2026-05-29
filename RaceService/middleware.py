from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def validation_error_handler(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = {}
        for error in exc.errors():
            field_name = error['loc'][-1]
            message = error['msg'].replace("Value error, ", "")
            errors[field_name] = message
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Validation error",
                "errors": errors
            }
        )