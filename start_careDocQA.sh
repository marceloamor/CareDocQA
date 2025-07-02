#!/bin/bash

# ✅ CareDocQA - Complete System Startup Script
# Launches all microservices for healthcare document Q&A system
# Perfect for Emma AI technical interview demonstration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Header
echo -e "${CYAN}"
echo "✅ ==============================================="
echo "   CareDocQA - Healthcare AI Microservices"
echo "   Full-Stack System Startup"
echo "===============================================${NC}"

# Global variables for process management
DOCUMENT_SERVICE_PID=""
AI_SERVICE_PID=""
API_GATEWAY_PID=""
REACT_PID=""

# Cleanup function - kills all services on script exit
cleanup() {
    echo -e "\n${YELLOW}⏳ Shutting down CareDocQA services...${NC}"
    
    # Function to kill a service more aggressively
    kill_service() {
        local pid=$1
        local name=$2
        
        if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
            echo -e "${BLUE}⏳ Stopping $name (PID: $pid)...${NC}"
            
            # Try graceful shutdown first
            kill -TERM $pid 2>/dev/null || true
            
            # Wait a moment for graceful shutdown
            sleep 2
            
            # Check if still running
            if kill -0 $pid 2>/dev/null; then
                echo -e "${YELLOW}⏳ Force stopping $name...${NC}"
                # Kill the process group to catch child processes
                kill -KILL -$pid 2>/dev/null || true
                kill -KILL $pid 2>/dev/null || true
            fi
            
            echo -e "${GREEN}✅ $name stopped${NC}"
        fi
    }
    
    # Kill services with their PIDs
    kill_service "$REACT_PID" "React Frontend"
    kill_service "$API_GATEWAY_PID" "API Gateway" 
    kill_service "$AI_SERVICE_PID" "AI Service"
    kill_service "$DOCUMENT_SERVICE_PID" "Document Service"
    
    # Additional cleanup: kill any remaining processes on our ports
    echo -e "${YELLOW}⏳ Cleaning up ports...${NC}"
    
    # Kill processes using our specific ports
    for port in 3000 8000 5100 5000; do
        local port_pids=$(lsof -ti :$port 2>/dev/null || true)
        if [ ! -z "$port_pids" ]; then
            echo -e "${BLUE}⏳ Killing remaining processes on port $port...${NC}"
            echo "$port_pids" | xargs -r kill -KILL 2>/dev/null || true
        fi
    done
    
    # Extra cleanup: kill any Python/Node processes that might be related to our services
    echo -e "${YELLOW}⏳ Final cleanup of related processes...${NC}"
    
    # Kill any Python processes running our specific apps
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "services/.*app.py" 2>/dev/null || true
    
    # Kill any Node processes running React dev server
    pkill -f "react-scripts start" 2>/dev/null || true
    pkill -f "care-doc-qa-frontend" 2>/dev/null || true
    
    # Wait a moment for ports to be released
    sleep 1
    
    # Verify ports are free
    echo -e "${YELLOW}⏳ Verifying ports are free...${NC}"
    local ports_still_open=""
    for port in 3000 8000 5100 5000; do
        if lsof -ti :$port >/dev/null 2>&1; then
            ports_still_open="$ports_still_open $port"
        fi
    done
    
    if [ ! -z "$ports_still_open" ]; then
        echo -e "${RED}❌ Warning: Some ports still in use:$ports_still_open${NC}"
        echo -e "${YELLOW}⏳ You may need to wait a moment or restart your terminal${NC}"
    else
        echo -e "${GREEN}✅ All ports are now free${NC}"
    fi
    
    echo -e "${GREEN}✅ All services stopped cleanly${NC}"
    echo -e "${CYAN}✅ Thanks for using CareDocQA!${NC}"
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Function to check if a port is available
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use (needed for $service)${NC}"
        echo -e "${YELLOW}✅ Please stop the service using port $port and try again${NC}"
        exit 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            echo -e "${YELLOW}⏳ Still waiting for $service_name... (attempt $attempt/$max_attempts)${NC}"
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within $max_attempts seconds${NC}"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "\n${PURPLE}⏳ Checking Prerequisites...${NC}"
    
    # Check Python virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Python virtual environment not found${NC}"
        echo -e "${YELLOW}✅ Run: python -m venv venv${NC}"
        exit 1
    fi
    
    # Check if venv is activated or activate it
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}✅ Activating Python virtual environment...${NC}"
        source venv/bin/activate
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found${NC}"
        echo -e "${YELLOW}✅ Please install Node.js 18+ and try again${NC}"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found${NC}"
        echo -e "${YELLOW}✅ Please install npm and try again${NC}"
        exit 1
    fi
    
    # Check OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY environment variable not set${NC}"
        echo -e "${YELLOW}✅ Run: export OPENAI_API_KEY='your-api-key-here'${NC}"
        exit 1
    fi
    
    # Check required directories
    if [ ! -d "sample_documents" ]; then
        echo -e "${YELLOW}⚠️  sample_documents directory not found${NC}"
        echo -e "${YELLOW}✅ Some demo features may not work${NC}"
    fi
    
    echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
}

# Function to check port availability
check_ports() {
    echo -e "\n${PURPLE}⏳ Checking Port Availability...${NC}"
    
    check_port 5000 "Document Service"
    check_port 5100 "AI Service"
    check_port 8000 "API Gateway"
    check_port 3000 "React Frontend"
    
    echo -e "${GREEN}✅ All required ports are available${NC}"
}

# Function to start backend services
start_backend_services() {
    echo -e "\n${PURPLE}✅ Starting Backend Services...${NC}"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start Document Service
    echo -e "${BLUE}✅ Starting Document Service (Port 5000)...${NC}"
    cd services/document-service
    setsid python app.py > ../../logs/document-service.log 2>&1 &
    DOCUMENT_SERVICE_PID=$!
    cd ../..
    
    # Wait for Document Service
    wait_for_service "http://localhost:5000/health" "Document Service"
    
    # Start AI Service
    echo -e "${BLUE}✅ Starting AI Service (Port 5100)...${NC}"
    cd services/ai-service
    setsid python app.py > ../../logs/ai-service.log 2>&1 &
    AI_SERVICE_PID=$!
    cd ../..
    
    # Wait for AI Service
    wait_for_service "http://localhost:5100/health" "AI Service"
    
    # Start API Gateway
    echo -e "${BLUE}✅ Starting API Gateway (Port 8000)...${NC}"
    cd services/api-gateway
    setsid python app.py > ../../logs/api-gateway.log 2>&1 &
    API_GATEWAY_PID=$!
    cd ../..
    
    # Wait for API Gateway
    wait_for_service "http://localhost:8000/health" "API Gateway"
    
    echo -e "${GREEN}✅ All backend services are running!${NC}"
}

# Function to start React frontend
start_frontend() {
    echo -e "\n${PURPLE}✅ Starting React Frontend...${NC}"
    
    # Check if node_modules exists
    if [ ! -d "frontend/care-doc-qa-frontend/node_modules" ]; then
        echo -e "${YELLOW}⏳ Installing npm dependencies...${NC}"
        cd frontend/care-doc-qa-frontend
        npm install > ../../logs/npm-install.log 2>&1
        cd ../..
    fi
    
    # Start React development server
    echo -e "${BLUE}✅ Starting React Development Server (Port 3000)...${NC}"
    cd frontend/care-doc-qa-frontend
    setsid npm start > ../../logs/react-frontend.log 2>&1 &
    REACT_PID=$!
    cd ../..
    
    # Wait for React to be ready
    wait_for_service "http://localhost:3000" "React Frontend"
    
    echo -e "${GREEN}✅ React frontend is running!${NC}"
}

# Function to show system status
show_system_status() {
    echo -e "\n${CYAN}✅ System Status Dashboard${NC}"
    echo "=============================================="
    echo -e "${GREEN}✅ Document Service:${NC}  http://localhost:5000 (PID: $DOCUMENT_SERVICE_PID)"
    echo -e "${GREEN}✅ AI Service:${NC}        http://localhost:5100 (PID: $AI_SERVICE_PID)"
    echo -e "${GREEN}✅ API Gateway:${NC}       http://localhost:8000 (PID: $API_GATEWAY_PID)"
    echo -e "${GREEN}✅ React Frontend:${NC}    http://localhost:3000 (PID: $REACT_PID)"
    echo "=============================================="
}

# Function to show usage instructions
show_usage_instructions() {
    echo -e "\n${CYAN}✅ Ready for Emma AI Interview Demo!${NC}"
    echo "=============================================="
    echo -e "${YELLOW}✅ Open your browser:${NC} http://localhost:3000"
    echo -e "${YELLOW}✅ API Documentation:${NC} http://localhost:8000/docs"
    echo ""
    echo -e "${PURPLE}✅ Demo Healthcare Use Cases:${NC}"
    echo "1. Upload 'care_plan_mrs_wilson.txt'"
    echo "   Ask: 'What medications does Mrs Wilson take?'"
    echo ""
    echo "2. Upload 'emergency_procedures.txt'" 
    echo "   Ask: 'What should I do if there's a fire?'"
    echo ""
    echo "3. Upload 'dementia_care_guidelines.txt'"
    echo "   Ask: 'How should I communicate with dementia patients?'"
    echo ""
    echo -e "${CYAN}✅ Key Features to Highlight:${NC}"
    echo "• Microservice Architecture (3 backend services + React)"
    echo "• API Gateway Pattern with service orchestration"
    echo "• Real-time AI responses with cost tracking"
    echo "• Healthcare-focused UI/UX design"
    echo "• Full-stack integration (Python + React)"
    echo ""
    echo -e "${YELLOW}✅ Management:${NC}"
    echo "• Press Ctrl+C to stop all services"
    echo "• Logs are in ./logs/ directory"
    echo "• Clear database: python clear_database.py"
    echo "=============================================="
}

# Function to create logs directory
setup_logging() {
    mkdir -p logs
    echo -e "${BLUE}✅ Logs will be saved to ./logs/ directory${NC}"
}

# Main execution flow
main() {
    # Setup
    setup_logging
    check_prerequisites
    check_ports
    
    # Start services
    start_backend_services
    start_frontend
    
    # Show status and instructions
    show_system_status
    show_usage_instructions
    
    # Keep script running and monitor services
    echo -e "\n${GREEN}✅ CareDocQA is fully operational!${NC}"
    echo -e "${YELLOW}⏳ Press Ctrl+C to stop all services...${NC}"
    
    # Monitor services
    while true; do
        # Check if any service has died
        if ! kill -0 $DOCUMENT_SERVICE_PID 2>/dev/null; then
            echo -e "${RED}❌ Document Service has stopped unexpectedly${NC}"
            break
        fi
        
        if ! kill -0 $AI_SERVICE_PID 2>/dev/null; then
            echo -e "${RED}❌ AI Service has stopped unexpectedly${NC}"
            break
        fi
        
        if ! kill -0 $API_GATEWAY_PID 2>/dev/null; then
            echo -e "${RED}❌ API Gateway has stopped unexpectedly${NC}"
            break
        fi
        
        if ! kill -0 $REACT_PID 2>/dev/null; then
            echo -e "${RED}❌ React Frontend has stopped unexpectedly${NC}"
            break
        fi
        
        sleep 5
    done
}

# Run main function
main 