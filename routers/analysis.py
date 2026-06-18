from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from models.schemas import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
    ComparisonRequest,
    ComparisonResponse,
    CommitMetricResponse,
    PerformanceReportResponse
)
from models.database import Repository, CommitMetric, PerformanceAnalysis
from services.git_analyzer import GitAnalyzer
from services.metrics_calculator import MetricsCalculator
from services.ai_analyzer import AIAnalyzer
from config import settings

router = APIRouter(prefix="/api/v1", tags=["analysis"])
logger = logging.getLogger(__name__)

# Instâncias globais
git_analyzer = GitAnalyzer()
ai_analyzer = AIAnalyzer(settings.ANTHROPIC_API_KEY)


@router.post("/analyze", response_model=RepositoryAnalysisResponse)
async def analyze_repository(
    request: RepositoryAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = None
):
    """
    Analisa um repositório GitHub e extrai métricas de performance
    
    Exemplo:
    ```
    POST /api/v1/analyze
    {
        "url": "https://github.com/user/repo.git",
        "analyze_all_history": false
    }
    ```
    """
    try:
        logger.info(f"Iniciando análise de {request.url}")
        
        # Clone do repositório
        repo = git_analyzer.clone_repository(request.url)
        
        # Extrai informações do repositório
        repo_info = git_analyzer.get_repository_info(repo)
        
        # Get commits
        limit = None if request.analyze_all_history else 50
        commits_data = git_analyzer.get_commits_with_files(repo, limit=limit)
        
        # Calcula métricas para cada commit
        repo_path = str(repo.working_dir)
        commits_with_metrics = []
        
        for commit in commits_data:
            # Calcula complexidade do repositório naquele ponto
            try:
                complexity, _ = MetricsCalculator.calculate_complexity(repo_path)
            except:
                complexity = 0.0
            
            commit["complexity"] = complexity
            commit["avg_method_length"] = 0.0  # Placeholder
            commits_with_metrics.append(commit)
        
        # Preparar resposta
        response_commits = [
            CommitMetricResponse(
                sha=c["sha"],
                message=c["message"],
                author=c["author"],
                committed_date=c["committed_date"],
                complexity=c.get("complexity", 0.0),
                lines_added=c.get("lines_added", 0),
                lines_removed=c.get("lines_removed", 0),
                files_changed=c.get("files_changed", 0),
                avg_method_length=c.get("avg_method_length", 0.0)
            )
            for c in commits_with_metrics
        ]
        
        response = RepositoryAnalysisResponse(
            repository_url=repo_info.get("url", request.url),
            repository_name=repo_info.get("name", "Unknown"),
            total_commits=len(commits_with_metrics),
            analysis_status="completed",
            commits=response_commits
        )
        
        # Cleanup em background
        background_tasks.add_task(git_analyzer.cleanup, repo_path)
        
        logger.info(f"Análise concluída: {len(commits_with_metrics)} commits processados")
        
        return response
    
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze/detailed", response_model=PerformanceReportResponse)
async def analyze_detailed(
    request: RepositoryAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Análise detalhada com insights de IA
    Identifica degradações e fornece recomendações
    
    Exemplo:
    ```
    POST /api/v1/analyze/detailed
    {
        "url": "https://github.com/user/repo.git",
        "analyze_all_history": false
    }
    ```
    """
    try:
        logger.info(f"Iniciando análise detalhada de {request.url}")
        
        # Clone
        repo = git_analyzer.clone_repository(request.url)
        repo_info = git_analyzer.get_repository_info(repo)
        repo_path = str(repo.working_dir)
        
        # Commits
        limit = None if request.analyze_all_history else 50
        commits_data = git_analyzer.get_commits_with_files(repo, limit=limit)
        
        # Calcula complexidade
        for commit in commits_data:
            try:
                complexity, _ = MetricsCalculator.calculate_complexity(repo_path)
                commit["complexity"] = complexity
            except:
                commit["complexity"] = 0.0
        
        # Análise de IA
        ai_analysis = ai_analyzer.analyze_performance_degradation(
            commits_data,
            repo_info
        )
        
        response_commits = [
            CommitMetricResponse(
                sha=c["sha"],
                message=c["message"],
                author=c["author"],
                committed_date=c["committed_date"],
                complexity=c.get("complexity", 0.0),
                lines_added=c.get("lines_added", 0),
                lines_removed=c.get("lines_removed", 0),
                files_changed=c.get("files_changed", 0),
                avg_method_length=0.0
            )
            for c in commits_data
        ]
        
        response = PerformanceReportResponse(
            repository_url=repo_info.get("url", request.url),
            total_commits_analyzed=len(commits_data),
            degradations_found=len(ai_analysis.get("degradation_points", [])),
            ai_analysis=ai_analysis.get("analysis", ""),
            commits_timeline=response_commits
        )
        
        # Cleanup
        background_tasks.add_task(git_analyzer.cleanup, repo_path)
        
        return response
    
    except Exception as e:
        logger.error(f"Erro na análise detalhada: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_commits(request: ComparisonRequest):
    """
    Compara dois commits específicos
    """
    try:
        # Aqui você buscaria os commits do banco de dados
        # Por enquanto, retornamos um placeholder
        raise HTTPException(
            status_code=501,
            detail="Endpoint de comparação ainda em desenvolvimento"
        )
    
    except Exception as e:
        logger.error(f"Erro ao comparar: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Code Performance Time Machine API",
        "version": "1.0.0"
    }
