from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commits = relationship("CommitMetric", back_populates="repository", cascade="all, delete-orphan")
    analyses = relationship("PerformanceAnalysis", back_populates="repository", cascade="all, delete-orphan")


class CommitMetric(Base):
    __tablename__ = "commit_metrics"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), index=True)
    sha = Column(String, index=True)
    message = Column(String)
    author = Column(String)
    committed_date = Column(DateTime, index=True)
    
    # Métricas
    complexity = Column(Float)  # Complexidade ciclomática média
    lines_added = Column(Integer)
    lines_removed = Column(Integer)
    files_changed = Column(Integer)
    avg_method_length = Column(Float)
    
    # Status da análise
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("Repository", back_populates="commits")


class PerformanceAnalysis(Base):
    __tablename__ = "performance_analyses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), index=True)
    
    # Análise
    analysis_text = Column(Text)  # Resultado da IA
    degradation_detected = Column(Integer, default=0)  # Número de degradações encontradas
    total_commits_analyzed = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("Repository", back_populates="analyses")
