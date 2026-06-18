from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from config import settings
from routers import analysis

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia lifecycle da aplicação"""
    logger.info("🚀 Iniciando Code Performance Time Machine API")
    yield
    logger.info("🛑 Encerrando aplicação")


# Criar app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Análise de performance de repositórios Git com IA",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analysis.router)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Code Performance Time Machine API",
        "version": settings.API_VERSION,
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "analyze_detailed": "/api/v1/analyze/detailed",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }


@app.get("/docs-redirect")
async def docs_redirect():
    """Redireciona para documentação interativa"""
    return {"docs_url": "/docs", "redoc_url": "/redoc"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
