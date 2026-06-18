import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DegradationType(str, Enum):
    """Tipos de degradação detectados"""
    COMPLEXITY_SPIKE = "complexity_spike"
    GRADUAL_INCREASE = "gradual_increase"
    FILE_EXPLOSION = "file_explosion"
    CODE_CHURN = "code_churn"
    MAINTENANCE_CRISIS = "maintenance_crisis"


@dataclass
class DegradationPoint:
    """Ponto de degradação identificado"""
    commit_index: int
    commit_sha: str
    commit_message: str
    degradation_type: DegradationType
    severity_score: float  # 0-100
    affected_metric: str
    before_value: float
    after_value: float
    percentage_change: float
    recommendation: str


@dataclass
class RepositoryHealth:
    """Score de saúde geral do repositório"""
    overall_score: float  # 0-100
    complexity_trend: str  # "improving", "stable", "declining"
    health_interpretation: str
    critical_issues: int
    warnings: int


class NonAIAnalyzer:
    """
    Análise de performance SEM IA
    Usa apenas estatística, detecção de anomalias e heurísticas
    """

    # Thresholds configuráveis
    COMPLEXITY_SPIKE_THRESHOLD = 1.5  # 50% de aumento = spike
    GRADUAL_INCREASE_WINDOW = 10  # Olhar últimos 10 commits
    GRADUAL_INCREASE_THRESHOLD = 0.2  # 20% de aumento gradual
    Z_SCORE_THRESHOLD = 2.0  # Desvios padrão da média
    MIN_COMMITS_FOR_ANALYSIS = 5

    @staticmethod
    def analyze_complexity_trend(commits: List[Dict]) -> Dict:
        """
        Analisa a TENDÊNCIA de complexidade
        Retorna: padrão, velocidade de mudança, etc
        """
        if len(commits) < NonAIAnalyzer.MIN_COMMITS_FOR_ANALYSIS:
            return {"status": "insufficient_data"}

        complexities = [c.get("complexity", 0) for c in commits]

        # Calcula estatísticas básicas
        avg_complexity = np.mean(complexities)
        std_complexity = np.std(complexities)
        min_complexity = np.min(complexities)
        max_complexity = np.max(complexities)

        # Calcula regressão linear (tendência)
        x = np.arange(len(complexities))
        z = np.polyfit(x, complexities, 1)
        slope = z[0]  # Inclinação da reta

        # Interpreta a tendência
        if slope < -0.01:
            trend = "improving"
        elif slope > 0.01:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "average": avg_complexity,
            "std_dev": std_complexity,
            "min": min_complexity,
            "max": max_complexity,
            "trend": trend,
            "trend_slope": slope,
            "coefficient_of_variation": (std_complexity / avg_complexity) if avg_complexity > 0 else 0,
        }

    @staticmethod
    def detect_anomalies_zscore(commits: List[Dict], metric: str = "complexity") -> List[Dict]:
        """
        Detecta ANOMALIAS usando Z-Score
        Valores com |z-score| > 2 são outliers
        """
        if len(commits) < 3:
            return []

        values = [c.get(metric, 0) for c in commits]
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:  # Todos os valores iguais
            return []

        anomalies = []
        for i, (commit, value) in enumerate(zip(commits, values)):
            z_score = abs((value - mean) / std)

            if z_score > NonAIAnalyzer.Z_SCORE_THRESHOLD:
                anomalies.append({
                    "commit_index": i,
                    "commit_sha": commit.get("sha"),
                    "metric": metric,
                    "value": value,
                    "expected_value": mean,
                    "z_score": z_score,
                    "severity": "critical" if z_score > 3 else "warning"
                })

        return anomalies

    @staticmethod
    def detect_complexity_spikes(commits: List[Dict]) -> List[DegradationPoint]:
        """
        Detecta PICOS REPENTINOS de complexidade
        Ex: commit anterior = 5, commit atual = 7.5 (50% aumento = spike)
        """
        spikes = []

        for i in range(1, len(commits)):
            prev_commit = commits[i - 1]
            curr_commit = commits[i]

            prev_complexity = prev_commit.get("complexity", 0)
            curr_complexity = curr_commit.get("complexity", 0)

            if prev_complexity == 0:
                continue

            # Calcula percentual de mudança
            pct_change = ((curr_complexity - prev_complexity) / prev_complexity) * 100

            # Se aumentou mais que o threshold, é um spike
            if pct_change > (NonAIAnalyzer.COMPLEXITY_SPIKE_THRESHOLD * 100):
                severity = min(100, pct_change / 2)  # Mapeia percentual para 0-100

                spikes.append(DegradationPoint(
                    commit_index=i,
                    commit_sha=curr_commit.get("sha"),
                    commit_message=curr_commit.get("message"),
                    degradation_type=DegradationType.COMPLEXITY_SPIKE,
                    severity_score=severity,
                    affected_metric="complexity",
                    before_value=prev_complexity,
                    after_value=curr_complexity,
                    percentage_change=pct_change,
                    recommendation=f"Refatore funções complexas. Considere quebrar em métodos menores."
                ))

        return spikes

    @staticmethod
    def detect_gradual_decline(commits: List[Dict]) -> List[DegradationPoint]:
        """
        Detecta DEGRADAÇÃO GRADUAL
        Ex: nos últimos 10 commits, complexidade aumentou 20% consistentemente
        """
        window = NonAIAnalyzer.GRADUAL_INCREASE_WINDOW
        degradations = []

        if len(commits) < window:
            return degradations

        for i in range(window, len(commits)):
            window_commits = commits[i - window:i + 1]
            complexities = [c.get("complexity", 0) for c in window_commits]

            # Calcula regressão linear desta janela
            x = np.arange(len(complexities))
            z = np.polyfit(x, complexities, 1)
            slope = z[0]

            first_complexity = complexities[0]
            last_complexity = complexities[-1]

            if first_complexity > 0:
                pct_change = ((last_complexity - first_complexity) / first_complexity) * 100

                # Se há aumento gradual consistente
                if slope > 0 and pct_change > (NonAIAnalyzer.GRADUAL_INCREASE_THRESHOLD * 100):
                    degradations.append(DegradationPoint(
                        commit_index=i,
                        commit_sha=commits[i].get("sha"),
                        commit_message=commits[i].get("message"),
                        degradation_type=DegradationType.GRADUAL_INCREASE,
                        severity_score=min(50, pct_change / 2),  # Max 50 points
                        affected_metric="complexity",
                        before_value=first_complexity,
                        after_value=last_complexity,
                        percentage_change=pct_change,
                        recommendation=f"Degradação gradual detectada. Refatore regularmente."
                    ))

        return degradations

    @staticmethod
    def detect_file_explosion(commits: List[Dict]) -> List[DegradationPoint]:
        """
        Detecta FILE EXPLOSION
        Quando muitos arquivos são modificados (possível refatoração confusa)
        """
        explosions = []
        files_changed = [c.get("files_changed", 0) for c in commits]

        # Calcula Z-score para número de arquivos
        if len(files_changed) > 2:
            mean_files = np.mean(files_changed)
            std_files = np.std(files_changed)

            if std_files > 0:
                for i, commit in enumerate(commits):
                    num_files = commit.get("files_changed", 0)
                    z_score = (num_files - mean_files) / std_files

                    if z_score > 2.5:  # Outlier significativo
                        explosions.append(DegradationPoint(
                            commit_index=i,
                            commit_sha=commit.get("sha"),
                            commit_message=commit.get("message"),
                            degradation_type=DegradationType.FILE_EXPLOSION,
                            severity_score=min(70, z_score * 20),
                            affected_metric="files_changed",
                            before_value=mean_files,
                            after_value=num_files,
                            percentage_change=((num_files - mean_files) / mean_files * 100) if mean_files > 0 else 0,
                            recommendation=f"Muitos arquivos alterados. Considere commits mais focados."
                        ))

        return explosions

    @staticmethod
    def detect_code_churn(commits: List[Dict]) -> List[DegradationPoint]:
        """
        Detecta CODE CHURN
        Quando há muito movimento de código sem resultado líquido
        Exemplo: +500 linhas, -400 linhas = muita remoção relativa
        """
        churn_issues = []

        for i in range(1, len(commits)):
            commit = commits[i]

            lines_added = commit.get("lines_added", 0)
            lines_removed = commit.get("lines_removed", 0)
            total_changed = lines_added + lines_removed

            if total_changed > 100:  # Só se foi uma mudança grande
                # Taxa de churn = linhas removidas / total de mudanças
                churn_rate = lines_removed / total_changed if total_changed > 0 else 0

                # Se removeu muitas linhas relativas, pode ser refatoração confusa
                if churn_rate > 0.6:  # 60% das mudanças foram remoções
                    churn_issues.append(DegradationPoint(
                        commit_index=i,
                        commit_sha=commit.get("sha"),
                        commit_message=commit.get("message"),
                        degradation_type=DegradationType.CODE_CHURN,
                        severity_score=min(60, churn_rate * 100),
                        affected_metric="code_churn",
                        before_value=churn_rate * 100,
                        after_value=churn_rate * 100,
                        percentage_change=0,
                        recommendation=f"Alto churn detectado ({churn_rate*100:.0f}%). Refatore de forma mais incremental."
                    ))

        return churn_issues

    @staticmethod
    def calculate_health_score(commits: List[Dict]) -> RepositoryHealth:
        """
        Calcula SCORE DE SAÚDE do repositório (0-100)
        """
        if len(commits) < NonAIAnalyzer.MIN_COMMITS_FOR_ANALYSIS:
            return RepositoryHealth(
                overall_score=50,
                complexity_trend="unknown",
                health_interpretation="Dados insuficientes para análise",
                critical_issues=0,
                warnings=0
            )

        # Coleta todas as degradações
        spikes = NonAIAnalyzer.detect_complexity_spikes(commits)
        gradual = NonAIAnalyzer.detect_gradual_decline(commits)
        explosions = NonAIAnalyzer.detect_file_explosion(commits)
        churn = NonAIAnalyzer.detect_code_churn(commits)

        all_degradations = spikes + gradual + explosions + churn

        # Conta issues
        critical_issues = sum(1 for d in all_degradations if d.severity_score > 70)
        warnings = len(all_degradations) - critical_issues

        # Calcula tendência
        trend_info = NonAIAnalyzer.analyze_complexity_trend(commits)
        trend = trend_info.get("trend", "stable")

        # Score = 100 - (severidade média ponderada)
        if all_degradations:
            avg_severity = np.mean([d.severity_score for d in all_degradations])
            score = max(0, 100 - avg_severity)
        else:
            score = 100

        # Ajusta por tendência
        if trend == "declining":
            score -= 15
        elif trend == "improving":
            score += 10

        score = max(0, min(100, score))

        # Interpretação
        if score >= 80:
            interpretation = "✅ Saúde Excelente"
        elif score >= 60:
            interpretation = "⚠️ Saúde Boa (alguns pontos de atenção)"
        elif score >= 40:
            interpretation = "⚠️ Saúde Fraca (degradação significativa)"
        else:
            interpretation = "🔴 Saúde Crítica (refatoração urgente)"

        return RepositoryHealth(
            overall_score=score,
            complexity_trend=trend,
            health_interpretation=interpretation,
            critical_issues=critical_issues,
            warnings=warnings
        )

    @staticmethod
    def generate_text_report(commits: List[Dict], repo_info: Dict) -> str:
        """
        Gera RELATÓRIO TEXTUAL (similar ao que IA geraria)
        Mas 100% baseado em algoritmos determinísticos
        """
        trend_info = NonAIAnalyzer.analyze_complexity_trend(commits)
        health = NonAIAnalyzer.calculate_health_score(commits)

        spikes = NonAIAnalyzer.detect_complexity_spikes(commits)
        gradual = NonAIAnalyzer.detect_gradual_decline(commits)
        explosions = NonAIAnalyzer.detect_file_explosion(commits)
        churn = NonAIAnalyzer.detect_code_churn(commits)

        all_degradations = spikes + gradual + explosions + churn
        all_degradations.sort(key=lambda x: x.severity_score, reverse=True)

        # Monta relatório
        report = f"""
═══════════════════════════════════════════════════════════════
RELATÓRIO DE ANÁLISE DE PERFORMANCE - {repo_info.get('name', 'Unknown')}
═══════════════════════════════════════════════════════════════

📊 RESUMO EXECUTIVO
───────────────────────────────────────────────────────────────
Saúde Geral: {health.overall_score:.1f}/100 {health.health_interpretation}
Tendência: {health.complexity_trend.upper()}
Total de Commits Analisados: {len(commits)}
Issues Críticos: {health.critical_issues}
Avisos: {health.warnings}

📈 ANÁLISE DE TENDÊNCIA
───────────────────────────────────────────────────────────────
Complexidade Média: {trend_info['average']:.2f}
Desvio Padrão: {trend_info['std_dev']:.2f}
Range: {trend_info['min']:.2f} - {trend_info['max']:.2f}
Coeficiente de Variação: {trend_info['coefficient_of_variation']:.2f}
Inclinação (Slope): {trend_info['trend_slope']:.4f}

Interpretação:
"""

        if trend_info['trend'] == 'improving':
            report += "✅ O código está ficando mais simples e fácil de manter.\n"
        elif trend_info['trend'] == 'declining':
            report += "⚠️ Atenção: A complexidade está aumentando. Refatoração recomendada.\n"
        else:
            report += "➡️ A complexidade permanece estável.\n"

        if all_degradations:
            report += f"""

🚨 PROBLEMAS DETECTADOS ({len(all_degradations)} total)
───────────────────────────────────────────────────────────────"""
            for i, deg in enumerate(all_degradations[:5], 1):  # Top 5
                report += f"""

{i}. [{deg.degradation_type.value.upper()}] 
   Commit: {deg.commit_sha}
   Mensagem: {deg.commit_message[:60]}...
   Severidade: {deg.severity_score:.1f}/100
   Mudança: {deg.before_value:.2f} → {deg.after_value:.2f} ({deg.percentage_change:+.1f}%)
   Recomendação: {deg.recommendation}"""

        report += """

📋 RECOMENDAÇÕES
───────────────────────────────────────────────────────────────"""

        if health.critical_issues > 0:
            report += "\n1. CRÍTICO: Refatore imediatamente as funções de maior complexidade."
            report += "\n   - Use extract method para reduzir linhas de funções longas"
            report += "\n   - Divida arquivos grandes em módulos menores"

        if trend_info['trend'] == 'declining':
            report += "\n2. TENDÊNCIA: Estabeleça code review para novas mudanças"
            report += "\n   - Limite complexity por função (máx ~10-15)"

        if len(explosions) > 2:
            report += "\n3. ESTRUTURA: Commits modificam muitos arquivos"
            report += "\n   - Pequenos commits = mais rastreáveis"
            report += "\n   - Agrupe mudanças relacionadas"

        report += """

═══════════════════════════════════════════════════════════════
Relatório gerado por análise estatística determinística.
Sem modelos de IA - 100% algoritmos puros.
═══════════════════════════════════════════════════════════════
"""
        return report
