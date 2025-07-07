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

echo -e "${YELLOW}🏥 Assignment Submission${NC}"
echo -e "${BLUE}⏳ Starting AI-Enhanced Incident Response System...${NC}"

# Check prerequisites
echo -e "\n${PURPLE}🔍 Checking Prerequisites...${NC}"

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Python virtual environment not found. Please run:${NC}"
    echo -e "${YELLOW}   python -m venv venv${NC}"
    echo -e "${YELLOW}   source venv/bin/activate${NC}"
    echo -e "${YELLOW}   pip install -r requirements.txt${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Check OpenAI API key (from .env file or environment)
if [ -f ".env" ] && grep -q "OPENAI_API_KEY=" .env; then
    echo -e "${GREEN}✅ OpenAI API key found in .env file${NC}"
elif [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ OpenAI API key configured in environment${NC}"
else
    echo -e "${RED}❌ OpenAI API key not found. Please:${NC}"
    echo -e "${YELLOW}   1. Add OPENAI_API_KEY=your-key to .env file, OR${NC}"
    echo -e "${YELLOW}   2. Run: export OPENAI_API_KEY='your-api-key-here'${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found: $(npm --version)${NC}"

# Check ports availability
echo -e "\n${PURPLE}🔌 Checking Port Availability...${NC}"

check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use (needed for $service)${NC}"
        echo -e "${YELLOW}   Please run: ./kill_ports.sh${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Port $port is available for $service${NC}"
    fi
}

check_port 5001 "incident-processor"
check_port 8000 "api-gateway"
check_port 3000 "react-frontend"

# Create logs directory
mkdir -p logs

# Function to start a service and wait for it to be healthy
start_service() {
    local service_name=$1
    local service_dir=$2
    local service_port=$3
    local health_endpoint=$4
    local start_command=$5
    
    echo -e "\n${BLUE}🚀 Starting $service_name...${NC}"
    
    cd "$service_dir"
    nohup $start_command > "../../logs/${service_name}.log" 2>&1 &
    local pid=$!
    cd - > /dev/null
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to start (PID: $pid)...${NC}"
    
    # Wait up to 30 seconds for service to become healthy
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$health_endpoint" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy and ready${NC}"
            return 0
        fi
        
        sleep 1
        attempt=$((attempt + 1))
        
        # Show progress every 5 seconds
        if [ $((attempt % 5)) -eq 0 ]; then
            echo -e "${YELLOW}   Still waiting for $service_name... (${attempt}/${max_attempts})${NC}"
        fi
        
        # Check if process is still running
        if ! kill -0 $pid 2>/dev/null; then
            echo -e "${RED}❌ $service_name process died. Check logs/${service_name}.log${NC}"
            return 1
        fi
    done
    
    echo -e "${RED}❌ $service_name failed to start within ${max_attempts} seconds${NC}"
    echo -e "${YELLOW}   Check logs/${service_name}.log for details${NC}"
    return 1
}

# Start backend services
echo -e "\n${CYAN}🔥 STARTING BACKEND SERVICES${NC}"

# Start Incident Processor Service
start_service "incident-processor" "services/incident-processor" 5001 "http://localhost:5001/health" "python app.py"

# Start API Gateway
start_service "api-gateway" "services/api-gateway" 8000 "http://localhost:8000/health" "python app.py"

# Start React Frontend
echo -e "\n${CYAN}🔥 STARTING REACT FRONTEND${NC}"

cd frontend/care-doc-qa-frontend

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing npm dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}✅ npm dependencies installed${NC}"
else
    echo -e "${GREEN}✅ npm dependencies already installed${NC}"
fi

# Start React development server
echo -e "\n${BLUE}🚀 Starting React Frontend...${NC}"
nohup npm start > "../../logs/react-frontend.log" 2>&1 &
REACT_PID=$!

cd ../..

# Wait for React to start
echo -e "${YELLOW}⏳ Waiting for React frontend to start...${NC}"
sleep 10

# Check if React is running
if curl -s "http://localhost:3000" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ React frontend is ready${NC}"
else
    echo -e "${YELLOW}⏳ React is still starting up (this can take a minute)...${NC}"
fi

# Final system check
echo -e "\n${CYAN}🩺 SYSTEM HEALTH CHECK${NC}"

health_check() {
    local service=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $service: Unhealthy${NC}"
        return 1
    fi
}

health_check "Incident Processor" "http://localhost:5001/health"
health_check "API Gateway" "http://localhost:8000/health"
health_check "React Frontend" "http://localhost:3000"

# Success message
echo -e "\n${GREEN}🎉 AI-ENHANCED INCIDENT RESPONSE SYSTEM READY!${NC}"
echo -e "\n${CYAN}📱 ACCESS POINTS:${NC}"
echo -e "${YELLOW}   🌐 Main Application: http://localhost:3000${NC}"
echo -e "${YELLOW}   🔧 API Gateway: http://localhost:8000${NC}"
echo -e "${YELLOW}   📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}   🧠 Incident Processor: http://localhost:5001${NC}"

echo -e "\n${CYAN}🎯 ASSIGNMENT FEATURES:${NC}"
echo -e "${GREEN}   ✅ Policy-driven incident analysis${NC}"
echo -e "${GREEN}   ✅ Automated incident report generation${NC}"
echo -e "${GREEN}   ✅ Professional email drafting${NC}"
echo -e "${GREEN}   ✅ Natural language policy Q&A${NC}"
echo -e "${GREEN}   ✅ Document editing with feedback${NC}"
echo -e "${GREEN}   ✅ Cross-document consistency updates${NC}"

echo -e "\n${CYAN}📝 HOW TO USE:${NC}"
echo -e "${YELLOW}   1. Open http://localhost:3000 in your browser${NC}"
echo -e "${YELLOW}   2. Ask policy questions or paste a call transcript${NC}"
echo -e "${YELLOW}   3. System automatically analyzes and generates documents${NC}"
echo -e "${YELLOW}   4. Edit generated content with natural language feedback${NC}"

echo -e "\n${CYAN}📋 SAMPLE TRANSCRIPT TO TEST:${NC}"
echo -e "${YELLOW}   Paste this into the chat for instant analysis:${NC}"
echo -e "${BLUE}   Julie Peaterson: 'Good morning, how can I help you?'${NC}"
echo -e "${BLUE}   Greg Jones: 'Hi, I've fallen again this week...'${NC}"

echo -e "\n${PURPLE}🔄 To stop all services: Press Ctrl+C then run ./kill_ports.sh${NC}"

# Keep script running and monitor services
echo -e "\n${YELLOW}⏳ Monitoring services... (Press Ctrl+C to stop)${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Stopping services...${NC}"
    
    # Kill all background processes started by this script
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Additional cleanup for specific processes
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Monitor loop
while true; do
    sleep 5
    
    # Check if critical services are still running
    if ! curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ API Gateway appears to be down${NC}"
        echo -e "${YELLOW}   Check logs/api-gateway.log for details${NC}"
    fi
    
    if ! curl -s "http://localhost:5001/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ Incident Processor appears to be down${NC}"
        echo -e "${YELLOW}   Check logs/incident-processor.log for details${NC}"
    fi
done 