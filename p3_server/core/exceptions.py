from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = "INTERNAL_ERROR"):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundError(AppError):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=404, detail=detail, code="NOT_FOUND")


class ValidationError(AppError):
    def __init__(self, detail: str = "请求参数无效"):
        super().__init__(status_code=422, detail=detail, code="VALIDATION_ERROR")


class ServiceUnavailableError(AppError):
    def __init__(self, detail: str = "服务暂不可用"):
        super().__init__(status_code=503, detail=detail, code="SERVICE_UNAVAILABLE")


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {"code": exc.code, "message": exc.detail}
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {"code": "HTTP_ERROR", "message": exc.detail}
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "服务器内部错误"}
            },
        )