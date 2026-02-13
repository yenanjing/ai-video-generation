#!/bin/bash

# AI Video Generation System - Installation Verification Script

set -e

echo "🔍 AI Video Generation System - Installation Verification"
echo "=========================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check function
check() {
    local name=$1
    local command=$2
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name"
    else
        echo -e "${RED}✗${NC} $name"
        ((ERRORS++))
    fi
}

# Warning function
warn() {
    local name=$1
    local command=$2
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name"
    else
        echo -e "${YELLOW}⚠${NC} $name (optional)"
        ((WARNINGS++))
    fi
}

echo "1. System Requirements"
echo "----------------------"
check "Python 3.10+" "python3 --version | grep -qE 'Python 3\.(1[0-9]|[2-9][0-9])'"
check "Node.js 18+" "node --version | grep -qE 'v(1[8-9]|[2-9][0-9])'"
check "FFmpeg" "ffmpeg -version"
check "npm" "npm --version"
warn "Git" "git --version"
warn "Docker" "docker --version"
warn "Docker Compose" "docker-compose --version"
echo ""

echo "2. Project Structure"
echo "--------------------"
check "video_engine/" "test -d video_engine"
check "video_api/" "test -d video_api"
check "video_ui/" "test -d video_ui"
check "workspace/" "test -d workspace || mkdir -p workspace"
check ".env file" "test -f .env"
echo ""

echo "3. Python Dependencies"
echo "----------------------"
check "requirements.txt" "test -f requirements.txt"
check "requirements-api.txt" "test -f requirements-api.txt"

# Check if venv exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    
    # Activate venv and check packages
    source venv/bin/activate 2>/dev/null || true
    
    check "fastapi installed" "python -c 'import fastapi' 2>/dev/null"
    check "anthropic installed" "python -c 'import anthropic' 2>/dev/null"
    check "replicate installed" "python -c 'import replicate' 2>/dev/null"
    warn "uvicorn installed" "python -c 'import uvicorn' 2>/dev/null"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found"
    echo "  Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    ((WARNINGS++))
fi
echo ""

echo "4. React Frontend"
echo "-----------------"
check "package.json" "test -f video_ui/package.json"
check "tsconfig.json" "test -f video_ui/tsconfig.json"

if [ -d "video_ui/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node modules installed"
else
    echo -e "${YELLOW}⚠${NC} Node modules not installed"
    echo "  Run: cd video_ui && npm install"
    ((WARNINGS++))
fi

if [ -d "video_ui/build" ]; then
    echo -e "${GREEN}✓${NC} Production build exists"
else
    echo -e "${YELLOW}⚠${NC} Production build not found (optional for development)"
    ((WARNINGS++))
fi
echo ""

echo "5. Configuration"
echo "----------------"
check ".env exists" "test -f .env"

if [ -f .env ]; then
    check "ANTHROPIC_API_KEY set" "grep -q 'ANTHROPIC_API_KEY=sk-ant-' .env"
    check "REPLICATE_API_TOKEN set" "grep -q 'REPLICATE_API_TOKEN=r8_' .env"
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "  Run: cp .env.example .env"
    echo "  Then edit .env with your API keys"
    ((ERRORS++))
fi
echo ""

echo "6. Deployment Files"
echo "-------------------"
check "start_dev.sh" "test -f start_dev.sh && test -x start_dev.sh"
check "Dockerfile" "test -f Dockerfile"
check "docker-compose.yml" "test -f docker-compose.yml"
echo ""

echo "7. Documentation"
echo "----------------"
check "README.md" "test -f README.md"
check "DEPLOYMENT.md" "test -f DEPLOYMENT.md"
check "PHASE3_COMPLETE.md" "test -f PHASE3_COMPLETE.md"
check "PROJECT_COMPLETE.md" "test -f PROJECT_COMPLETE.md"
check "FINAL_SUMMARY.md" "test -f FINAL_SUMMARY.md"
echo ""

echo "8. CLI Commands"
echo "---------------"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
    check "video_engine module" "python -c 'import video_engine' 2>/dev/null"
    check "CLI accessible" "python -m video_engine.cli --help > /dev/null 2>&1"
else
    echo -e "${YELLOW}⚠${NC} Skipping CLI checks (venv not found)"
    ((WARNINGS++))
fi
echo ""

echo "=========================================================="
echo "Verification Complete"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You're ready to start:"
    echo "  ./start_dev.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings${NC}"
    echo ""
    echo "System is functional but some optional features are missing."
    echo "You can still start with: ./start_dev.sh"
    exit 0
else
    echo -e "${RED}✗ $ERRORS errors, $WARNINGS warnings${NC}"
    echo ""
    echo "Please fix the errors above before starting."
    echo ""
    echo "Quick fix commands:"
    echo "  1. Create virtual environment:"
    echo "     python -m venv venv"
    echo "     source venv/bin/activate"
    echo "     pip install -r requirements.txt -r requirements-api.txt"
    echo ""
    echo "  2. Install frontend dependencies:"
    echo "     cd video_ui && npm install && cd .."
    echo ""
    echo "  3. Configure environment:"
    echo "     cp .env.example .env"
    echo "     # Edit .env with your API keys"
    exit 1
fi
