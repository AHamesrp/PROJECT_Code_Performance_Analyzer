# Análise de Performance SEM IA 📊

## Resumo Executivo

O arquivo `services/non_ai_analyzer.py` implementa **análise estatística pura** para detectar degradação de performance em repositórios Git **sem usar nenhuma IA**.

Todos os insights são gerados através de:
- ✅ Estatística descritiva
- ✅ Detecção de anomalias  
- ✅ Análise de série temporal
- ✅ Heurísticas determinísticas

---

## 🔍 Técnicas Utilizadas

### 1️⃣ **Z-Score (Detecção de Outliers)**

```python
z_score = (valor - média) / desvio_padrão

Se |z_score| > 2.0 → É uma anomalia
```

**Exemplo prático:**
```
Complexidade histórica: [3.0, 3.2, 3.1, 3.3, 7.5]
                                            ↑ anomalia!

Média = 3.82
Desvio padrão = 1.71
Z-score do 7.5 = (7.5 - 3.82) / 1.71 = 2.15 ✅ anomalia!
```

**Uso no código:**
```python
anomalies = NonAIAnalyzer.detect_anomalies_zscore(
    commits,
    metric="complexity"
)
```

**Vantagens:**
- ✅ Matematicamente provado
- ✅ Detecta valores realmente anormais
- ✅ Rápido O(n)
- ✅ Reproduzível 100%

---

### 2️⃣ **Regressão Linear (Tendência)**

```python
# Ajusta uma linha aos dados
# y = slope * x + intercept

slope > 0 → Tendência PIORANDO
slope < 0 → Tendência MELHORANDO
slope ≈ 0 → Tendência ESTÁVEL
```

**Exemplo visual:**
```
Complexidade ao longo do tempo:
│     /
│    /  ← slope positivo = degradação
│   /
│  *
└──────────
```

**Código:**
```python
x = np.arange(len(complexities))
z = np.polyfit(x, complexities, 1)
slope = z[0]  # Primeiro coeficiente

if slope > 0.01:
    trend = "declining"
```

**Por que funciona:**
- Mostra se está melhorando ou piorando
- Calcula **velocidade** de mudança
- Ignora ruído (valores esporádicos)

---

### 3️⃣ **Detecção de Picos (Spike Detection)**

```python
pct_change = ((nova_valor - valor_anterior) / valor_anterior) * 100

Se pct_change > threshold (ex: 50%) → É um spike!
```

**Exemplo:**
```
Commit 1: complexidade = 5.0
Commit 2: complexidade = 7.5
Mudança = (7.5 - 5.0) / 5.0 * 100 = 50%

⚠️ SPIKE! Aumentou 50% em um commit!
```

**Implementação:**
```python
def detect_complexity_spikes(commits: List[Dict]) -> List[DegradationPoint]:
    spikes = []
    
    for i in range(1, len(commits)):
        prev = commits[i - 1].get("complexity", 0)
        curr = commits[i].get("complexity", 0)
        
        pct_change = ((curr - prev) / prev) * 100
        
        if pct_change > 50:  # threshold
            spikes.append(...)
    
    return spikes
```

---

### 4️⃣ **Detecção de Degradação Gradual**

```python
Olhar janela móvel (ex: últimos 10 commits)
Calcular regressão linear DESSA janela
Se slope > 0 consistentemente → degradação gradual
```

**Exemplo:**
```
Commits 1-10: [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9]
              └─ slope = +0.1 por commit
              
Commits 11-20: [4.0, 4.1, 4.2, ...]
               └ slope = +0.1 continua!

Problema: Está piorando de forma constante!
```

**Por que é importante:**
- Um spike é fácil de ver
- Mas degradação LENTA é insidiosa
- 1% por commit × 100 commits = 100% de piora!

---

### 5️⃣ **File Explosion Detection**

```python
Conta quantos arquivos foram alterados
Se está muito acima da média → é explosão
```

**Lógica:**
```
Histórico de arquivos alterados: [2, 3, 4, 3, 2, 25, 3, 2]
                                           ↑ outlier!

Um commit que toca 25 arquivos quando o normal é 3?
→ Possível refatoração confusa ou merge conflituoso
```

**Implementação:**
```python
# Calcula Z-score do número de arquivos
z_score = (num_files - media) / desvio_padrao

if z_score > 2.5:  # Outlier
    flag_as_explosion()
```

---

### 6️⃣ **Code Churn Detection**

```
Churn = linhas removidas / (linhas adicionadas + removidas)

Se churn > 60% → muita refatoração
→ Possível código instável
```

**Exemplo:**
```
Commit A: +500 linhas, -50 linhas
         churn = 50/550 = 9% → Normal, código novo

Commit B: +100 linhas, -400 linhas  
         churn = 400/500 = 80% → ALTO!
         → Provavelmente grande refactor
         → Risco: quebrou algo?
```

**Por que detecta problemas:**
- Muito churn = muita incerteza
- Refactores devem ser focados
- Alto churn distribuído pode deixar código quebrado

---

## 🎯 Exemplos Práticos

### Exemplo 1: Detectar Pico
```python
commits = [
    {"sha": "abc", "complexity": 5.0},
    {"sha": "def", "complexity": 5.2},
    {"sha": "ghi", "complexity": 7.8},  # ← Spike!
]

spikes = NonAIAnalyzer.detect_complexity_spikes(commits)
# Retorna: 1 spike com severidade 56% (aumentou 56%)
```

### Exemplo 2: Detectar Tendência
```python
commits = [
    {"complexity": 3.0},
    {"complexity": 3.2},
    {"complexity": 3.5},
    {"complexity": 3.9},  # ← Degradação gradual
    {"complexity": 4.2},
]

trend = NonAIAnalyzer.analyze_complexity_trend(commits)
# trend["trend"] = "declining"
# trend["trend_slope"] = +0.29 (aumenta 0.29 por commit!)
```

### Exemplo 3: Health Score
```python
health = NonAIAnalyzer.calculate_health_score(commits)
print(f"Score: {health.overall_score}/100")
print(f"Interpretação: {health.health_interpretation}")

# Saída:
# Score: 42.3/100
# Interpretação: ⚠️ Saúde Fraca (degradação significativa)
```

---

## ⚙️ Como Usar no Backend

### Opção 1: Usar SEM IA (Rápido)

```python
from services.non_ai_analyzer import NonAIAnalyzer

@app.post("/api/v1/analyze")
async def analyze_repository(request: RepositoryAnalysisRequest):
    repo = git_analyzer.clone_repository(request.url)
    commits = git_analyzer.get_commits_with_files(repo)
    
    # Análise ESTATÍSTICA (SEM IA)
    health = NonAIAnalyzer.calculate_health_score(commits)
    spikes = NonAIAnalyzer.detect_complexity_spikes(commits)
    report = NonAIAnalyzer.generate_text_report(commits, repo_info)
    
    return {
        "health_score": health.overall_score,
        "issues": spikes,
        "report": report
    }
```

### Opção 2: Usar COM IA (Contextual)

```python
from services.ai_analyzer import AIAnalyzer

ai_analyzer = AIAnalyzer(api_key)
analysis = ai_analyzer.analyze_performance_degradation(commits, repo_info)

return {
    "ai_analysis": analysis["analysis"],
    "degradations": analysis["degradation_points"]
}
```

### Opção 3: Usar AMBAS (Híbrido)

```python
# Estatístico para detecção rápida
health = NonAIAnalyzer.calculate_health_score(commits)
spikes = NonAIAnalyzer.detect_complexity_spikes(commits)

# IA para relatório bonito
ai_analysis = AIAnalyzer(...).analyze_performance_degradation(commits, repo_info)

return {
    "quick_metrics": {
        "health_score": health.overall_score,
        "issues_found": len(spikes)
    },
    "detailed_analysis": ai_analysis["analysis"]
}
```

---

## 📊 Comparação: Estatístico vs IA

| Aspecto | Estatístico | IA |
|---------|-----------|-------|
| **Velocidade** | ⚡⚡⚡ ms | 🐢 segundos |
| **Reproduzibilidade** | 100% sempre igual | Pode variar |
| **Explicabilidade** | Você entende tudo | "Caixa preta" |
| **Context-aware** | Não | Sim |
| **Custo** | Grátis | $$ |
| **Confiabilidade** | 100% | 95% |

---

## 🚀 Quando Usar Cada Um?

### Use ESTATÍSTICO quando:
- ✅ Quer velocidade (para feedback imediato)
- ✅ Quer reproduzibilidade (testes, CI/CD)
- ✅ Não tem acesso a IA
- ✅ Precisa explicar EXATAMENTE por quê
- ✅ Quer algo lightweight

### Use IA quando:
- ✅ Quer insights contextuais
- ✅ Precisa de linguagem natural
- ✅ Quer recomendações específicas
- ✅ Está explicando para stakeholders
- ✅ Tempo não é fator crítico

### Use AMBAS quando:
- ✅ Análise em tempo real (estatístico)
- ✅ + Relatório executivo (IA)
- ✅ Máxima qualidade de insights

---

## 📈 Exemplos de Output

### Health Score
```
85-100: ✅ Excelente
60-85:  ⚠️ Boa (alguns pontos de atenção)
40-60:  ⚠️ Fraca (degradação significativa)
0-40:   🔴 Crítica (refatoração urgente)
```

### Detecção de Issues
```
🔴 CRÍTICO (severidade > 70)
  - Picos de complexidade com impacto
  - Degradação tendendo para pior

🟡 AVISO (severidade 40-70)
  - Aumentos moderados
  - Padrões de churn

⚪ INFORMATIVO (severidade < 40)
  - Mudanças menores
  - Alertas preventivos
```

---

## 🔧 Personalizando Thresholds

Todos os valores estão em constantes no início da classe:

```python
class NonAIAnalyzer:
    COMPLEXITY_SPIKE_THRESHOLD = 1.5        # 50% aumento
    GRADUAL_INCREASE_THRESHOLD = 0.2        # 20% em 10 commits
    Z_SCORE_THRESHOLD = 2.0                 # 2 desvios padrão
    MIN_COMMITS_FOR_ANALYSIS = 5
```

Para um repositório específico:
```python
# Mais rigoroso
COMPLEXITY_SPIKE_THRESHOLD = 1.2  # 20% é spike

# Mais lenient
COMPLEXITY_SPIKE_THRESHOLD = 2.0  # 100% é spike
```

---

## 🎓 Por Que Funciona?

### Fundamentos Matemáticos:

1. **Distribuição Normal**: Commits "normais" seguem distribuição
   - Valores extremos (outliers) são detectáveis via Z-score

2. **Tendência Linear**: Performance degrada (ou melhora) linearmente
   - Regressão linear captura a velocidade

3. **Decomposição**: Anomalia = fora do padrão + fora da tendência
   - Se combina detecção de picos + declínio gradual

4. **Heurísticas**: Problemas práticos têm sinais claros
   - File explosion = commit tocou muitos arquivos
   - Code churn = refactor confuso

---

## 💡 Insights

A beleza da abordagem estatística é que:

1. **Você entende completamente** como funciona
2. **Pode debugar** se algo não bate
3. **Pode ajustar** para seu caso de uso
4. **Não depende** de serviço externo
5. **É instantâneo** (roda localmente)

A desvantagem é que:
- Não entende CONTEXTO ("por que foi degradação?")
- Gera relatórios técnicos, não executivos
- Precisa de threshold tuning

Por isso IA é útil: ela preenche essa lacuna!

---

## 📝 Testando Localmente

```bash
# Run the comparison
python services/comparison_analyzer.py

# Output:
# ════════════════════════════════════════════
# COMPARAÇÃO: ANÁLISE ESTATÍSTICA vs IA
# ════════════════════════════════════════════
# 📊 Saúde Geral: 42.3/100
# 📈 Tendência: DECLINING
# 🔍 Issues Encontrados: 3
#    • Picos de complexidade: 1
#    • Degradação gradual: 0
#    • Explosão de arquivos: 1
#    • Code churn: 1
```

---

**Desenvolvido com ❤️ usando estatística pura e Python**
