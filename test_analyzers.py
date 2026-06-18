#!/usr/bin/env python3
"""
Script de Teste: Análise Estatística vs IA

Executa ambos os métodos e mostra comparação.
"""

from services.non_ai_analyzer import NonAIAnalyzer
from services.comparison_analyzer import AnalysisComparator
import json

# Dados de exemplo com problema real
SAMPLE_COMMITS = [
    # Fase 1: Código estável
    {
        "sha": "abc0001",
        "message": "Initial setup",
        "author": "John",
        "committed_date": "2024-01-01",
        "complexity": 3.0,
        "lines_added": 100,
        "lines_removed": 0,
        "files_changed": 5
    },
    {
        "sha": "abc0002",
        "message": "Add utils",
        "author": "John",
        "committed_date": "2024-01-02",
        "complexity": 3.1,
        "lines_added": 150,
        "lines_removed": 10,
        "files_changed": 3
    },
    {
        "sha": "abc0003",
        "message": "Add models",
        "author": "Jane",
        "committed_date": "2024-01-03",
        "complexity": 3.2,
        "lines_added": 200,
        "lines_removed": 5,
        "files_changed": 4
    },

    # Fase 2: Primeiro aumento
    {
        "sha": "abc0004",
        "message": "Add feature X",
        "author": "John",
        "committed_date": "2024-01-04",
        "complexity": 3.5,  # Pequeno aumento
        "lines_added": 180,
        "lines_removed": 20,
        "files_changed": 5
    },

    # Fase 3: SPIKE!
    {
        "sha": "abc0005",
        "message": "Big refactor (messy)",  # 🚨
        "author": "Bob",
        "committed_date": "2024-01-05",
        "complexity": 5.8,  # SPIKE! 65% aumento
        "lines_added": 50,
        "lines_removed": 300,  # Muito churn!
        "files_changed": 18  # 🚨 Muitos arquivos!
    },

    # Fase 4: Ainda degradado
    {
        "sha": "abc0006",
        "message": "Try to fix",
        "author": "John",
        "committed_date": "2024-01-06",
        "complexity": 5.5,
        "lines_added": 100,
        "lines_removed": 80,
        "files_changed": 6
    },

    # Fase 5: Continua piorando lentamente
    {
        "sha": "abc0007",
        "message": "Add more features",
        "author": "Jane",
        "committed_date": "2024-01-07",
        "complexity": 5.7,  # Degradação gradual
        "lines_added": 200,
        "lines_removed": 30,
        "files_changed": 7
    },
    {
        "sha": "abc0008",
        "message": "Quick fix",
        "author": "Bob",
        "committed_date": "2024-01-08",
        "complexity": 5.9,  # Piora continua...
        "lines_added": 120,
        "lines_removed": 40,
        "files_changed": 5
    },
    {
        "sha": "abc0009",
        "message": "Minor tweaks",
        "author": "John",
        "committed_date": "2024-01-09",
        "complexity": 6.1,
        "lines_added": 80,
        "lines_removed": 20,
        "files_changed": 3
    },
    {
        "sha": "abc0010",
        "message": "Polish",
        "author": "Jane",
        "committed_date": "2024-01-10",
        "complexity": 6.3,  # Continua subindo
        "lines_added": 90,
        "lines_removed": 15,
        "files_changed": 4
    },
]

REPO_INFO = {
    "name": "example-project",
    "url": "https://github.com/example/project.git"
}


def print_section(title: str):
    """Imprime separador de seção"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def test_statistical_analysis():
    """Testa apenas análise estatística (rápido)"""
    print_section("🧮 TESTE 1: ANÁLISE ESTATÍSTICA (SEM IA)")

    # Análise de complexidade
    print("📊 Analisando tendência...")
    trend = NonAIAnalyzer.analyze_complexity_trend(SAMPLE_COMMITS)
    print(f"  • Complexidade média: {trend['average']:.2f}")
    print(f"  • Desvio padrão: {trend['std_dev']:.2f}")
    print(f"  • Tendência: {trend['trend'].upper()}")
    print(f"  • Inclinação: {trend['trend_slope']:.4f} (aumenta por commit)")
    print(f"  • Coef. Variação: {trend['coefficient_of_variation']:.2f}")

    # Health score
    print("\n🏥 Calculando health score...")
    health = NonAIAnalyzer.calculate_health_score(SAMPLE_COMMITS)
    print(f"  • Score: {health.overall_score:.1f}/100")
    print(f"  • Interpretação: {health.health_interpretation}")
    print(f"  • Issues críticos: {health.critical_issues}")
    print(f"  • Avisos: {health.warnings}")

    # Detecta anomalias
    print("\n🚨 Detectando anomalias (Z-Score)...")
    anomalies = NonAIAnalyzer.detect_anomalies_zscore(SAMPLE_COMMITS, "complexity")
    for anom in anomalies:
        print(f"  • {anom['commit_sha']}: {anom['metric']} = {anom['value']:.2f} "
              f"(Z-score: {anom['z_score']:.2f}) - {anom['severity'].upper()}")

    # Detecta picos
    print("\n📈 Detectando picos de complexidade...")
    spikes = NonAIAnalyzer.detect_complexity_spikes(SAMPLE_COMMITS)
    for spike in spikes:
        print(f"  • {spike.commit_sha}: {spike.before_value:.2f} → {spike.after_value:.2f} "
              f"({spike.percentage_change:+.1f}%) - Severidade: {spike.severity_score:.0f}%")
        print(f"    Msg: {spike.commit_message}")
        print(f"    Rec: {spike.recommendation}")

    # Detecta degradação gradual
    print("\n📉 Detectando degradação gradual...")
    gradual = NonAIAnalyzer.detect_gradual_decline(SAMPLE_COMMITS)
    if gradual:
        for deg in gradual:
            print(f"  • Commits {deg.commit_index-9}..{deg.commit_index}: "
                  f"aumento de {deg.percentage_change:+.1f}%")
    else:
        print("  (Nenhuma degradação gradual detectada nesta janela)")

    # Detecta explosão de arquivos
    print("\n💥 Detectando explosão de arquivos...")
    explosions = NonAIAnalyzer.detect_file_explosion(SAMPLE_COMMITS)
    for exp in explosions:
        print(f"  • {exp.commit_sha}: {exp.after_value:.0f} arquivos "
              f"(média: {exp.before_value:.0f})")

    # Detecta code churn
    print("\n🔄 Detectando code churn...")
    churns = NonAIAnalyzer.detect_code_churn(SAMPLE_COMMITS)
    for churn in churns:
        print(f"  • {churn.commit_sha}: {churn.percentage_change:.0f}% churn")

    # Gera relatório textual
    print("\n📄 Gerando relatório textual...")
    report = NonAIAnalyzer.generate_text_report(SAMPLE_COMMITS, REPO_INFO)
    print(report)


def test_comparison():
    """Compara análise estatística com IA (se disponível)"""
    print_section("🔬 TESTE 2: COMPARAÇÃO ESTATÍSTICO vs IA")

    results = AnalysisComparator.analyze_repository(
        commits=SAMPLE_COMMITS,
        repo_info=REPO_INFO,
        use_ai=False,  # Mude para True se quiser testar com IA
        use_stats=True
    )

    AnalysisComparator.print_comparison_report(results)


def test_custom_thresholds():
    """Testa com thresholds diferentes"""
    print_section("⚙️ TESTE 3: IMPACTO DOS THRESHOLDS")

    print("Testando diferentes thresholds para detecção de picos...\n")

    # Threshold padrão
    thresholds = [1.2, 1.5, 2.0, 3.0]

    for threshold in thresholds:
        # Simula mudança de threshold
        spikes = []
        for i in range(1, len(SAMPLE_COMMITS)):
            prev = SAMPLE_COMMITS[i - 1].get("complexity", 0)
            curr = SAMPLE_COMMITS[i].get("complexity", 0)

            if prev > 0:
                increase = curr / prev
                if increase > threshold:
                    spikes.append({
                        "sha": SAMPLE_COMMITS[i]["sha"],
                        "increase_multiplier": increase
                    })

        print(f"Threshold: {threshold}x (aumento de {(threshold-1)*100:.0f}%)")
        print(f"  Picos detectados: {len(spikes)}")
        for spike in spikes:
            print(f"    - {spike['sha']}: {spike['increase_multiplier']:.2f}x")
        print()


def main():
    """Função principal"""
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "CODE PERFORMANCE ANALYZER - TESTES DE ANÁLISE".center(78) + "║")
    print("║" + "Estatístico vs IA".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")

    # Teste 1: Análise estatística
    test_statistical_analysis()

    # Teste 2: Comparação
    test_comparison()

    # Teste 3: Thresholds
    test_custom_thresholds()

    print_section("✅ TESTES CONCLUÍDOS")
    print("""
Resumo:
  ✅ Análise estatística: Implementada
  ✅ Detecção de anomalias: Funcional
  ✅ Comparação com IA: Pronta para integração

Próximos passos:
  1. Integrar ao FastAPI (routers/analysis.py)
  2. Adicionar endpoint /api/v1/analyze-stats
  3. Testar com repositórios reais
  4. Comparar resultados com e sem IA
    """)


if __name__ == "__main__":
    main()
