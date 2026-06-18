# 🚀 INSTALAÇÃO RÁPIDA - Code Performance Time Machine

## 📦 O que você recebeu

Um arquivo ZIP contendo um projeto **backend Python + FastAPI** para análise de performance de repositórios Git.

**Tamanho:** 34 KB (ZIP comprimido)  
**Arquivos:** 21 arquivos + pastas

---

## ⚡ INSTALAÇÃO (5 MINUTOS)

### **Passo 1: Descompactar o ZIP**

```bash
unzip code-performance-analyzer.zip
cd code-performance-analyzer
```

### **Passo 2: Criar virtual environment**

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
# OU
venv\Scripts\activate       # Windows
```

### **Passo 3: Instalar dependências**

```bash
pip install -r requirements.txt
```

Vai instalar:
- FastAPI (framework web)
- GitPython (análise de Git)
- Radon (complexidade de código)
- Anthropic (IA - opcional)
- SQLAlchemy (banco de dados)
- E mais...

### **Passo 4: Configurar .env (Opcional)**

```bash
# Se quer usar IA:
nano .env
# Edite e adicione sua ANTHROPIC_API_KEY
```

Se não tiver chave, não tem problema! O projeto funciona 100% sem IA.

---

## 🎯 TESTAR AGORA (Escolha 1)

### **Opção A: Testar SEM rodar servidor (Rápido)**

```bash
python test_analyzers.py
```

**Vai mostrar em 1 minuto:**
- ✅ Análise estatística completa
- ✅ Health score (0-100)
- ✅ Issues detectados
- ✅ Comparação com/sem IA

---

### **Opção B: Rodar servidor FastAPI**

```bash
python main.py
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Em outro terminal, testar:**

```bash
# Health check (deve retornar 200)
curl http://localhost:8000/api/v1/health

# Documentação interativa
# Abra no navegador: http://localhost:8000/docs
```

---

## 📂 Estrutura do Projeto

```
code-performance-analyzer/
├── main.py                          # Aplicação FastAPI
├── config.py                        # Configurações
├── requirements.txt                 # Dependências Python
├── .env.example                     # Exemplo de variáveis
├── README.md                        # Documentação completa
├── ANALISE_SEM_IA.md               # Explicação técnica (LEIA!)
│
├── models/
│   ├── database.py                  # SQLAlchemy models
│   └── schemas.py                   # Pydantic schemas
│
├── services/
│   ├── git_analyzer.py              # Análise de Git
│   ├── metrics_calculator.py        # Cálculo de complexidade
│   ├── ai_analyzer.py               # Análise com IA
│   ├── non_ai_analyzer.py           # ✨ Análise SEM IA (novo!)
│   └── comparison_analyzer.py       # ✨ Comparador (novo!)
│
├── routers/
│   └── analysis.py                  # Endpoints da API
│
├── test_analyzers.py                # Testes Python
└── test_api.sh                      # Testes via curl
```

---

## 🧠 ENTENDER O PROJETO

### **1. Leia isto PRIMEIRO (5 min)**
```bash
cat ANALISE_SEM_IA.md
```

Explica as 6 técnicas estatísticas usadas:
- Z-Score
- Regressão Linear
- Spike Detection
- Degradação Gradual
- File Explosion
- Code Churn

### **2. Veja em ação (1 min)**
```bash
python test_analyzers.py
```

### **3. Explore o código**
- `services/non_ai_analyzer.py` - Análise estatística
- `services/ai_analyzer.py` - Integração com Claude
- `routers/analysis.py` - Endpoints

---

## 🔌 ENDPOINTS DISPONÍVEIS

```
GET  /api/v1/health              # Health check
POST /api/v1/analyze             # Análise básica
POST /api/v1/analyze/detailed    # Análise com IA
```

### **Exemplo de uso:**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/repo.git",
    "analyze_all_history": false
  }'
```

---

## 🆘 TROUBLESHOOTING

### **Erro: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

### **Erro: "Port 8000 already in use"**
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### **Erro: "git command not found"**
Instale Git: https://git-scm.com/download

### **Erro: "ANTHROPIC_API_KEY not set"**
Opcional! O projeto funciona 100% sem IA.
Se quiser usar, obtenha em: https://console.anthropic.com

---

## 📊 PRÓXIMOS PASSOS

### **Dia 1: Entender**
- [ ] Ler `ANALISE_SEM_IA.md`
- [ ] Rodar `python test_analyzers.py`
- [ ] Explorar `services/non_ai_analyzer.py`

### **Dia 2: Testar**
- [ ] Rodar `python main.py`
- [ ] Testar endpoints em `/docs`
- [ ] Testar com repositório real

### **Dia 3: Expandir**
- [ ] Adicionar novo método de análise
- [ ] Integrar com banco de dados
- [ ] Criar frontend com Svelte (futuro)

---

## 🎓 O QUE VOCÊ APRENDER

Este projeto ensina:

✅ **Backend com FastAPI**
- Criação de APIs REST
- Schemas com Pydantic
- Integração com banco de dados

✅ **Análise de Dados**
- Estatística (Z-score, regressão linear)
- Detecção de anomalias
- Séries temporais

✅ **Git Programático**
- Clonar repositórios
- Extrair histórico de commits
- Análise de diffs

✅ **Integração com IA**
- API do Anthropic Claude
- Processamento de respostas
- Context management

✅ **Boas Práticas**
- Estrutura modular
- Logging
- Error handling
- Documentação

---

## 💡 DICAS

1. **Comece simples:** Use `test_analyzers.py` para entender o fluxo
2. **Leia o código:** Cada função tem comentários
3. **Experimente:** Mude thresholds em `non_ai_analyzer.py`
4. **Debugue:** Use `print()` liberalmente
5. **Versionize:** `git init` nesta pasta!

---

## 📚 RECURSOS

- **FastAPI docs:** https://fastapi.tiangolo.com/
- **GitPython docs:** https://gitpython.readthedocs.io/
- **Radon docs:** https://radon.readthedocs.io/
- **Anthropic Claude:** https://console.anthropic.com/

---

## ✅ CHECKLIST FINAL

- [ ] ZIP descompactado
- [ ] Venv criado e ativado
- [ ] `pip install -r requirements.txt` executado
- [ ] `python test_analyzers.py` funcionando
- [ ] Documentação lida
- [ ] Pronto para começar!

---

## 🎉 PARABÉNS!

Você agora tem um projeto profissional de análise de performance de Git.

**Próximos passos:** Integrar Svelte + Three.js para visualização 3D (vem em breve!)

---

**Desenvolvido com ❤️ em Python**

Dúvidas? Leia `README.md` para documentação completa!
