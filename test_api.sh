#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Code Performance Analyzer - Test Suite║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# 1. Health Check
echo -e "${GREEN}[1] Health Check${NC}"
curl -s "$BASE_URL/api/v1/health" | jq .
echo ""

# 2. Root endpoint
echo -e "${GREEN}[2] Root Endpoint${NC}"
curl -s "$BASE_URL/" | jq .
echo ""

# 3. Análise básica (substitua a URL por um repo real)
echo -e "${GREEN}[3] Análise Básica de Repositório${NC}"
echo "Analisando: https://github.com/torvalds/linux.git (isso pode levar alguns minutos...)"
curl -s -X POST "$BASE_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/torvalds/linux.git",
    "analyze_all_history": false
  }' | jq .
echo ""

# 4. Análise Detalhada com IA
echo -e "${GREEN}[4] Análise Detalhada com IA${NC}"
echo "Analisando com insights de IA..."
curl -s -X POST "$BASE_URL/api/v1/analyze/detailed" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/torvalds/linux.git",
    "analyze_all_history": false
  }' | jq .
echo ""

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testes Concluídos!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
