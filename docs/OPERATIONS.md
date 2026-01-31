# Operation Manual

## Daily Operations

### Morning Routine (8:00 AM)
1. Check daily report in console/logs
2. Review dashboard metrics at http://localhost:3000
3. Analyze winning offers (>5% conversion rate)
4. Review scheduled content for the day

### Throughout the Day
- Monitor revenue tracking
- Respond to system alerts
- Check email subscriber growth
- Review content performance

### Evening Review (6:00 PM)
1. Assess daily revenue vs. target
2. Review new signals collected
3. Check offers deployed
4. Plan next day's focus

## Weekly Tasks

### Monday
- Review weekend performance
- Analyze week's goals
- Adjust automation settings if needed

### Wednesday
- Mid-week checkpoint
- Review A/B test results
- Optimize underperforming offers

### Friday
- Weekly revenue report
- Plan weekend content
- Schedule next week's offer generation

### Sunday
- Week-in-review analysis
- Strategic planning for next week
- Review and update email sequences

## Monthly Operations

### First Week
- **Revenue Analysis**: Compare to $8.7K target
- **Offer Audit**: Identify winners and losers
- **Content Review**: Best performing posts
- **Email List**: Segment and clean list

### Second Week
- **Scaling**: Execute reinvestment if threshold met
- **New Strategies**: Test new platforms or angles
- **Product Suites**: Bundle successful offers

### Third Week
- **Optimization**: Improve conversion funnels
- **Pricing Tests**: A/B test price points
- **Distribution**: Expand to new platforms

### Fourth Week
- **Monthly Report**: Full performance analysis
- **Strategy Adjustment**: Plan next month
- **System Maintenance**: Update dependencies

## Troubleshooting

### System Not Starting
```bash
# Check logs
tail -f logs/api.log
tail -f logs/scheduler.log

# Verify dependencies
pip install -r requirements.txt

# Reinitialize database
python -c "from backend.database.models import init_db; init_db()"
```

### No Signals Being Collected
- Check API keys in `.env`
- Verify internet connection
- Check rate limits on APIs
- Review error logs

### Offers Not Generating
- Ensure signals exist in database
- Check OpenAI API key and credits
- Verify offer generation settings
- Check database permissions

### Payment Processing Issues
- Verify Stripe API key
- Check webhook configuration
- Test with Stripe test mode first
- Review Stripe dashboard for errors

### Content Not Posting
- Check `CONTENT_POSTING_ENABLED=True` in `.env`
- Verify platform API credentials
- Review platform rate limits
- Check scheduled post status in database

## Performance Optimization

### Speed Up Signal Collection
- Increase concurrent API requests
- Cache frequently accessed data
- Use database indexing
- Optimize scraping selectors

### Improve Conversion Rates
- A/B test landing page designs
- Optimize pricing points
- Improve offer descriptions
- Add social proof
- Test different CTAs

### Scale Revenue
1. Identify 2-3 winning offers
2. Increase distribution frequency
3. Add paid traffic
4. Create upsell sequences
5. Build email automation

## Automation Tuning

### Adjust Signal Scanning Frequency
Edit `.env`:
```
SIGNAL_SCAN_INTERVAL_HOURS=4  # Scan every 4 hours instead of 6
```

### Modify Content Posting Schedule
Edit `scripts/scheduler.py`:
```python
# Post every hour instead of every 2 hours
schedule.every(1).hours.do(lambda: run_async_job(job_post_content))
```

### Change Conversion Threshold
Edit `.env`:
```
MIN_CONVERSION_THRESHOLD=0.03  # Lower threshold to 3%
```

### Adjust Reinvestment Amount
Edit `.env`:
```
AUTO_REINVEST_THRESHOLD=500  # Increase to $500
```

## Security Best Practices

1. **Never commit `.env` file**
   - Always in `.gitignore`
   - Keep separate for dev/prod

2. **Rotate API Keys Monthly**
   - Update all platform credentials
   - Test after rotation

3. **Monitor API Usage**
   - Check for unexpected spikes
   - Set up billing alerts

4. **Backup Database Weekly**
   ```bash
   cp data/stealth_ai.db backups/stealth_ai_$(date +%Y%m%d).db
   ```

5. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install -U package_name
   ```

## Scaling Playbook

### From $0 to $310 (Days 1-14)
- Deploy 3-5 offers
- Post 2-3 times daily
- Focus on organic distribution
- Optimize based on early data

### From $310 to $1K (Days 15-21)
- Execute reinvestment
- Start paid traffic testing
- Build email sequences
- Create first product bundle

### From $1K to $5K (Days 22-30)
- Scale winning offers
- Expand to new platforms
- Increase content frequency
- Build community/audience

### From $5K to $8.7K (Days 31-45)
- Optimize conversion funnels
- Maximize customer lifetime value
- Add premium tier products
- Build referral system

## Emergency Procedures

### System Crash
1. Stop all services: `./scripts/stop.sh`
2. Check logs for errors
3. Backup database
4. Restart: `./scripts/start.sh`

### Revenue Drop
1. Check offer availability
2. Verify payment processing
3. Review traffic sources
4. Analyze conversion funnel

### API Rate Limits Hit
1. Reduce request frequency
2. Implement exponential backoff
3. Consider upgrading API tier
4. Cache more aggressively

### Database Corruption
1. Stop all services
2. Restore from backup
3. Verify data integrity
4. Restart services

## Metrics to Watch

### Daily
- Revenue
- Conversions
- Traffic/Impressions
- Email subscribers

### Weekly
- Conversion rate trends
- Top performing offers
- Content engagement
- Email open rates

### Monthly
- Revenue vs. target ($8.7K)
- Customer acquisition cost
- Lifetime value
- Refund rate

## Success Indicators

✅ **Healthy System**
- 5+ signals collected daily
- 2+ offers deployed weekly
- 10+ posts scheduled
- 5%+ conversion rate on winners
- $100+ daily revenue

⚠️ **Needs Attention**
- <3 signals daily
- 0 new offers this week
- <2% conversion rate
- $0 revenue in 48 hours

🚨 **Critical Issues**
- 0 signals in 24 hours
- All offers offline
- No scheduled content
- Payment processing down
