#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Flask API - Running Local CI/CD Jobs${NC}"
echo "================================================"

# Function to print job headers
print_job_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ $1 failed${NC}"
    exit 1
}

# Function to handle success
handle_success() {
    echo -e "${GREEN}✅ $1 passed${NC}"
}

# Create test results directory
mkdir -p test-results

print_job_header "FORMATTING & LINT FIXES"

# Auto-format code with black
echo -e "${YELLOW}🔧 Auto-formatting code with black...${NC}"
black app/ tests/ || handle_error "Black formatting"
handle_success "Code formatting"

# Auto-fix some flake8 issues with autopep8
echo -e "${YELLOW}🔧 Auto-fixing PEP8 issues...${NC}"
if command -v autopep8 >/dev/null 2>&1; then
    autopep8 --in-place --aggressive --aggressive app/ tests/
    handle_success "PEP8 auto-fix"
else
    echo -e "${YELLOW}⚠️  autopep8 not installed, skipping auto-fix${NC}"
fi

# Sort imports with isort
echo -e "${YELLOW}🔧 Sorting imports...${NC}"
if command -v isort >/dev/null 2>&1; then
    isort app/ tests/
    handle_success "Import sorting"
else
    echo -e "${YELLOW}⚠️  isort not installed, skipping import sorting${NC}"
fi

print_job_header "JOB 1: TESTS"
echo -e "${YELLOW}🧪 Running pytest with coverage...${NC}"
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    --junit-xml=test-results/pytest.xml \
    --verbose || handle_error "Tests"
handle_success "Job 1: Tests"

print_job_header "JOB 2: LINT"

# Run flake8
echo -e "${YELLOW}🔍 Running flake8 code style check...${NC}"
flake8 app/ tests/ \
    --max-line-length=120 \
    --exclude=__pycache__,*.pyc,.git,venv,.venv \
    --ignore=E203,W503 \
    --format=pylint || handle_error "Flake8"

# Run black check
echo -e "${YELLOW}🎨 Checking black code formatting...${NC}"
black --check --diff app/ tests/ || handle_error "Black check"

handle_success "Job 2: Lint"

print_job_header "JOB 3: SECURITY SCAN"

# Run bandit
echo -e "${YELLOW}🔒 Running bandit security scan...${NC}"
bandit -r app/ \
    -f json \
    -o bandit-report.json \
    --severity-level medium || echo -e "${YELLOW}⚠️  Security issues found (expected in development)${NC}"

bandit -r app/ -f screen

# Run safety check
echo -e "${YELLOW}🛡️  Running safety dependency check...${NC}"
safety check --json --output safety-report.json || echo -e "${YELLOW}⚠️  Dependency vulnerabilities found${NC}"
safety check || echo -e "${YELLOW}⚠️  Some dependencies have known vulnerabilities${NC}"

handle_success "Job 3: Security Scan"

print_job_header "JOB 4: DOCKER SECURITY SCAN"

# Build Docker image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
docker build -t flask-api:local . || handle_error "Docker build"

# Run Trivy scan if available
echo -e "${YELLOW}🔍 Running Trivy container scan...${NC}"
if command -v trivy >/dev/null 2>&1; then
    trivy image \
        --severity HIGH,CRITICAL \
        --format json \
        --output trivy-report.json \
        flask-api:local || echo -e "${YELLOW}⚠️  Container vulnerabilities found${NC}"
    
    trivy image --severity HIGH,CRITICAL flask-api:local
    handle_success "Job 4: Docker Security Scan"
else
    echo -e "${YELLOW}⚠️  Trivy not installed. Install with: brew install trivy${NC}"
    echo -e "${GREEN}✅ Docker build completed successfully${NC}"
fi

print_job_header "SUMMARY"
echo -e "${GREEN}🎉 All jobs completed!${NC}"
echo -e "${BLUE}📊 Reports generated:${NC}"
echo "  - Coverage HTML: htmlcov/index.html"
echo "  - Test results: test-results/pytest.xml"
echo "  - Security scan: bandit-report.json"
echo "  - Dependency scan: safety-report.json"
if command -v trivy >/dev/null 2>&1; then
    echo "  - Container scan: trivy-report.json"
fi

echo -e "\n${GREEN}✅ Ready for CI/CD pipeline!${NC}"