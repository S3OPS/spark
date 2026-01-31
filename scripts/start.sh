#!/bin/bash

# Stealth AI System - Full Start Script
# Starts all components of the system

echo "🚀 Starting Stealth AI Revenue System..."

# Create necessary directories
mkdir -p data/signals data/offers data/analytics
mkdir -p frontend/public/pages
mkdir -p logs

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before running!"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from backend.database.models import init_db; init_db(); print('✅ Database initialized')"

# Start the API server in the background
echo "🌐 Starting API server..."
python3 backend/api/main.py > logs/api.log 2>&1 &
API_PID=$!
echo "   API server PID: $API_PID"

# Wait for API to start
sleep 3

# Start the scheduler in the background
echo "⏰ Starting automation scheduler..."
python3 scripts/scheduler.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "   Scheduler PID: $SCHEDULER_PID"

# Start a simple HTTP server for the dashboard
echo "📊 Starting dashboard..."
cd frontend/public && python3 -m http.server 3000 > ../../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
cd ../..
echo "   Dashboard PID: $DASHBOARD_PID"

echo ""
echo "✅ All systems online!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🌐 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   API: tail -f logs/api.log"
echo "   Scheduler: tail -f logs/scheduler.log"
echo "   Dashboard: tail -f logs/dashboard.log"
echo ""
echo "🛑 To stop all services, run: ./scripts/stop.sh"
echo ""

# Save PIDs for later
echo "$API_PID" > .pids
echo "$SCHEDULER_PID" >> .pids
echo "$DASHBOARD_PID" >> .pids

# Keep script running
wait
