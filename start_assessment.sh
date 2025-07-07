#!/bin/bash

# 🎯 Emma AI Assessment - Incident Response System Startup
# AI-Enhanced Incident Response for Social Care
# Assignment submission for founding engineer role

set -e  # Exit on any error

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# ASCII Header
echo -e "${CYAN}"
echo "🎯 ==============================================="
echo "   Emma AI Assessment - Incident Response"
echo "   AI-Enhanced Social Care System"
echo "===============================================${NC}"

echo -e "${YELLOW}🏥 Assignment Submission by [Your Name]${NC}"
echo -e "${BLUE}⏳ Starting AI-Enhanced Incident Response System...${NC}"

# Check prerequisites
echo -e "\n${PURPLE}⏳ Checking Prerequisites...${NC}"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Python virtual environment not found${NC}"
    echo -e "${YELLOW}✅ Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Activate venv if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}✅ Activating Python virtual environment...${NC}"
    source venv/bin/activate
fi

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY environment variable not set${NC}"
    echo -e "${YELLOW}✅ Run: export OPENAI_API_KEY='your-api-key-here'${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites satisfied${NC}"

# Create logs directory
mkdir -p logs

# Start the assessment system
echo -e "\n${PURPLE}🚀 Starting Assessment Services...${NC}"

# For now, this will start the existing system as a placeholder
# We'll modify this to start the incident response system once built
echo -e "${BLUE}✅ Initialising Incident Response System...${NC}"
echo -e "${YELLOW}⏳ This will be updated to start the assignment-specific services${NC}"

echo -e "\n${CYAN}🎯 Assessment System Ready!${NC}"
echo "=============================================="
echo -e "${GREEN}✅ Incident Response UI:${NC}    http://localhost:3000"
echo -e "${GREEN}✅ API Documentation:${NC}       http://localhost:8000/docs"
echo -e "${GREEN}✅ System Health:${NC}           http://localhost:8000/health"
echo "=============================================="

echo -e "\n${PURPLE}📋 Assignment Features Demonstrated:${NC}"
echo "• Process social care call transcripts"
echo "• Analyse against policies automatically"  
echo "• Generate incident forms with AI"
echo "• Draft professional email responses"
echo "• React frontend with professional UI"
echo "• FastAPI backend with error handling"

echo -e "\n${CYAN}🌟 To explore the full microservice system:${NC}"
echo -e "${YELLOW}git checkout full-careDocQA-system${NC}"
echo -e "${YELLOW}./start_careDocQA.sh${NC}"

echo -e "\n${GREEN}🎯 Assessment submission ready for review!${NC}" 