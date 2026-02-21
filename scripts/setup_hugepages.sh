#!/bin/bash
# ============================================================================
# HyperMine Core — Setup de Huge Pages
# ============================================================================
# Este script configura Huge Pages no Linux para otimizar a performance
# de algoritmos memory-hard como RandomX.
#
# Uso: sudo ./setup_hugepages.sh [tamanho_mb]
# Exemplo: sudo ./setup_hugepages.sh 2560  (2.5GB para RandomX)
# ============================================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Tamanho padrão: 2560MB (suficiente para RandomX dataset de 2GB + overhead)
HUGE_PAGES_MB=${1:-2560}
HUGE_PAGE_SIZE_KB=2048  # 2MB pages
HUGE_PAGES_COUNT=$((HUGE_PAGES_MB * 1024 / HUGE_PAGE_SIZE_KB))

echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     HyperMine Core — Huge Pages Setup                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Erro: Este script precisa ser executado como root (sudo).${NC}"
    exit 1
fi

echo -e "${YELLOW}Configurando ${HUGE_PAGES_COUNT} Huge Pages de 2MB (${HUGE_PAGES_MB}MB total)...${NC}"

# 1. Liberar cache do sistema para garantir memória contígua
echo -e "  [1/5] Liberando cache do sistema..."
sync
echo 3 > /proc/sys/vm/drop_caches

# 2. Configurar número de Huge Pages
echo -e "  [2/5] Alocando Huge Pages..."
echo $HUGE_PAGES_COUNT > /proc/sys/vm/nr_hugepages

# Verificar se todas foram alocadas
ALLOCATED=$(cat /proc/sys/vm/nr_hugepages)
if [[ $ALLOCATED -lt $HUGE_PAGES_COUNT ]]; then
    echo -e "${YELLOW}  Aviso: Apenas ${ALLOCATED}/${HUGE_PAGES_COUNT} páginas alocadas.${NC}"
    echo -e "${YELLOW}  Pode ser necessário reiniciar o sistema para liberar memória.${NC}"
else
    echo -e "${GREEN}  ${ALLOCATED} Huge Pages alocadas com sucesso.${NC}"
fi

# 3. Configurar limites de memória locked
echo -e "  [3/5] Configurando limites de memória..."
if ! grep -q "memlock unlimited" /etc/security/limits.conf 2>/dev/null; then
    echo "* soft memlock unlimited" >> /etc/security/limits.conf
    echo "* hard memlock unlimited" >> /etc/security/limits.conf
    echo -e "${GREEN}  Limites de memória configurados.${NC}"
else
    echo -e "  Limites de memória já configurados."
fi

# 4. Desabilitar Transparent Huge Pages (conflita com explicit huge pages)
echo -e "  [4/5] Desabilitando Transparent Huge Pages..."
if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]]; then
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
    echo -e "${GREEN}  THP desabilitado.${NC}"
fi

# 5. Persistir configuração no boot
echo -e "  [5/5] Persistindo configuração..."
SYSCTL_CONF="/etc/sysctl.d/99-hypermine-hugepages.conf"
cat > $SYSCTL_CONF << EOF
# HyperMine Core — Huge Pages Configuration
vm.nr_hugepages = ${HUGE_PAGES_COUNT}
EOF
echo -e "${GREEN}  Configuração salva em ${SYSCTL_CONF}${NC}"

# Resumo
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Completo!                                     ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Huge Pages: ${ALLOCATED} x 2MB = $((ALLOCATED * 2))MB                   ${NC}"
echo -e "${GREEN}║  THP: Desabilitado                                   ║${NC}"
echo -e "${GREEN}║  Memlock: Unlimited                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Para verificar: ${YELLOW}cat /proc/meminfo | grep Huge${NC}"
