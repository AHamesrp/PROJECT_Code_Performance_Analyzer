# Code Performance Time Machine — Documentação Técnica

> **Repositório:** `PROJECT_Code_Performance_Analyzer`
> **Versão da API:** 1.0.0
> **Última análise:** Julho/2026

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Stack Tecnológica](#3-stack-tecnológica)
4. [Estrutura de Diretórios](#4-estrutura-de-diretórios)
5. [Componentes Principais](#5-componentes-principais)
6. [Modelos de Dados (Schemas)](#6-modelos-de-dados-schemas)
7. [Referência da API](#7-referência-da-api)
8. [Interfaces Alternativas (GUI e CLI)](#8-interfaces-alternativas-gui-e-cli)
9. [Algoritmos de Análise](#9-algoritmos-de-análise)
10. [Configuração e Variáveis de Ambiente](#10-configuração-e-variáveis-de-ambiente)
11. [Instalação e Execução](#11-instalação-e-execução)
12. [Testes](#12-testes)
13. [Pontos de Atenção e Débito Técnico](#13-pontos-de-atenção-e-débito-técnico)
14. [Recomendações de Evolução](#14-recomendações-de-evolução)

---

## 1. Visão Geral

O **Code Performance Time Machine** é uma aplicação Python que analisa a evolução histórica de repositórios Git, calculando métricas de complexidade de código ao longo do tempo e identificando pontos de degradação de performance/manutenibilidade.

O sistema oferece **duas abordagens de análise, que podem ser usadas isoladamente ou em conjunto**:

- **Análise Estatística (sem IA):** determinística, baseada em Z-Score, regressão linear e heurísticas de threshold sobre métricas de complexidade ciclomática, churn de código e volume de arquivos alterados.
- **Análise com IA (Groq/LLM):** usa um modelo de linguagem (`llama-3.3-70b-versatile` via API Groq) para gerar uma narrativa qualitativa sobre riscos, tendências e recomendações de refatoração.

A aplicação expõe essas capacidades através de três frontends distintos:

| Interface | Arquivo | Público-alvo |
|---|---|---|
| API REST (FastAPI) | `main.py`, `routers/analysis.py` | Integração via HTTP, uso programático |
| Aplicação Desktop (Tkinter) | `app_gui.py` | Uso interativo local, sem terminal |
| CLI | `scripts/analyze_repo.py` | Automação, scripts, pipelines |

### Fluxo de análise (alto nível)

```
URL do repositório
      │
      ▼
RepoManager.clone_or_update()      → clona repo em diretório temporário
      │
      ▼
GitAnalyzer.get_commits_with_files() → extrai metadados de commits (SHA, autor, +/- linhas, arquivos)
      │
      ▼
Para cada commit: checkout + MetricsCalculator.calculate_complexity()
      │                        (radon cc_visit — complexidade ciclomática)
      ▼
NonAIAnalyzer  (determinístico)   e/ou   AIAnalyzer (Groq LLM)
      │
      ▼
Resposta consolidada (JSON via API, texto via CLI/GUI)
      │
      ▼
RepoManager.cleanup()              → remove diretório temporário
```

---

## 2. Arquitetura

O projeto segue uma arquitetura em camadas simples, típica de um serviço FastAPI de médio porte, sem uso de banco de dados persistente — **toda análise é feita sob demanda, em memória, por request**.

```
┌─────────────────────────────────────────────────────────────┐
│                      Camada de Apresentação                  │
│   FastAPI (main.py)  │  Tkinter GUI (app_gui.py)  │  CLI     │
└──────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                     Camada de Roteamento (API)                 │
│                    routers/analysis.py (APIRouter)              │
└────────────────────────────────┬──────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                        Camada de Serviços                       │
│  RepoManager │ GitAnalyzer │ MetricsCalculator │ AIAnalyzer     │
│              │             │  NonAIAnalyzer     │ ComparisonAnalyzer │
└────────────────────────────────┬──────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                    Camada de Infraestrutura                     │
│   GitPython (clone/checkout) │ Radon (métricas) │ Groq API      │
│              Sistema de arquivos temporário (_repos, /tmp)       │
└─────────────────────────────────────────────────────────────────┘
```

**Características arquiteturais observadas:**

- **Stateless por design:** não há camada de persistência (banco de dados); cada requisição refaz o clone e o cálculo de métricas do zero.
- **Instâncias de serviço como singletons de módulo:** `repo_manager`, `git_analyzer` e `ai_analyzer` são instanciados uma única vez no escopo do router (`routers/analysis.py`), e reutilizados entre requisições.
- **Processamento síncrono e sequencial:** o `checkout` de cada commit + cálculo de complexidade ocorre em loop sequencial dentro do próprio request HTTP (ver seção 13 — Pontos de Atenção).
- **Camada de IA plugável:** `AIAnalyzer` é isolado por trás de uma interface simples (`analyze_performance_degradation`), permitindo trocar o provedor (hoje Groq) sem afetar o restante do sistema.

## 3. Stack Tecnológica

| Categoria | Tecnologia | Versão | Uso no projeto |
|---|---|---|---|
| Framework Web | FastAPI | 0.104.1 | Exposição da API REST (`main.py`, `routers/`) |
| ASGI Server | Uvicorn (`[standard]`) | 0.24.0 | Servidor de aplicação, com `reload` em modo debug |
| Controle de versão | GitPython | 3.1.40 | Clone, checkout e leitura de histórico de commits |
| Métricas de código | Radon | 6.0.1 | Complexidade ciclomática (`cc_visit`) e Maintainability Index (`mi_visit`) |
| Validação de dados | Pydantic | 2.13.4 | Schemas de request/response (`models/schemas.py`) |
| Configuração | pydantic-settings | 2.1.0 | Carregamento de variáveis de ambiente (`config.py`) |
| HTTP client | requests | 2.31.0 | Chamadas à API da Groq (`services/ai_analyzer.py`) |
| Cálculo numérico | NumPy | 2.4.6 | Estatística (médias, desvio padrão, regressão linear, Z-Score) em `non_ai_analyzer.py` |
| Testes | pytest | 7.4.3 | `test_ai_analyzer.py`, `test_analyzers.py` |
| I/O assíncrono | aiofiles | 23.2.1 | Declarado nas dependências (uso direto não identificado no código analisado) |
| Cliente HTTP para testes | httpx | 0.25.2 | Compatibilidade com o `TestClient` do FastAPI |
| GUI Desktop | Tkinter (`ttk`, `scrolledtext`) | stdlib | Interface gráfica standalone (`app_gui.py`) |
| LLM externo | Groq API (`llama-3.3-70b-versatile`) | — | Geração de insights textuais (`services/ai_analyzer.py`) |

> **Observação:** o `requirements.txt` fixa `pydantic==2.13.4` e `numpy==2.4.6`. Ao atualizar o ambiente, vale confirmar compatibilidade dessas versões com `pydantic-settings==2.1.0`, que historicamente acompanha a série 2.x inicial do Pydantic.

## 4. Estrutura de Diretórios

```
PROJECT_Code_Performance_Analyzer/
├── main.py                      # Bootstrap da aplicação FastAPI
├── config.py                    # Settings (env vars) via pydantic-settings
├── requirements.txt              # Dependências fixadas
├── requirements.py               # Script alternativo de instalação (pip programático)
├── test_api.sh                   # Smoke tests via curl contra a API rodando
├── test_analyzers.py             # Script manual de comparação estatística vs IA
├── test_ai_analyzer.py           # Testes unitários (pytest) do AIAnalyzer
├── app_gui.py                    # Aplicação desktop (Tkinter)
├── README.md                     # Notas rápidas de uso (setup de venv, comandos)
├── .gitignore
│
├── routers/
│   ├── __init__.py
│   └── analysis.py               # Endpoints REST (/api/v1/*)
│
├── models/
│   └── schemas.py                # Modelos Pydantic (request/response)
│
├── services/
│   ├── __init__.py
│   ├── repo_manager.py           # Clone/checkout/cleanup de repositórios
│   ├── git_analyzer.py           # Extração de metadados de commits
│   ├── metrics_calculator.py     # Complexidade, Maintainability Index, LOC
│   ├── non_ai_analyzer.py        # Heurísticas estatísticas de degradação
│   ├── ai_analyzer.py            # Integração com Groq LLM
│   └── comparison_analyzer.py    # Comparação lado a lado: estatístico vs IA
│
├── scripts/
│   └── analyze_repo.py           # CLI standalone de análise
│
├── static/                        # Frontend estático servido em "/" (index.html)
│
└── _repos/                        # Registro (.txt) de URLs de repositórios já analisados
    ├── academia_fabiano_lp_c20d6ade.txt
    └── simple_crud_fdaa0af9.txt
```

## 5. Componentes Principais

### 5.1 `services/repo_manager.py` — `RepoManager`

Responsável pelo ciclo de vida do repositório clonado.

- **`clone_or_update(url, force_clone=False)`**: cria um diretório temporário único (`tempfile.mkdtemp`) e clona o repositório via `GitPython`. Antes disso, chama `save_repo_link()`, que grava um arquivo `.txt` em `_repos/<nome>_<hash>.txt` contendo apenas a URL — funcionando como um registro leve de repositórios já analisados (não versiona código, apenas metadado).
- **`_build_authenticated_url(url)`**: injeta um `GITHUB_TOKEN` (se configurado) na URL HTTPS do GitHub, permitindo clonar repositórios privados.
- **`validate_git_url(url)`**: validação simples baseada em sufixo `.git`, prefixo `git@` ou presença de `github.com`/`gitlab.com` na string — não é uma validação estrita de formato de URL.
- **`cleanup(repo)`**: remove o diretório temporário. Implementa fallback robusto para lidar com erros de permissão do Windows (`chmod 0o777` recursivo, depois `rmdir /s /q` ou `rm -rf` via subprocess como último recurso).

### 5.2 `services/git_analyzer.py` — `GitAnalyzer`

Extrai metadados de commits para uso posterior pelos analisadores.

- **`get_commits_with_files(repo, limit=50)`**: itera `repo.iter_commits()`, limita ao `n` mais recentes, e para cada commit extrai SHA (curto e completo), mensagem (truncada em 100 caracteres), autor, data, arquivos alterados e linhas adicionadas/removidas via `commit.stats`. Ao final, **inverte a lista** para ordem cronológica (mais antigo primeiro) — importante para os cálculos de tendência e regressão linear que assumem ordem temporal crescente.
- **`get_repository_info(repo)`**: retorna nome, URL, número de branches remotas, total de commits e contagem de arquivos por extensão.
- **`get_files_by_type`** e **`cleanup`**: utilitários auxiliares.

### 5.3 `services/metrics_calculator.py` — `MetricsCalculator`

Camada de cálculo de métricas de qualidade de código, via **Radon**. Todos os métodos são `@staticmethod` — a classe funciona como um namespace de funções puras, sem estado.

- **`calculate_complexity(repo_path)`**: percorre recursivamente todos os arquivos `.py` do repositório (ignorando `venv`, `__pycache__`, `.git`, `node_modules`), roda `radon.cc_visit` em cada arquivo e calcula a complexidade ciclomática média por arquivo, depois a média geral do repositório. Retorna também os 5 arquivos mais complexos.
  - ⚠️ **Limitação importante:** apenas arquivos `.py` são analisados. As constantes `JS_EXTENSIONS` e `JAVA_EXTENSIONS` estão declaradas mas não são utilizadas em nenhum método — a análise de complexidade é, na prática, **Python-only**.
- **`calculate_maintainability_index(repo_path)`**: usa `radon.mi_visit(code, multi=True)` para obter o Maintainability Index (escala 0–100) por arquivo, com interpretação textual (`_interpret_mi`) segundo as faixas convencionais do Radon (≥85 Muito Alta, ≥70 Alta, ≥55 Moderada, ≥40 Baixa, <40 Muito Baixa).
- **`count_lines_of_code(repo_path, extensions=None)`**: conta linhas totais, em branco e comentários (heurística simples: linha começa com `#`) — não trata comentários multilinha (`"""..."""`) nem comentários de outras linguagens.
- **`analyze_full_repository(repo_path)`**: agrega complexidade, MI, LOC e um `health_score` combinado.
- **`_calculate_health_score(complexity, mi)`**: fórmula `(MI_normalizado × 0.4) + (score_de_complexidade × 0.6)`, onde `score_de_complexidade = max(0, 100 - complexidade × 5)`. Essa é uma fórmula **diferente** da usada em `NonAIAnalyzer.calculate_health_score` (seção 9.3) — os dois métodos calculam "saúde" de formas distintas e não devem ser confundidos.

### 5.4 `services/non_ai_analyzer.py` — `NonAIAnalyzer`

O núcleo da análise determinística/estatística. Ver detalhamento dos algoritmos na seção 9.

Principais responsabilidades:
- Tendência de complexidade via regressão linear (`analyze_complexity_trend`)
- Detecção de anomalias via Z-Score (`detect_anomalies_zscore`)
- Detecção de 4 tipos de degradação: `COMPLEXITY_SPIKE`, `GRADUAL_INCREASE`, `FILE_EXPLOSION`, `CODE_CHURN` (enum `DegradationType`)
- Cálculo de um `RepositoryHealth` (score 0–100 + interpretação textual)
- Geração de relatório textual completo (`generate_text_report`), usado pela CLI e pela GUI

### 5.5 `services/ai_analyzer.py` — `AIAnalyzer`

Encapsula a chamada à API da Groq (compatível com o formato OpenAI Chat Completions).

- **`analyze_performance_degradation(commits, repository_info, use_top_commits=20)`**: monta um prompt estruturado em português com os dados dos commits e solicita ao LLM uma análise em 4 seções (riscos, o que está piorando, recomendações, justificativa). Retorna também `degradation_points`, calculados **localmente** (não pelo LLM) via `_identify_degradations` — um detector de spikes simples baseado em variação percentual de complexidade entre commits consecutivos (threshold padrão: 2%, deliberadamente baixo, o que tende a gerar muitos falsos positivos — ver seção 13).
  - ⚠️ **Nota:** o parâmetro `use_top_commits` é aceito mas **nunca utilizado** dentro do método — a variável `filtered_commits` recebe simplesmente `commits` sem qualquer filtragem. O método auxiliar `_select_top_commits_for_ai`, que implementa um sistema de scoring por relevância/recência, existe na classe mas não é chamado de lugar nenhum na aplicação (é coberto apenas em teste unitário).
- **`_call_groq(prompt, max_tokens)`**: chamada HTTP direta via `requests.post`, timeout de 60s, `temperature=0.2`. Lança `ValueError` se `GROQ_API_KEY` não estiver configurada.
- **`compare_commits(commit1, commit2)`**: gera uma comparação textual entre dois commits específicos via LLM — mas não há endpoint REST que exponha essa funcionalidade (o endpoint `/api/v1/compare` está estruturalmente pronto, porém retorna `501 Not Implemented`, ver seção 7.3).

### 5.6 `services/comparison_analyzer.py` — `AnalysisComparator`

Utilitário de comparação lado a lado entre o método estatístico e o método com IA, útil para fins de demonstração/benchmark (usado em `test_analyzers.py`). Não é consumido pela API REST nem pela GUI em produção — é essencialmente uma ferramenta de desenvolvimento/showcase.

### 5.7 `routers/analysis.py`

Define o `APIRouter` com prefixo `/api/v1` e tag `analysis`. Instancia `repo_manager`, `git_analyzer` e `ai_analyzer` como **singletons de módulo**, criados uma única vez na importação do arquivo (não por request, nem via injeção de dependência do FastAPI — ver seção 13).

## 6. Modelos de Dados (Schemas)

Definidos em `models/schemas.py`, usando Pydantic v2 (`class Config: from_attributes = True`, equivalente ao antigo `orm_mode`).

### `CommitMetricResponse`
Representa um commit já processado com suas métricas.

| Campo | Tipo | Descrição |
|---|---|---|
| `sha` | `str` | Hash curto do commit |
| `message` | `str` | Mensagem do commit (truncada em 100 caracteres na origem) |
| `author` | `str` | Nome do autor |
| `committed_date` | `datetime` | Data do commit |
| `complexity` | `float` | Complexidade ciclomática média calculada via Radon |
| `lines_added` | `int` | Linhas adicionadas |
| `lines_removed` | `int` | Linhas removidas |
| `files_changed` | `int` | Número de arquivos alterados |
| `avg_method_length` | `float` | **Sempre `0.0`** — campo placeholder, nunca calculado de fato (ver seção 13) |

### `RepositoryAnalysisRequest`
| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `url` | `str` | — | URL do repositório Git |
| `analyze_all_history` | `bool` | `False` | Se `False`, limita a análise aos 50 commits mais recentes |

### `RepositoryAnalysisResponse`
Agrega `repository_url`, `repository_name`, `total_commits`, `analysis_status` e a lista de `commits: List[CommitMetricResponse]`.

### `PerformanceReportResponse`
Usado pelo endpoint de análise detalhada (com IA): `repository_url`, `total_commits_analyzed`, `degradations_found`, `ai_analysis` (texto gerado pelo LLM) e `commits_timeline`.

### `ComparisonRequest` / `ComparisonResponse`
Modelos já definidos para o endpoint `/api/v1/compare` — que atualmente **não está implementado** (retorna 501). Os campos definidos (`complexity_change`, `degradation_percentage` etc.) descrevem a intenção futura da funcionalidade.

## 7. Referência da API

Base path: `/api/v1` · Documentação interativa automática disponível em `/docs` (Swagger) e `/redoc`.

### 7.1 `POST /api/v1/analyze`

Analisa um repositório e retorna as métricas de complexidade por commit, **sem** envolver IA.

**Request:**
```json
{
  "url": "https://github.com/user/repo.git",
  "analyze_all_history": false
}
```

**Fluxo interno:**
1. Valida a URL (`RepoManager.validate_git_url`).
2. Clona o repositório (`clone_or_update`).
3. Extrai info do repo e lista de commits (limitada a 50, salvo `analyze_all_history=true`).
4. Para **cada commit**, faz `git checkout` daquele SHA e roda `MetricsCalculator.calculate_complexity` sobre o working directory naquele estado — ou seja, a complexidade retornada é a complexidade **do repositório inteiro no momento daquele commit**, não apenas do diff.
5. Agenda limpeza do diretório clonado como `BackgroundTask`.

**Response:** `RepositoryAnalysisResponse` (ver seção 6).

**Erros:** qualquer exceção durante o processo retorna `400 Bad Request` com o detalhe da exceção — não há diferenciação entre erro de validação, falha de clone (rede/autenticação) ou erro de processamento (ver seção 13).

### 7.2 `POST /api/v1/analyze/detailed`

Mesmo fluxo de coleta de métricas do endpoint anterior, mas ao final envia os commits para `AIAnalyzer.analyze_performance_degradation`, que consulta a Groq API e retorna uma análise textual qualitativa.

**Response:** `PerformanceReportResponse`, incluindo o campo `ai_analysis` com o texto gerado pelo LLM e `degradations_found` (contagem de pontos de degradação identificados heuristicamente, não pela IA).

**Pré-requisito:** variável de ambiente `GROQ_API_KEY` configurada — caso contrário, a chamada ao LLM falha internamente e a exceção é capturada e retornada como texto de erro dentro do próprio campo `analysis` (o endpoint não retorna erro HTTP nesse caso específico, apenas embute a mensagem de erro no corpo da resposta).

### 7.3 `POST /api/v1/compare`

**Não implementado.** Retorna sempre `501 Not Implemented` com a mensagem *"Endpoint de comparação ainda em desenvolvimento"*. Os schemas `ComparisonRequest`/`ComparisonResponse` já existem, indicando que a funcionalidade está planejada mas não entregue.

### 7.4 `GET /api/v1/health`

Health check simples, sem dependências externas:
```json
{
  "status": "healthy",
  "service": "Code Performance Time Machine API",
  "version": "1.0.0"
}
```

### 7.5 `GET /`

Serve o frontend estático (`static/index.html`) — não analisado em profundidade neste documento, pois o conteúdo do diretório `static/` não foi fornecido junto ao repositório.

### 7.6 `GET /docs-redirect`

Endpoint utilitário que retorna as URLs de `/docs` e `/redoc` em formato JSON (não faz redirecionamento HTTP de fato, apenas informa as rotas).

## 8. Interfaces Alternativas (GUI e CLI)

### 8.1 Aplicação Desktop — `app_gui.py`

Interface Tkinter com tema escuro customizado (`tk_setPalette`, estilos `ttk` sobrescritos para tons de cinza escuro/azul). Fluxo:

1. Usuário informa a URL do repositório e opcionalmente marca "Análise detalhada (IA)".
2. `on_start()` dispara `run_analysis` em uma **thread separada** (`threading.Thread(..., daemon=True)`), evitando travar a UI durante o clone e o processamento.
3. Ao final, `self.after(0, self.display_results, analysis_data)` atualiza a UI de volta na thread principal do Tkinter — padrão correto para atualizar widgets a partir de uma thread de trabalho.
4. Exibe três áreas de texto: resumo executivo, timeline de commits (até 12) e relatório completo (estatístico ou de IA, dependendo do modo escolhido).

Reaproveita diretamente os serviços da API (`RepoManager`, `GitAnalyzer`, `MetricsCalculator`, `AIAnalyzer`, `NonAIAnalyzer`) — não há duplicação de lógica de negócio entre GUI e API, o que é um ponto positivo de design.

### 8.2 CLI — `scripts/analyze_repo.py`

Script standalone que aceita `--url` (com um repositório de exemplo como padrão, hardcoded) e `--detailed` (flag para habilitar análise de IA). Internamente segue o mesmo fluxo de clone → checkout por commit → cálculo de complexidade → relatório (`NonAIAnalyzer.generate_text_report`), imprimindo o resultado diretamente no `stdout`.

> ⚠️ O valor padrão de `--url` aponta para um repositório específico (`AHamesrp/academia_fabiano_lp.git`) — aparentemente um repositório de teste do autor, deixado como default. Recomenda-se tornar `--url` obrigatório em ambientes que não sejam de desenvolvimento local.

## 9. Algoritmos de Análise

### 9.1 Complexidade Ciclomática (Radon)

Calculada por `MetricsCalculator.calculate_complexity`: para cada arquivo `.py`, `radon.cc_visit(code)` retorna uma lista de blocos analisáveis (funções, métodos, classes) com sua complexidade individual; a métrica por arquivo é a **média simples** dessas complexidades, e a métrica do repositório é a média das médias por arquivo — não uma média ponderada por número de funções, o que faz com que um arquivo pequeno com uma função complexa pese o mesmo que um arquivo grande com muitas funções simples.

### 9.2 Tendência de Complexidade (regressão linear)

`NonAIAnalyzer.analyze_complexity_trend` ajusta uma reta (`np.polyfit(x, complexities, 1)`) sobre a série de complexidades por commit. O coeficiente angular (`slope`) determina a classificação:
- `slope < -0.01` → tendência **improving**
- `slope > 0.01` → tendência **declining**
- caso contrário → **stable**

Requer no mínimo `MIN_COMMITS_FOR_ANALYSIS = 5` commits; abaixo disso, retorna `{"status": "insufficient_data"}`.

### 9.3 Detecção de Degradação — 4 heurísticas independentes

| Heurística | Método | Critério de disparo | Métrica de severidade |
|---|---|---|---|
| **Complexity Spike** | `detect_complexity_spikes` | Aumento > 50% (`COMPLEXITY_SPIKE_THRESHOLD = 1.5`) entre commits consecutivos | `min(100, pct_change / 2)` |
| **Gradual Increase** | `detect_gradual_decline` | Em janela de 10 commits (`GRADUAL_INCREASE_WINDOW`), slope positivo e aumento > 20% (`GRADUAL_INCREASE_THRESHOLD`) | `min(50, pct_change / 2)` |
| **File Explosion** | `detect_file_explosion` | Z-score de `files_changed` > 2.5 | `min(70, z_score * 20)` |
| **Code Churn** | `detect_code_churn` | Mudança total > 100 linhas **e** taxa de remoção > 60% do total alterado | `min(60, churn_rate * 100)` |

O **Health Score** (`calculate_health_score`, retorna `RepositoryHealth`) é calculado como:
```
score = 100 - média(severidade de todas as degradações detectadas)
score += 10  se tendência = "improving"
score -= 15  se tendência = "declining"
score = clamp(score, 0, 100)
```
Interpretação: ≥80 Excelente · ≥60 Boa · ≥40 Fraca · <40 Crítica.

> ⚠️ Esse cálculo é **diferente** do `_calculate_health_score` em `MetricsCalculator` (seção 5.3), que usa uma fórmula baseada em MI + complexidade ponderados (40/60). Duas fontes de verdade distintas para "saúde do repositório" coexistem no código — atenção ao integrar os dois módulos em um único relatório.

### 9.4 Detecção de Anomalias (Z-Score)

`detect_anomalies_zscore` calcula `|z| = |(valor - média) / desvio_padrão|` para qualquer métrica numérica dos commits; `|z| > 2.0` é considerado anomalia (`Z_SCORE_THRESHOLD`), classificada como `critical` se `|z| > 3` ou `warning` caso contrário. Não é chamado por nenhum endpoint de produção — usado apenas em `test_analyzers.py`.

### 9.5 Análise via IA (Groq)

O prompt enviado ao LLM inclui o resumo de **todos** os commits recebidos (não há truncamento por padrão, apesar do parâmetro `use_top_commits` sugerir isso — ver seção 5.5), pedindo uma resposta estruturada em 4 seções fixas. Os "pontos de degradação" retornados pela API vêm de uma heurística local (`_identify_degradations`, threshold de 2% de aumento de complexidade) — **não são extraídos do texto gerado pelo LLM**, ou seja, a contagem de degradações é sempre determinística mesmo na "análise com IA".

## 10. Configuração e Variáveis de Ambiente

Gerenciadas por `config.py` (`pydantic-settings`), com suporte a arquivo `.env`:

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `GROQ_API_KEY` | `str` | `""` | Chave de API da Groq, necessária para os endpoints `/analyze/detailed` e para a GUI em modo "detalhado" |
| `GITHUB_TOKEN` | `str` | `""` | Token para clonar repositórios privados do GitHub via HTTPS autenticado |
| `DEBUG` | `bool` | `True` | Habilita `reload` do Uvicorn |
| `ENVIRONMENT` | `str` | `"development"` | Rótulo informativo, logado no startup |
| `HOST` | `str` | `"0.0.0.0"` | Host do Uvicorn (fixo no código, não lido de env var apesar de estar na classe `Settings`) |
| `PORT` | `int` | `8000` | Porta do Uvicorn (idem — valor fixo na classe, não parametrizado por variável de ambiente) |

> ⚠️ `HOST` e `PORT` estão definidos como atributos fixos da classe `Settings` (não usam `os.getenv`), diferentemente de `GROQ_API_KEY`, `GITHUB_TOKEN`, `DEBUG` e `ENVIRONMENT`. Para alterar host/porta em produção, hoje é necessário editar `config.py` diretamente — não é configurável apenas por variável de ambiente, apesar da classe se chamar `Settings` e usar `pydantic_settings.BaseSettings`.

## 11. Instalação e Execução

```bash
# 1. Clonar o repositório e criar ambiente virtual
git clone https://github.com/AHamesrp/PROJECT_Code_Performance_Analyzer.git
cd PROJECT_Code_Performance_Analyzer
python -m venv venv

# 2. Ativar o ambiente virtual
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências (duas opções equivalentes)
pip install -r requirements.txt
# ou, via script auxiliar (força reinstalação/upgrade):
python requirements.py

# 4. Configurar variáveis de ambiente (.env na raiz do projeto)
echo "GROQ_API_KEY=sua_chave_aqui" >> .env
echo "GITHUB_TOKEN=seu_token_aqui" >> .env

# 5. Subir a API
python main.py
# equivalente a: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. (Opcional) Rodar a interface desktop
python app_gui.py

# 7. (Opcional) Rodar a CLI
python scripts/analyze_repo.py --url https://github.com/user/repo.git --detailed
```

A API estará disponível em `http://localhost:8000`, com documentação interativa em `http://localhost:8000/docs`.

Testes de fumaça contra a API já em execução podem ser feitos com o script fornecido:
```bash
chmod +x test_api.sh
./test_api.sh
```
> Requer `jq` instalado, e por padrão testa contra `https://github.com/torvalds/linux.git` — um repositório grande, adequado apenas para teste manual pontual (a análise pode levar minutos, dado o `checkout` sequencial por commit).

## 12. Testes

| Arquivo | Tipo | Cobertura |
|---|---|---|
| `test_ai_analyzer.py` | Testes unitários (pytest) | Mock de `requests.post` para validar payload enviado à Groq (`test_analyze_performance_degradation_uses_groq_payload`) e a lógica de priorização de commits (`test_select_top_commits_for_ai_prioritizes_recent_commits`) — **testa um método (`_select_top_commits_for_ai`) que não é usado em produção** (ver seção 5.5 e 13) |
| `test_analyzers.py` | Script de demonstração manual (não pytest) | Executa `NonAIAnalyzer` e `AnalysisComparator` sobre um dataset sintético de 10 commits com um "spike" deliberado de complexidade, imprimindo resultados no console |
| `test_api.sh` | Smoke test de integração | Exercita `/health`, `/`, `/analyze` e `/analyze/detailed` via `curl`, contra um repositório real de terceiros |

**Lacunas de cobertura identificadas:**
- Não há testes automatizados (pytest) para `MetricsCalculator`, `GitAnalyzer`, `RepoManager` ou `NonAIAnalyzer` — os únicos testes formais cobrem exclusivamente `AIAnalyzer`.
- Não há testes de integração automatizados dos endpoints FastAPI usando `TestClient`/`httpx` (apesar de `httpx` estar nas dependências) — a validação de endpoints depende do script bash manual.
- Não há testes para os caminhos de erro (URL inválida, falha de clone, `GROQ_API_KEY` ausente).

## 13. Pontos de Atenção e Débito Técnico

Lista consolidada de observações relevantes para manutenção e evolução do projeto, na perspectiva de revisão sênior de código:

1. **Performance: checkout sequencial por commit.** Tanto `/analyze` quanto `/analyze/detailed` fazem `git checkout` + varredura completa do repositório para **cada commit individualmente**, de forma síncrona dentro do request HTTP. Para repositórios com muitos arquivos ou muitos commits (mesmo limitado a 50), isso pode tornar o endpoint lento e bloquear o event loop do FastAPI (as chamadas não são `async`, e não há uso de `run_in_executor`/`BackgroundTasks` para o processamento pesado, apenas para o cleanup).
2. **`avg_method_length` nunca é calculado.** O campo existe no schema `CommitMetricResponse` e é sempre preenchido com `0.0` (comentado como `# Placeholder` no próprio `routers/analysis.py`) — consumidores da API podem interpretar erroneamente esse campo como um valor real.
3. **Duas fórmulas distintas de "Health Score" convivem no código** (`MetricsCalculator._calculate_health_score` vs. `NonAIAnalyzer.calculate_health_score`), com pesos e critérios diferentes, sem nomenclatura que as diferencie claramente. Risco de confusão para quem for integrar os dois relatórios em um dashboard único.
4. **`AIAnalyzer._select_top_commits_for_ai` é código morto em produção.** Está implementado, testado unitariamente, mas nunca chamado por `analyze_performance_degradation` — o parâmetro `use_top_commits` é aceito e ignorado. Isso significa que **todo** o histórico de commits retornado é enviado ao prompt do LLM, o que pode gerar prompts muito longos (custo/tokens) para `analyze_all_history=true`.
5. **Endpoint `/api/v1/compare` não implementado** apesar de schemas prontos (`ComparisonRequest`/`ComparisonResponse`) — expõe uma funcionalidade "fantasma" na documentação OpenAI/Swagger que sempre retorna 501.
6. **Tratamento de erro genérico.** Praticamente todos os métodos usam `except Exception as e` amplos, retornando `400 Bad Request` para qualquer falha em `/analyze` e `/analyze/detailed` — não há diferenciação entre erro de validação (URL malformada), erro de rede (clone falhou) e erro de infraestrutura (Groq indisponível, rate limit, etc.), dificultando o diagnóstico por clientes da API.
7. **Ausência de rate limiting / autenticação na API.** Não há nenhuma camada de autenticação, autorização ou limitação de taxa nos endpoints — qualquer cliente pode disparar clones de repositórios arbitrários e chamadas à Groq (que possuem custo), o que é uma exposição relevante caso o serviço seja publicado publicamente (`CORSMiddleware` está configurado com `allow_origins=["*"]`, reforçando esse risco).
8. **Falta de persistência.** Toda análise é recalculada do zero a cada chamada — repetir a análise do mesmo repositório/commit reprocessa tudo novamente, sem cache. Os arquivos `.txt` em `_repos/` apenas registram a URL, não armazenam resultados.
9. **`MetricsCalculator` está documentado como multi-linguagem mas só analisa Python.** As constantes `JS_EXTENSIONS` e `JAVA_EXTENSIONS` sugerem suporte planejado a JavaScript/TypeScript/Java que não foi implementado (`Radon` é uma ferramenta Python-only por natureza, então suportar outras linguagens exigiria uma ferramenta de métricas adicional).
10. **Contagem de linhas de comentário é uma heurística frágil.** `count_lines_of_code` considera comentário apenas linhas que começam com `#`, sem tratar docstrings (`"""..."""`) nem comentários de bloco — subestima significativamente a proporção real de documentação em código Python idiomático.
11. **Threshold de degradação inconsistente entre módulos.** `AIAnalyzer._identify_degradations` usa `threshold_increase=2.0` (2%) como percentual de aumento para marcar degradação, enquanto `NonAIAnalyzer.detect_complexity_spikes` usa 50% (`COMPLEXITY_SPIKE_THRESHOLD = 1.5`, ou seja, 150% do valor original). Isso faz com que a contagem de "degradações" retornada por `/analyze/detailed` seja muito mais sensível (mais falsos positivos) do que a do endpoint puramente estatístico — os dois números não são comparáveis entre si, apesar de aparecerem lado a lado em UIs que consomem ambos.
12. **CLI com URL padrão hardcoded** apontando para um repositório de teste pessoal do autor (`academia_fabiano_lp`), o que pode causar confusão se executada sem o parâmetro `--url` em ambiente não familiarizado com o projeto.

## 14. Recomendações de Evolução

1. **Paralelizar o cálculo de métricas por commit** (ex.: `concurrent.futures.ThreadPoolExecutor`, já que a maior parte do custo é I/O de disco e subprocessos Git) ou, alternativamente, calcular a complexidade **apenas do diff** de cada commit em vez do repositório inteiro em cada checkout — reduz drasticamente o tempo de resposta.
2. **Unificar o cálculo de Health Score** em um único serviço/fórmula documentada, ou renomear claramente os dois indicadores existentes (ex.: `structural_health_score` vs. `trend_health_score`) para evitar ambiguidade em relatórios.
3. **Implementar cache de resultados** por `(repo_url, commit_sha)`, mesmo que em memória ou SQLite local, para evitar reprocessamento de commits já analisados anteriormente — especialmente relevante dado que a mesma URL costuma ser re-analisada (ver os registros em `_repos/`).
4. **Adicionar autenticação básica (API key) e rate limiting** antes de expor a API além do ambiente local/de desenvolvimento, dado o custo de infraestrutura (clone de repositórios arbitrários + chamadas à Groq).
5. **Padronizar os thresholds de degradação** entre `AIAnalyzer` e `NonAIAnalyzer`, ou documentar explicitamente por que diferem, para permitir comparações justas entre os dois métodos de análise.
6. **Completar ou remover o endpoint `/api/v1/compare`** — deixar um endpoint documentado no Swagger que sempre retorna 501 é uma fonte de confusão para consumidores da API.
7. **Ativar `_select_top_commits_for_ai`** dentro de `analyze_performance_degradation` (respeitando o parâmetro já existente `use_top_commits`), reduzindo o tamanho/custo dos prompts enviados à Groq em repositórios com muito histórico.
8. **Expandir a suíte de testes automatizados** para cobrir `NonAIAnalyzer`, `MetricsCalculator` e os endpoints REST via `TestClient`, incluindo casos de erro (URL inválida, ausência de `GROQ_API_KEY`, falha de clone).
9. **Tornar `HOST` e `PORT` verdadeiramente configuráveis via variável de ambiente**, consistente com o restante da classe `Settings`.
10. **Melhorar a heurística de contagem de comentários** para reconhecer docstrings Python (`'''`/`"""`), aumentando a precisão da métrica de LOC.

---

*Documento gerado a partir de leitura estática do código-fonte disponibilizado do repositório `PROJECT_Code_Performance_Analyzer`. Não foram executados os testes nem o serviço em ambiente real como parte desta análise.*
