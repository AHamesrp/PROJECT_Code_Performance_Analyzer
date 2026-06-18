import os
from pathlib import Path
from typing import Dict, List, Tuple
from radon.complexity import cc_visit
from radon.metrics import mi_visit, mi_parameters
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calcula métricas de complexidade e qualidade de código"""

    # Extensões Python
    PYTHON_EXTENSIONS = [".py"]
    JS_EXTENSIONS = [".js", ".ts", ".jsx", ".tsx"]
    JAVA_EXTENSIONS = [".java"]

    @staticmethod
    def calculate_complexity(repo_path: str) -> Tuple[float, Dict]:
        """
        Calcula complexidade ciclomática média do repositório
        Retorna: (complexidade_média, detalhes)
        """
        try:
            complexities = []
            file_complexities = {}
            
            repo_path = Path(repo_path)
            
            # Analisa apenas arquivos Python (compatível com Radon)
            for py_file in repo_path.rglob("*.py"):
                # Ignora venv, __pycache__, etc
                if any(part in py_file.parts for part in ["venv", "__pycache__", ".git", "node_modules"]):
                    continue
                
                try:
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    
                    # Calcula complexidade
                    results = cc_visit(code)
                    
                    if results:
                        file_cc = sum(r.complexity for r in results) / len(results)
                        complexities.append(file_cc)
                        file_complexities[str(py_file.relative_to(repo_path))] = file_cc
                
                except Exception as e:
                    logger.warning(f"Erro ao analisar {py_file}: {e}")
                    continue
            
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0.0
            
            return avg_complexity, {
                "average": avg_complexity,
                "files_analyzed": len(file_complexities),
                "highest_complexity_files": sorted(
                    file_complexities.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }
        
        except Exception as e:
            logger.error(f"Erro ao calcular complexidade: {e}")
            return 0.0, {"error": str(e)}

    @staticmethod
    def calculate_maintainability_index(repo_path: str) -> Tuple[float, Dict]:
        """
        Calcula Maintainability Index (MI)
        Escala: 0-100 (100 = mais fácil de manter)
        """
        try:
            mi_values = []
            
            repo_path = Path(repo_path)
            
            for py_file in repo_path.rglob("*.py"):
                if any(part in py_file.parts for part in ["venv", "__pycache__", ".git", "node_modules"]):
                    continue
                
                try:
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    
                    mi = mi_visit(code, multi=True)
                    if isinstance(mi, float):
                        mi_values.append(mi)
                
                except Exception as e:
                    logger.warning(f"Erro ao calcular MI em {py_file}: {e}")
                    continue
            
            avg_mi = sum(mi_values) / len(mi_values) if mi_values else 0.0
            
            return avg_mi, {
                "average_mi": avg_mi,
                "files_analyzed": len(mi_values),
                "interpretation": MetricsCalculator._interpret_mi(avg_mi)
            }
        
        except Exception as e:
            logger.error(f"Erro ao calcular MI: {e}")
            return 0.0, {"error": str(e)}

    @staticmethod
    def _interpret_mi(mi_value: float) -> str:
        """Interpreta o Maintainability Index"""
        if mi_value >= 85:
            return "Very High Maintainability"
        elif mi_value >= 70:
            return "High Maintainability"
        elif mi_value >= 55:
            return "Moderate Maintainability"
        elif mi_value >= 40:
            return "Low Maintainability"
        else:
            return "Very Low Maintainability"

    @staticmethod
    def count_lines_of_code(repo_path: str, extensions: List[str] = None) -> Dict:
        """Conta linhas de código por tipo de arquivo"""
        if extensions is None:
            extensions = MetricsCalculator.PYTHON_EXTENSIONS
        
        stats = {}
        
        try:
            repo_path = Path(repo_path)
            
            for ext in extensions:
                total_lines = 0
                total_files = 0
                blank_lines = 0
                comment_lines = 0
                
                for file_path in repo_path.rglob(f"*{ext}"):
                    if any(part in file_path.parts for part in ["venv", "__pycache__", ".git", "node_modules"]):
                        continue
                    
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for line in f:
                                total_lines += 1
                                stripped = line.strip()
                                if not stripped:
                                    blank_lines += 1
                                elif stripped.startswith("#"):
                                    comment_lines += 1
                        
                        total_files += 1
                    except Exception as e:
                        logger.warning(f"Erro ao contar linhas em {file_path}: {e}")
                        continue
                
                if total_files > 0:
                    stats[ext] = {
                        "files": total_files,
                        "total_lines": total_lines,
                        "blank_lines": blank_lines,
                        "comment_lines": comment_lines,
                        "code_lines": total_lines - blank_lines - comment_lines,
                    }
            
            return stats
        
        except Exception as e:
            logger.error(f"Erro ao contar LOC: {e}")
            return {}

    @staticmethod
    def analyze_full_repository(repo_path: str) -> Dict:
        """Análise completa do repositório"""
        try:
            complexity, complexity_details = MetricsCalculator.calculate_complexity(repo_path)
            mi, mi_details = MetricsCalculator.calculate_maintainability_index(repo_path)
            loc = MetricsCalculator.count_lines_of_code(repo_path)
            
            return {
                "complexity": {
                    "average": complexity,
                    "details": complexity_details
                },
                "maintainability_index": {
                    "average": mi,
                    "details": mi_details
                },
                "lines_of_code": loc,
                "health_score": MetricsCalculator._calculate_health_score(complexity, mi)
            }
        
        except Exception as e:
            logger.error(f"Erro na análise completa: {e}")
            return {}

    @staticmethod
    def _calculate_health_score(complexity: float, mi: float) -> float:
        """Calcula score geral de saúde (0-100)"""
        # Peso 40% para MI, 60% para complexidade
        mi_score = (mi / 100) * 100 if mi <= 100 else 100
        complexity_score = max(0, 100 - (complexity * 5))  # Cada ponto de complexidade = -5 pontos
        
        return (mi_score * 0.4) + (complexity_score * 0.6)
