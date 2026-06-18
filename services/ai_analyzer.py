import json
import logging
from typing import Dict, List
from anthropic import Anthropic
from models.schemas import CommitMetricResponse

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Usa Claude para analisar padrões de performance e degradação"""

    def __init__(self, api_key: str):
        self.client = Anthropic()

    def analyze_performance_degradation(
        self,
        commits: List[Dict],
        repository_info: Dict
    ) -> Dict:
        """
        Analisa degradação de performance ao longo dos commits
        Retorna: análise textual + commits problemáticos identificados
        """
        try:
            # Prepara dados para a IA
            commits_summary = self._prepare_commits_summary(commits)
            
            prompt = f"""
Você é um especialista em análise de performance de código. Analise os seguintes dados de commits 
de um repositório e identifique:

1. **Períodos de degradação**: Quando a complexidade aumentou drasticamente
2. **Commits problemáticos**: Quais commits causaram piora na qualidade
3. **Tendências**: Está melhorando ou piorando?
4. **Recomendações**: O que fazer para melhorar

## Dados do Repositório
Nome: {repository_info.get('name', 'Unknown')}
URL: {repository_info.get('url', 'Unknown')}
Total de Commits: {len(commits)}

## Timeline de Commits (últimos 20)
{commits_summary}

Forneça uma análise estruturada e acionável. Seja direto e objetivo.
"""
            
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis_text = message.content[0].text
            
            # Identifica degradações
            degradation_points = self._identify_degradations(commits)
            
            return {
                "analysis": analysis_text,
                "degradation_points": degradation_points,
                "commits_count": len(commits),
                "average_complexity": sum(c.get("complexity", 0) for c in commits) / len(commits) if commits else 0
            }
        
        except Exception as e:
            logger.error(f"Erro na análise de IA: {e}")
            return {
                "analysis": f"Erro ao analisar: {str(e)}",
                "degradation_points": [],
                "commits_count": len(commits)
            }

    @staticmethod
    def _prepare_commits_summary(commits: List[Dict], limit: int = 20) -> str:
        """Prepara resumo dos commits para enviar à IA"""
        recent_commits = commits[-limit:] if len(commits) > limit else commits
        
        summary_lines = []
        for i, commit in enumerate(recent_commits, 1):
            line = (
                f"{i}. [{commit.get('sha', 'unknown')}] "
                f"Complexity: {commit.get('complexity', 0):.2f} | "
                f"Lines ±: +{commit.get('lines_added', 0)}/-{commit.get('lines_removed', 0)} | "
                f"Files: {commit.get('files_changed', 0)} | "
                f"{commit.get('message', 'No message')[:50]}"
            )
            summary_lines.append(line)
        
        return "\n".join(summary_lines)

    @staticmethod
    def _identify_degradations(commits: List[Dict], threshold_increase: float = 2.0) -> List[Dict]:
        """
        Identifica commits que causaram degradação de performance
        threshold_increase: quanto a complexidade precisa aumentar para considerar degradação
        """
        degradations = []
        
        if len(commits) < 2:
            return degradations
        
        for i in range(1, len(commits)):
            prev_commit = commits[i - 1]
            curr_commit = commits[i]
            
            prev_complexity = prev_commit.get("complexity", 0)
            curr_complexity = curr_commit.get("complexity", 0)
            
            # Verifica se houve degradação significativa
            if curr_complexity > 0 and prev_complexity > 0:
                increase_pct = ((curr_complexity - prev_complexity) / prev_complexity) * 100
                
                if increase_pct > threshold_increase:
                    degradations.append({
                        "commit_sha": curr_commit.get("sha"),
                        "commit_message": curr_commit.get("message"),
                        "from_complexity": prev_complexity,
                        "to_complexity": curr_complexity,
                        "increase_percentage": increase_pct,
                        "author": curr_commit.get("author")
                    })
        
        return degradations

    def compare_commits(self, commit1: Dict, commit2: Dict) -> str:
        """
        Compara dois commits e fornece análise de mudanças
        """
        try:
            prompt = f"""
Compare esses dois commits de código e analise as mudanças de performance:

## Commit 1 (Mais antigo)
- SHA: {commit1.get('sha')}
- Mensagem: {commit1.get('message')}
- Complexidade: {commit1.get('complexity', 0):.2f}
- Linhas adicionadas: {commit1.get('lines_added', 0)}
- Arquivos mudados: {commit1.get('files_changed', 0)}

## Commit 2 (Mais recente)
- SHA: {commit2.get('sha')}
- Mensagem: {commit2.get('message')}
- Complexidade: {commit2.get('complexity', 0):.2f}
- Linhas adicionadas: {commit2.get('lines_added', 0)}
- Arquivos mudados: {commit2.get('files_changed', 0)}

Forneça:
1. Resumo das mudanças
2. Impacto na performance
3. Recomendações de refatoração (se necessário)
"""
            
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=800,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"Erro ao comparar commits: {e}")
            return f"Erro: {str(e)}"
