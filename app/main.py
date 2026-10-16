
from fastapi import FastAPI

from app.api.use_cases import router as use_cases_router
from app.api.evaluations import router as evaluations_router

from app.core.logging_config import configure_logging
from app.middleware import RequestContextMiddleware

from app.services.readiness_service import check_readiness
from app.api.deployments import router as deployments_router
from app.core.exception_handlers import register_exception_handlers
configure_logging()
app = FastAPI(
    title="Enterprise AI Deployment & Evaluation Platform",
    description=(
        "A platform for evaluating AI systems, enforcing "
        "release policies, and measuring deployment readiness."
    ),
    version="0.1.0",
)
register_exception_handlers(app)
app.include_router(use_cases_router)
app.include_router(evaluations_router)
app.add_middleware(RequestContextMiddleware)
app.include_router(deployments_router)
@app.get("/", tags=["Platform"])
async def root() -> dict[str, str]:
    return {
        "service": "Enterprise AI Deployment & Evaluation Platform",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "enterprise-ai-deployment-platform",
    }
@app.get("/ready", tags=["Health"])
async def readiness():
    from fastapi.responses import JSONResponse

    result = check_readiness()
    status_code = 200 if result["status"] == "ready" else 503

    return JSONResponse(
        status_code=status_code,
        content=result,
    )

@app.get("/metrics", tags=["Monitoring"])
async def metrics() -> dict[str, int | float]:
    from app.core.metrics import request_metrics

    return request_metrics.snapshot()