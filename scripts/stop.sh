#!/bin/bash

# Stealth AI System - Stop Script
# Stops all running services

echo "🛑 Stopping Stealth AI Revenue System..."

if [ -f ".pids" ]; then
    while read pid; do
        if ps -p $pid > /dev/null; then
            echo "   Stopping process $pid..."
            kill $pid
        fi
    done < .pids
    
    rm .pids
    echo "✅ All services stopped"
else
    echo "⚠️  No PID file found. Services may not be running."
fi
