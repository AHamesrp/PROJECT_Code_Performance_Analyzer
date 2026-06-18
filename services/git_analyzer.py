import os
import tempfile
import shutil
from pathlib import Path
from git import Repo
from git.exc import GitCommandError
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """Analisa repositórios Git e extrai informações de commits"""

    def __init__(self, temp_dir: str = "/tmp/git_repos"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, repo_url: str) -> Repo:
        """Clona um repositório GitHub"""
        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_path = self.temp_dir / repo_name
            
            # Remove se já existe
            if repo_path.exists():
                shutil.rmtree(repo_path)
            
            logger.info(f"Clonando {repo_url}...")
            repo = Repo.clone_from(repo_url, to_path=str(repo_path))
            logger.info(f"Repositório clonado em {repo_path}")
            
            return repo
        except GitCommandError as e:
            logger.error(f"Erro ao clonar: {e}")
            raise

    def get_commits_with_files(self, repo: Repo, limit: int = 50) -> List[Dict]:
        """Extrai informações de commits com detalhes de arquivos"""
        commits_data = []
        
        try:
            commits = list(repo.iter_commits())[:limit]
            total = len(commits)
            
            logger.info(f"Processando {total} commits...")
            
            for idx, commit in enumerate(commits):
                try:
                    # Arquivos modificados
                    files_changed = 0
                    lines_added = 0
                    lines_removed = 0
                    
                    if commit.parents:
                        parent = commit.parents[0]
                        diff = parent.diff(commit)
                        
                        for item in diff:
                            files_changed += 1
                            # Estatísticas de diff
                            if item.diff:
                                diff_text = item.diff.decode('utf-8', errors='ignore')
                                lines_added += diff_text.count('\n+')
                                lines_removed += diff_text.count('\n-')
                    
                    commit_data = {
                        "sha": commit.hexsha[:8],  # SHA curto
                        "full_sha": commit.hexsha,
                        "message": commit.message.strip()[:100],
                        "author": commit.author.name,
                        "committed_date": commit.committed_datetime,
                        "files_changed": files_changed,
                        "lines_added": lines_added,
                        "lines_removed": lines_removed,
                    }
                    
                    commits_data.append(commit_data)
                    
                    if (idx + 1) % 10 == 0:
                        logger.info(f"Processados {idx + 1}/{total} commits")
                
                except Exception as e:
                    logger.warning(f"Erro processando commit {commit.hexsha}: {e}")
                    continue
            
            # Inverte para ordem cronológica (mais antigo primeiro)
            commits_data.reverse()
            return commits_data
        
        except Exception as e:
            logger.error(f"Erro ao processar commits: {e}")
            raise

    def get_files_by_type(self, repo: Repo, extensions: List[str] = None) -> Dict[str, int]:
        """Conta arquivos por tipo"""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs"]
        
        file_counts = {}
        
        try:
            for item in repo.tree().traverse():
                if item.type == "blob":
                    ext = Path(item.path).suffix
                    if ext in extensions:
                        file_counts[ext] = file_counts.get(ext, 0) + 1
            
            return file_counts
        except Exception as e:
            logger.error(f"Erro ao contar arquivos: {e}")
            return {}

    def get_repository_info(self, repo: Repo) -> Dict:
        """Extrai informações gerais do repositório"""
        try:
            return {
                "name": repo.remotes.origin.url.split("/")[-1].replace(".git", ""),
                "url": repo.remotes.origin.url,
                "branches": len(repo.remotes.origin.refs),
                "total_commits": len(list(repo.iter_commits())),
                "languages": self.get_files_by_type(repo),
            }
        except Exception as e:
            logger.error(f"Erro ao extrair info do repo: {e}")
            return {}

    def cleanup(self, repo_path: str = None):
        """Remove repositório clonado"""
        try:
            if repo_path and Path(repo_path).exists():
                shutil.rmtree(repo_path)
                logger.info(f"Limpeza concluída: {repo_path}")
        except Exception as e:
            logger.warning(f"Erro ao limpar: {e}")
