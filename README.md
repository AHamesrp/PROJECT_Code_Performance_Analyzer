## ⚠️This project was made 100% by AI, I'm testing how far AI can go for a real solution⚠️

# Code Performance Time Machine 🚀

Uma ferramenta que analisa a evolução de performance de repositórios Git ao longo do tempo, identificando degradações e fornecendo insights com IA.

## Features ✨

- 📊 **Análise de Complexidade Ciclomática** - Rastreie como a complexidade evolui
- 🔴 **Detecção de Degradação** - Identifique commits problemáticos automaticamente
- 🤖 **Análise com IA** - Insights automáticos sobre performance usando Claude
- 📈 **Timeline Interativa** - Visualize a evolução ao longo do tempo
- 🔍 **Comparação de Commits** - Compare dois pontos no tempo
- 📁 **Suporte Multi-linguagem** - Análise em Python, JavaScript, Java e mais

## Stack Técnica 🛠️

### Backend
- **FastAPI** - Framework web moderno e rápido
- **GitPython** - Interface Python para Git
- **Radon** - Análise de complexidade de código
- **Claude API** - IA para análise de padrões
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL/SQLite** - Persistência

### Frontend (próximas fases)
- Svelte
- Three.js (visualização 3D)
- Tailwind CSS

## Instalação 🔧

### Pré-requisitos
- Python 3.9+
- Git
- Conta Anthropic (para usar Claude API)

### Setup Rápido

1. **Clone o repositório**
```bash
git clone <seu-repo>
cd code-performance-analyzer
```

2. **Crie um virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY
```

5. **Inicie o servidor**
```bash
python main.py
```

O servidor estará disponível em `http://localhost:8000`

---

## Uso via Terminal 💻

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "Code Performance Time Machine API",
  "version": "1.0.0"
}
```

### 2. Análise Básica
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/repo.git",
    "analyze_all_history": false
  }'
```

**Parâmetros:**
- `url` (string): URL do repositório GitHub
- `analyze_all_history` (bool): Se true, analisa todos os commits. Se false, últimos 50.

**Resposta:**
```json
{
  "repository_url": "https://github.com/user/repo.git",
  "repository_name": "repo",
  "total_commits": 50,
  "analysis_status": "completed",
  "commits": [
    {
      "sha": "abc123",
      "message": "Fix: performance issue",
      "author": "John Doe",
      "committed_date": "2024-01-15T10:30:00",
      "complexity": 7.5,
      "lines_added": 150,
      "lines_removed": 45,
      "files_changed": 3,
      "avg_method_length": 25.3
    },
    ...
  ]
}
```

### 3. Análise Detalhada com IA
```bash
curl -X POST http://localhost:8000/api/v1/analyze/detailed \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/repo.git",
    "analyze_all_history": false
  }'
```

**Resposta incluir:**
- `ai_analysis` - Análise textual da IA
- `degradations_found` - Número de degradações detectadas
- `commits_timeline` - Lista de todos os commits com métricas

---

## Exemplo Completo com HTTPie 🚀

Se preferir usar `httpie` (mais legível que curl):

```bash
# Instalar httpie
pip install httpie

# Health check
http GET localhost:8000/api/v1/health

# Análise
http POST localhost:8000/api/v1/analyze \
  url=https://github.com/user/repo.git \
  analyze_all_history:=false

# Com prettify automático
http --pretty=all POST localhost:8000/api/v1/analyze \
  url=https://github.com/torvalds/linux.git \
  analyze_all_history:=false
```

---

## Estrutura do Projeto 📁

```
code-performance-analyzer/
├── main.py                 # Aplicação FastAPI principal
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── .env                   # Variáveis de ambiente
├── models/
│   ├── database.py       # Modelos SQLAlchemy
│   └── schemas.py        # Schemas Pydantic
├── services/
│   ├── git_analyzer.py   # Análise de repositórios Git
│   ├── metrics_calculator.py  # Cálculo de complexidade
│   └── ai_analyzer.py    # Análise com Claude API
├── routers/
│   └── analysis.py       # Endpoints da API
└── tests/
    └── test_api.sh       # Script de testes
```

---

## Fluxo de Análise 🔄

```
1. Usuário fornece URL do repositório
   ↓
2. GitPython clona o repositório
   ↓
3. Extrai histórico de commits
   ↓
4. Para cada commit:
   - Calcula complexidade ciclomática (Radon)
   - Conta linhas adicionadas/removidas
   - Conta arquivos modificados
   ↓
5. Claude API analisa:
   - Períodos de degradação
   - Commits problemáticos
   - Tendências gerais
   ↓
6. Retorna análise completa
```

---

## Métricas Coletadas 📊

- **Complexidade Ciclomática**: Medida de quantas caminhos diferentes o código pode tomar
- **Linhas Adicionadas/Removidas**: Volume de mudanças
- **Arquivos Modificados**: Escopo das mudanças
- **Maintainability Index**: Score de 0-100 sobre facilidade de manutenção
- **Degradação**: Aumentos significativos em complexidade

---

## Próximos Passos 🚀

- [ ] Frontend com Svelte + Three.js
- [ ] Visualização 3D de timeline
- [ ] Comparação entre branches
- [ ] Suporte a repositórios privados
- [ ] Sistema de cache para análises anteriores
- [ ] Webhooks para análise automática
- [ ] Dashboard em tempo real

---

## Troubleshooting 🔧

### Erro: "Failed to clone repository"
- Verifique se a URL do repositório é válida
- Se for repositório privado, use GitHub token em .env

### Erro: "ANTHROPIC_API_KEY not set"
- Configure a chave da API Anthropic em .env
- Ou exporte como variável de ambiente: `export ANTHROPIC_API_KEY=your_key`

### Erro: "Port 8000 already in use"
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Performance 🚡

- Análise de repositório com 50 commits: ~30-60 segundos
- Análise com IA: +10-15 segundos
- Análise completa de histórico: depende do tamanho do repositório

---

## Contribuindo 🤝

Este é um projeto de portfolio pessoal. Sugestões e melhorias são bem-vindas!

---

## Licença 📄

MIT License - veja LICENSE.md para detalhes

---

## Contato 📧

Arthur - [@AHamesrp](https://github.com/AHamesrp)

