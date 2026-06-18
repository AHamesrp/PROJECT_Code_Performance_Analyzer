from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CommitMetricResponse(BaseModel):
    sha: str
    message: str
    author: str
    committed_date: datetime
    complexity: float
    lines_added: int
    lines_removed: int
    files_changed: int
    avg_method_length: float

    class Config:
        from_attributes = True


class RepositoryAnalysisRequest(BaseModel):
    url: str
    analyze_all_history: bool = False  # Se False, analisa apenas últimos 50 commits


class RepositoryAnalysisResponse(BaseModel):
    repository_url: str
    repository_name: str
    total_commits: int
    analysis_status: str
    commits: List[CommitMetricResponse]
    
    class Config:
        from_attributes = True


class PerformanceReportResponse(BaseModel):
    repository_url: str
    total_commits_analyzed: int
    degradations_found: int
    ai_analysis: str
    commits_timeline: List[CommitMetricResponse]
    
    class Config:
        from_attributes = True


class ComparisonRequest(BaseModel):
    repository_url: str
    from_commit: str
    to_commit: str


class ComparisonResponse(BaseModel):
    from_commit: CommitMetricResponse
    to_commit: CommitMetricResponse
    complexity_change: float
    lines_added_change: int
    files_changed_count: int
    degradation_percentage: float

    class Config:
        from_attributes = True
