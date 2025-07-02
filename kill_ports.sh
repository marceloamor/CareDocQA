#!/bin/bash

# ❌ CareDocQA Port Killer - Emergency Cleanup Script
# Use this if the main startup script doesn't clean up properly

echo "❌ Emergency CareDocQA Port Cleanup"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill processes on our ports
echo -e "${YELLOW}⏳ Killing processes on CareDocQA ports...${NC}"

ports=(3000 8000 5100 5000)
for port in "${ports[@]}"; do
    echo -e "${YELLOW}⏳ Checking port $port...${NC}"
    
    # Get PIDs using the port
    port_pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ ! -z "$port_pids" ]; then
        echo -e "${RED}❌ Killing processes on port $port: $port_pids${NC}"
        echo "$port_pids" | xargs -r kill -KILL 2>/dev/null || true
        sleep 1
        
        # Check if port is now free
        if ! lsof -ti :$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Port $port is now free${NC}"
        else
            echo -e "${RED}❌ Port $port still in use${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port $port is already free${NC}"
    fi
done

# Kill specific process patterns
echo -e "\n${YELLOW}⏳ Killing CareDocQA-related processes...${NC}"

# Python services
pkill -f "python.*app.py" 2>/dev/null && echo -e "${GREEN}✅ Killed Python services${NC}" || true
pkill -f "services/.*app.py" 2>/dev/null || true

# React dev server
pkill -f "react-scripts start" 2>/dev/null && echo -e "${GREEN}✅ Killed React dev server${NC}" || true
pkill -f "care-doc-qa-frontend" 2>/dev/null || true

# Additional Node processes that might be hanging
pkill -f "node.*start" 2>/dev/null || true

echo -e "\n${YELLOW}⏳ Final verification...${NC}"

# Check final status
all_clear=true
for port in "${ports[@]}"; do
    if lsof -ti :$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port still in use${NC}"
        all_clear=false
    fi
done

if [ "$all_clear" = true ]; then
    echo -e "\n${GREEN}✅ SUCCESS: All CareDocQA ports are now free!${NC}"
    echo -e "${GREEN}✅ You can now restart the system with: ./start_careDocQA.sh${NC}"
else
    echo -e "\n${RED}❌ Some ports are still in use${NC}"
    echo -e "${YELLOW}⏳ You may need to wait a moment or restart your terminal${NC}"
    echo -e "${YELLOW}⏳ Or try: sudo lsof -ti :<port> | xargs sudo kill -9${NC}"
fi

echo "==================================" 