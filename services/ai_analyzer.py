import logging
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Usa o Groq para analisar padrões de performance e degradação."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def analyze_performance_degradation(
        self,
        commits: List[Dict],
        repository_info: Dict,
        use_top_commits: int = 20
    ) -> Dict:
        """
        Analisa degradação de performance ao longo dos commits.
        Retorna: análise textual + commits problemáticos identificados.
        """
        try:
            if not commits:
                return {
                    "analysis": "Nenhum commit disponível para análise.",
                    "degradation_points": [],
                    "commits_count": 0,
                    "average_complexity": 0
                }

            filtered_commits = commits
            commits_summary = self._prepare_commits_summary(filtered_commits)

            prompt = f"""
Você é um especialista em engenharia de software e análise de performance.
Considere todos os commits disponíveis e descreva o que eles mostram sobre a saúde do código.

Seu objetivo é fornecer:
1. Uma visão clara dos maiores riscos de regressão e degradação.
2. Quais commits ou padrões parecem mais problemáticos.
3. Quais tendências importantes aparecem nesses dados.
4. Ações práticas e priorizadas para refatoração/improvação.

Importante: não repita a análise estatística simples. Use os dados para produzir insights adicionais, recomendações e uma narrativa focada em ação.

## Dados do Repositório
Nome: {repository_info.get('name', 'Unknown')}
URL: {repository_info.get('url', 'Unknown')}
Total de Commits no Repositório: {len(commits)}
Commits analisados pela IA: {len(filtered_commits)}

## Commits Analisados
{commits_summary}

Forneça sua resposta em seções claras:
- Principais riscos
- O que está piorando
- Recomendações imediatas
- Justificativa
"""

            analysis_text = self._call_groq(prompt, max_tokens=1500)
            degradation_points = self._identify_degradations(filtered_commits)

            return {
                "analysis": analysis_text,
                "degradation_points": degradation_points,
                "commits_count": len(filtered_commits),
                "average_complexity": sum(c.get("complexity", 0) for c in filtered_commits) / len(filtered_commits) if filtered_commits else 0,
                "selected_commits": filtered_commits
            }

        except Exception as e:
            logger.error(f"Erro na análise de IA: {e}")
            return {
                "analysis": f"Erro ao analisar: {str(e)}",
                "degradation_points": [],
                "commits_count": len(commits)
            }

    def _call_groq(self, prompt: str, max_tokens: int = 1500) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY não configurada")

        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() if isinstance(content, str) else str(content)

    @staticmethod
    def _prepare_commits_summary(commits: List[Dict], limit: int = None) -> str:
        """Prepara resumo dos commits para enviar à IA."""
        summary_commits = commits if limit is None else (commits[:limit] if len(commits) > limit else commits)

        summary_lines = []
        for i, commit in enumerate(summary_commits, 1):
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
    def _select_top_commits_for_ai(commits: List[Dict], top_n: int = 20) -> List[Dict]:
        """Seleciona os commits mais relevantes para enviar à IA."""
        def score_commit(commit: Dict, recency_factor: float) -> float:
            complexity = commit.get("complexity", 0)
            files_changed = commit.get("files_changed", 0)
            lines_added = commit.get("lines_added", 0)
            lines_removed = commit.get("lines_removed", 0)

            return (
                complexity * 2
                + files_changed * 1.5
                + lines_added * 0.5
                + lines_removed * 0.5
                + recency_factor
            )

        total_commits = len(commits)
        scored = []
        for idx, commit in enumerate(commits):
            recency_factor = (idx + 1) / total_commits * 5.0
            scored.append((score_commit(commit, recency_factor), commit))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [commit for _, commit in scored[:top_n]]

    @staticmethod
    def _identify_degradations(commits: List[Dict], threshold_increase: float = 2.0) -> List[Dict]:
        """
        Identifica commits que causaram degradação de performance.
        threshold_increase: quanto a complexidade precisa aumentar para considerar degradação.
        """
        degradations = []

        if len(commits) < 2:
            return degradations

        for i in range(1, len(commits)):
            prev_commit = commits[i - 1]
            curr_commit = commits[i]

            prev_complexity = prev_commit.get("complexity", 0)
            curr_complexity = curr_commit.get("complexity", 0)

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
        """Compara dois commits e fornece análise de mudanças."""
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

            return self._call_groq(prompt, max_tokens=800)

        except Exception as e:
            logger.error(f"Erro ao comparar commits: {e}")
            return f"Erro: {str(e)}"
