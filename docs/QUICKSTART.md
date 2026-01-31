# Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Clone and Setup
```bash
git clone https://github.com/S3OPS/spark.git
cd spark
cp .env.example .env
```

### Step 2: Configure (Optional)
Edit `.env` and add your API keys:
```bash
# Minimum for testing (system works without these)
# none required!

# Recommended for production
OPENAI_API_KEY=sk-...        # For AI content generation
STRIPE_API_KEY=sk_test_...   # For payment processing
```

### Step 3: Run Quick Test
```bash
python3 tests/quick_start.py
```

You should see:
```
✅ CORE SYSTEM TESTS PASSED!
```

### Step 4: Install Full Dependencies (Optional)
```bash
pip install -r requirements.txt
```

### Step 5: Start the System
```bash
./scripts/start.sh
```

### Step 6: Access Dashboard
Open browser: `http://localhost:3000`

## What You Get

### Automated Revenue Engine
- ✅ Signal scanning every 6 hours
- ✅ Offer generation twice daily
- ✅ Content distribution every 2 hours
- ✅ Analytics tracking in real-time
- ✅ Auto-reinvestment at $310

### Complete System
- 🎯 Signal Compression Engine
- 💎 Micro-Offer Generator
- 🚀 Deployment Pipeline
- 📱 Distribution Automation
- 📊 Analytics Dashboard
- 💰 Revenue Tracking
- 📧 Email Automation

## Your First Hour

### Minute 0-5: Setup
```bash
git clone https://github.com/S3OPS/spark.git
cd spark
cp .env.example .env
```

### Minute 5-10: Test
```bash
python3 tests/quick_start.py
```

### Minute 10-20: Start System
```bash
./scripts/start.sh
```

### Minute 20-30: Explore Dashboard
- Open http://localhost:3000
- Click "Scan Signals"
- Click "Generate New Offers"
- View created offers

### Minute 30-40: Configure APIs (Optional)
- Add OpenAI key for better content
- Add Stripe for real payments
- Add social media APIs for distribution

### Minute 40-60: Deploy First Offer
1. Generate an offer from signals
2. Click deploy
3. Share landing page
4. Monitor conversions

## Revenue Timeline

### Days 1-3: Setup & First Offers
- ✅ System running
- ✅ 3-5 offers created
- ✅ Landing pages live
- 🎯 Goal: First sale

### Days 4-7: Validation
- ✅ Content distributed
- ✅ Traffic flowing
- ✅ Analytics tracking
- 🎯 Goal: 3-5 sales

### Days 8-14: Optimization
- ✅ Winners identified
- ✅ Losers retired
- ✅ Pricing optimized
- 🎯 Goal: $310 revenue

### Days 15-30: Scale
- ✅ Reinvestment executed
- ✅ Paid traffic running
- ✅ Bundles created
- 🎯 Goal: Path to $8.7K/month

## Common Commands

### Start System
```bash
./scripts/start.sh
```

### Stop System
```bash
./scripts/stop.sh
```

### View Logs
```bash
tail -f logs/api.log
tail -f logs/scheduler.log
```

### Run Tests
```bash
python3 tests/quick_start.py
pytest tests/
```

### Access Database
```bash
sqlite3 data/stealth_ai.db
```

### Manual Operations
```bash
# Scan signals
curl -X POST http://localhost:8000/api/signals/scan

# Generate offers
curl -X POST http://localhost:8000/api/offers/generate?batch_size=3

# Get dashboard metrics
curl http://localhost:8000/api/analytics/dashboard
```

## Troubleshooting

### System Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Install dependencies
pip install -r requirements.txt

# Check logs
cat logs/api.log
```

### No Signals Collected
- API keys not configured (optional for testing)
- Rate limits reached
- Internet connection issue
- Check logs for errors

### Offers Not Generating
- No signals in database (run scan first)
- OpenAI key not configured (uses fallback)
- Check logs for errors

### Can't Access Dashboard
- Check if services are running
- Try http://localhost:3000
- Check firewall settings

## Next Steps

### Immediate
1. Configure API keys in `.env`
2. Run signal scan
3. Generate first offers
4. Deploy and share

### This Week
1. Deploy 3-5 offers
2. Start content distribution
3. Monitor analytics
4. Optimize based on data

### This Month
1. Hit $310 revenue
2. Execute reinvestment
3. Scale winning offers
4. Build email list

## Resources

- 📖 Full Documentation: `/docs/`
- 🏗️ Architecture: `/docs/ARCHITECTURE.md`
- 🚀 Deployment: `/docs/DEPLOYMENT.md`
- ⚙️ Operations: `/docs/OPERATIONS.md`
- 📝 API Docs: `http://localhost:8000/docs`

## Support

### Documentation
- README.md - System overview
- ARCHITECTURE.md - Technical details
- OPERATIONS.md - Day-to-day operations
- DEPLOYMENT.md - Production setup

### Code Examples
- `examples/demo.py` - Workflow example
- `tests/quick_start.py` - Quick validation
- `tests/test_core.py` - Unit tests

### Get Help
1. Check documentation
2. Review examples
3. Check logs
4. Open GitHub issue

## Success Metrics

Track these in your dashboard:

✅ **System Health**
- Signals collected daily: 5+
- Offers generated weekly: 2+
- Content posts daily: 10+
- Uptime: 99%+

✅ **Revenue Progress**
- First sale: Day 1-7
- $310 milestone: Day 8-14
- $1K milestone: Day 15-21
- $8.7K monthly: Day 22-30

✅ **Performance**
- Conversion rate: 5%+
- Click-through rate: 8%+
- Email open rate: 20%+
- Customer satisfaction: 90%+

## Tips for Success

### 1. Start Simple
- Don't wait for perfect setup
- Deploy quickly, iterate fast
- Focus on one platform first

### 2. Track Everything
- Monitor all metrics
- Test variations
- Learn from data

### 3. Provide Value
- Solve real problems
- Deliver quality products
- Build trust with customers

### 4. Stay Compliant
- Follow platform rules
- No spam or shortcuts
- Build sustainable business

### 5. Iterate Fast
- Ship daily
- Test hypotheses
- Optimize continuously

## Ready to Launch?

```bash
# One command to start everything
./scripts/start.sh

# Then visit
http://localhost:3000
```

**Target:** First $310 in 14 days
**Goal:** $8.7K/month by day 30
**Strategy:** Signal → Offer → Deploy → Distribute → Scale

🚀 **Let's generate revenue!**
