"""
Comparador: Análise COM IA vs SEM IA

Este script demonstra as diferenças:
- SEM IA: Determinístico, reproduzível, rápido, baseado em estatística
- COM IA: Contextual, gerador de insights, mais lento, pode ser inconsistente
"""

import json
from typing import Dict, List
from services.non_ai_analyzer import NonAIAnalyzer, DegradationType
from services.ai_analyzer import AIAnalyzer
from config import settings


class AnalysisComparator:
    """Compara análises com e sem IA"""

    @staticmethod
    def analyze_repository(
        commits: List[Dict],
        repo_info: Dict,
        use_ai: bool = True,
        use_stats: bool = True
    ) -> Dict:
        """
        Realiza análise completa do repositório
        Retorna resultados de ambas as abordagens
        """

        results = {
            "repository": repo_info,
            "commits_analyzed": len(commits),
            "methods": {}
        }

        # MÉTODO 1: Análise Estatística (SEM IA)
        if use_stats:
            print("📊 Executando análise estatística...")
            results["methods"]["statistical"] = AnalysisComparator._statistical_analysis(commits)

        # MÉTODO 2: Análise com IA
        if use_ai and settings.ANTHROPIC_API_KEY:
            print("🤖 Executando análise com IA...")
            ai_analyzer = AIAnalyzer(settings.ANTHROPIC_API_KEY)
            results["methods"]["ai"] = AnalysisComparator._ai_analysis(
                commits,
                repo_info,
                ai_analyzer
            )

        # COMPARAÇÃO
        results["comparison"] = AnalysisComparator._compare_methods(results["methods"])

        return results

    @staticmethod
    def _statistical_analysis(commits: List[Dict]) -> Dict:
        """Análise puramente estatística"""
        try:
            health = NonAIAnalyzer.calculate_health_score(commits)
            spikes = NonAIAnalyzer.detect_complexity_spikes(commits)
            gradual = NonAIAnalyzer.detect_gradual_decline(commits)
            explosions = NonAIAnalyzer.detect_file_explosion(commits)
            churn = NonAIAnalyzer.detect_code_churn(commits)
            trend = NonAIAnalyzer.analyze_complexity_trend(commits)
            report = NonAIAnalyzer.generate_text_report(commits, {})

            return {
                "method": "Statistical Analysis (No AI)",
                "health_score": health.overall_score,
                "health_interpretation": health.health_interpretation,
                "trend": health.complexity_trend,
                "statistics": trend,
                "issues": {
                    "complexity_spikes": len(spikes),
                    "gradual_decline": len(gradual),
                    "file_explosion": len(explosions),
                    "code_churn": len(churn),
                    "total_issues": len(spikes) + len(gradual) + len(explosions) + len(churn)
                },
                "top_issues": [
                    {
                        "type": spike.degradation_type.value,
                        "sha": spike.commit_sha,
                        "severity": spike.severity_score,
                        "change": f"{spike.percentage_change:+.1f}%"
                    }
                    for spike in (spikes + gradual + explosions + churn)[:5]
                ],
                "report": report,
                "characteristics": {
                    "deterministic": True,
                    "repeatable": True,
                    "fast": True,
                    "explainable": True,
                    "context_aware": False
                }
            }

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _ai_analysis(
        commits: List[Dict],
        repo_info: Dict,
        ai_analyzer: AIAnalyzer
    ) -> Dict:
        """Análise com IA"""
        try:
            analysis = ai_analyzer.analyze_performance_degradation(commits, repo_info)

            return {
                "method": "AI Analysis (Claude)",
                "analysis_text": analysis.get("analysis", ""),
                "degradation_points": analysis.get("degradation_points", []),
                "total_degradations": len(analysis.get("degradation_points", [])),
                "characteristics": {
                    "deterministic": False,
                    "repeatable": False,
                    "fast": False,
                    "explainable": True,
                    "context_aware": True
                }
            }

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _compare_methods(methods: Dict) -> Dict:
        """Compara os resultados de ambos os métodos"""

        comparison = {
            "summary": "Comparação entre Análise Estatística vs IA",
            "details": {}
        }

        if "statistical" in methods and "ai" in methods:
            stats_method = methods["statistical"]
            ai_method = methods["ai"]

            comparison["details"] = {
                "health_score_statistical": stats_method.get("health_score", "N/A"),
                "issues_found_statistical": stats_method.get("issues", {}).get("total_issues", 0),
                "issues_found_ai": ai_method.get("total_degradations", 0),
                "speed": "Statistical ⚡ >> AI 🐌",
                "explainability": "Statistical 100% > AI ~80%",
                "context_awareness": "Statistical 0% < AI 100%"
            }

        return comparison

    @staticmethod
    def print_comparison_report(results: Dict):
        """Imprime relatório formatado"""

        print("\n" + "="*80)
        print("COMPARAÇÃO: ANÁLISE ESTATÍSTICA vs IA")
        print("="*80)

        print(f"\n📁 Repositório: {results['repository'].get('name', 'Unknown')}")
        print(f"📊 Commits analisados: {results['commits_analyzed']}")

        if "statistical" in results["methods"]:
            stats = results["methods"]["statistical"]
            print("\n" + "-"*80)
            print("📈 MÉTODO 1: ANÁLISE ESTATÍSTICA (SEM IA)")
            print("-"*80)
            print(f"Saúde Geral: {stats.get('health_score', 'N/A'):.1f}/100")
            print(f"Interpretação: {stats.get('health_interpretation', 'N/A')}")
            print(f"Tendência: {stats.get('trend', 'N/A').upper()}")
            print(f"\nProblemas Detectados:")
            issues = stats.get("issues", {})
            print(f"  • Picos de complexidade: {issues.get('complexity_spikes', 0)}")
            print(f"  • Degradação gradual: {issues.get('gradual_decline', 0)}")
            print(f"  • Explosão de arquivos: {issues.get('file_explosion', 0)}")
            print(f"  • Code churn: {issues.get('code_churn', 0)}")
            print(f"  • TOTAL: {issues.get('total_issues', 0)}")

            print("\nTop 3 Issues:")
            for issue in stats.get("top_issues", [])[:3]:
                print(f"  {issue['type']}: {issue['sha']} (Severidade: {issue['severity']:.0f}%)")

            print("\nCaracterísticas:")
            chars = stats.get("characteristics", {})
            for k, v in chars.items():
                emoji = "✅" if v else "❌"
                print(f"  {emoji} {k.replace('_', ' ').title()}: {v}")

        if "ai" in results["methods"]:
            ai = results["methods"]["ai"]
            print("\n" + "-"*80)
            print("🤖 MÉTODO 2: ANÁLISE COM IA (CLAUDE)")
            print("-"*80)
            print(f"Degradações encontradas: {ai.get('total_degradations', 0)}")
            print(f"\nAnálise IA:")
            print(ai.get("analysis_text", "N/A")[:500] + "...")

            print("\nCaracterísticas:")
            chars = ai.get("characteristics", {})
            for k, v in chars.items():
                emoji = "✅" if v else "❌"
                print(f"  {emoji} {k.replace('_', ' ').title()}: {v}")

        print("\n" + "="*80)
        print("RESUMO COMPARATIVO")
        print("="*80)

        comp = results.get("comparison", {})
        details = comp.get("details", {})

        if details:
            print(f"\n📊 Health Score (Estatístico): {details.get('health_score_statistical', 'N/A'):.1f}/100")
            print(f"🔍 Issues (Estatístico): {details.get('issues_found_statistical', 0)}")
            print(f"🔍 Issues (IA): {details.get('issues_found_ai', 0)}")
            print(f"\n⚡ Velocidade: {details.get('speed', 'N/A')}")
            print(f"📝 Explicabilidade: {details.get('explainability', 'N/A')}")
            print(f"🧠 Context-awareness: {details.get('context_awareness', 'N/A')}")

        print("\n" + "="*80)
        print("\n💡 INSIGHTS:")
        print("""
┌─────────────────────────────────────────────────────────────────┐
│ QUANDO USAR CADA MÉTODO:                                        │
├─────────────────────────────────────────────────────────────────┤
│ ✅ USE ESTATÍSTICO quando:                                     │
│   • Precisa de velocidade (ms vs segundos)                      │
│   • Quer resultados reproduzíveis 100%                          │
│   • Precisa explicar EXATAMENTE por quê detectou algo          │
│   • Não tem API key de IA disponível                            │
│   • Quer algo lightweight/sem dependências externas             │
│                                                                 │
│ ✅ USE IA quando:                                              │
│   • Quer insights contextuais de um especialista               │
│   • Precisa de linguagem natural/recomendações específicas      │
│   • Tem tempo (leva alguns segundos)                           │
│   • Quer análise mais "humana"                                 │
│   • Precisa explicar para stakeholders não-técnicos            │
│                                                                 │
│ 🎯 USE AMBAS (HÍBRIDO):                                        │
│   • Estadístico para detecção rápida                           │
│   • IA para gerar relatório executivo                          │
│   • Combine velocidade + contexto                              │
└─────────────────────────────────────────────────────────────────┘
""")

        print("\n")


# Script de teste
if __name__ == "__main__":
    # Dados de exemplo para teste
    sample_commits = [
        {
            "sha": "abc123",
            "message": "Initial commit",
            "author": "Dev",
            "committed_date": "2024-01-01",
            "complexity": 3.0,
            "lines_added": 100,
            "lines_removed": 0,
            "files_changed": 5
        },
        {
            "sha": "def456",
            "message": "Add feature A",
            "author": "Dev",
            "committed_date": "2024-01-05",
            "complexity": 3.2,
            "lines_added": 200,
            "lines_removed": 10,
            "files_changed": 3
        },
        {
            "sha": "ghi789",
            "message": "Big refactor (BUG)",
            "author": "Dev",
            "committed_date": "2024-01-10",
            "complexity": 5.5,  # SPIKE!
            "lines_added": 50,
            "lines_removed": 400,
            "files_changed": 12  # MUITOS ARQUIVOS!
        },
        {
            "sha": "jkl012",
            "message": "Fix complexity",
            "author": "Dev",
            "committed_date": "2024-01-15",
            "complexity": 4.8,
            "lines_added": 80,
            "lines_removed": 150,
            "files_changed": 4
        },
    ]

    sample_repo = {
        "name": "example-repo",
        "url": "https://github.com/example/repo"
    }

    # Executa comparação
    results = AnalysisComparator.analyze_repository(
        commits=sample_commits,
        repo_info=sample_repo,
        use_ai=False,  # Mude para True se quiser testar com IA
        use_stats=True
    )

    # Imprime relatório
    AnalysisComparator.print_comparison_report(results)
