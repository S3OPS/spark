# System Architecture

## Overview

The Stealth AI Revenue System is a modular, event-driven architecture designed for automated revenue generation through signal analysis and micro-offer deployment.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Data Sources                     │
├─────────────────────────────────────────────────────────────────┤
│  Twitter API  │  Reddit API  │  Marketplaces  │  Other Sources  │
└─────────────┬───────────────┴────────────────┴─────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Signal Compression Engine                     │
├─────────────────────────────────────────────────────────────────┤
│  • Data Collection         • Signal Analysis                     │
│  • Trend Detection         • Scoring Algorithm                   │
│  • Pain Point Extraction   • Opportunity Ranking                │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Micro-Offer Generator                        │
├─────────────────────────────────────────────────────────────────┤
│  • AI Content Generation   • Template Selection                 │
│  • Pricing Optimization    • Product Metadata                   │
│  • Quality Validation      • Type Classification                │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Deployment Pipeline                         │
├─────────────────────────────────────────────────────────────────┤
│  • Landing Page Gen        • Payment Integration                │
│  • A/B Testing Setup       • Analytics Tracking                 │
│  • URL Generation          • Offer Activation                   │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ├──────────────────┬──────────────────┬─────────────┐
              ▼                  ▼                  ▼             ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌─────────┐
│ Distribution     │  │ Analytics &      │  │ Scaling      │  │ Email   │
│ Automation       │  │ Tracking         │  │ Engine       │  │ Auto    │
├──────────────────┤  ├──────────────────┤  ├──────────────┤  ├─────────┤
│ • Twitter        │  │ • Impressions    │  │ • Winners    │  │ • Seqs  │
│ • Reddit         │  │ • Clicks         │  │ • Reinvest   │  │ • Segs  │
│ • LinkedIn       │  │ • Conversions    │  │ • Upsells    │  │ • CLV   │
│ • Scheduling     │  │ • Revenue        │  │ • Bundles    │  │ • Flows │
└──────────────────┘  └──────────────────┘  └──────────────┘  └─────────┘
              │                  │                  │             │
              └──────────────────┴──────────────────┴─────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   SQLite Database      │
                    ├────────────────────────┤
                    │ • Signals              │
                    │ • Offers               │
                    │ • Analytics            │
                    │ • Revenue              │
                    │ • Subscribers          │
                    └────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  FastAPI Backend       │
                    │  (RESTful API)         │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Web Dashboard         │
                    │  (HTML/CSS/JS)         │
                    └────────────────────────┘
```

## Component Details

### 1. Signal Compression Engine
**Purpose:** Identify high-conversion opportunities from minimal data

**Key Classes:**
- `SignalCompressor`: Main orchestrator
- `TwitterSignalCollector`: Twitter API integration
- `RedditSignalCollector`: Reddit API integration
- `MarketplaceSignalCollector`: Marketplace scraping

**Data Flow:**
1. Collect raw data from APIs
2. Extract pain points and trends
3. Calculate confidence, conversion potential, speed-to-market scores
4. Compute weighted overall score
5. Store in database, ranked by score

**Scoring Algorithm:**
```python
overall_score = (
    confidence_score × 0.3 +
    conversion_potential × 0.5 +
    speed_to_market × 0.2
)
```

### 2. Micro-Offer Generator
**Purpose:** Create digital products from signals

**Key Classes:**
- `OfferGenerator`: Main generator
- Template generators for each offer type

**Offer Types:**
- Guides (PDF/eBook)
- Templates (Notion/Sheets)
- Tools (Scripts/Extensions)
- Mini-courses (Email series)
- Resource lists (Curated collections)

**Pricing Strategy:**
- Base prices: $10-$50 range
- Adjusted by deliverables count
- Optimized for rapid validation

### 3. Deployment Pipeline
**Purpose:** Automate offer deployment

**Key Classes:**
- `DeploymentPipeline`: Deployment orchestrator
- `AnalyticsTracker`: Performance tracking

**Process:**
1. Generate landing page HTML
2. Create payment link (Stripe/Gumroad)
3. Set up analytics tracking
4. Activate offer
5. Return URLs

**Landing Page Features:**
- Conversion-optimized design
- Mobile responsive
- Payment integration
- Analytics tracking
- A/B test ready

### 4. Distribution Automation
**Purpose:** Distribute content across platforms

**Key Classes:**
- `ContentGenerator`: AI-powered content creation
- `DistributionScheduler`: Scheduling manager
- Platform-specific posters (Twitter, Reddit, LinkedIn)

**Content Types:**
- Twitter: Threaded promotions
- Reddit: Value-add posts
- LinkedIn: Professional posts
- Video: Short-form scripts

**Compliance:**
- Respects platform ToS
- Rate limiting
- Value-first approach
- No spam

### 5. Analytics & Tracking
**Purpose:** Monitor performance

**Metrics Tracked:**
- Impressions (page views)
- Clicks (CTA clicks)
- Conversions (purchases)
- Revenue (total/net)
- Conversion rates
- Customer lifetime value

**Real-time Calculations:**
- CTR = clicks / impressions
- Conversion rate = conversions / clicks
- Net profit = revenue - fees

### 6. Scaling Engine
**Purpose:** Automated growth decisions

**Key Classes:**
- `ScalingEngine`: Scaling orchestrator
- `RevenuePredictor`: Revenue forecasting
- `UpsellFunnel`: Funnel management
- `EmailAutomation`: Email sequences

**Automation Rules:**
- Identify winners (>5% conversion)
- Execute reinvestment at $310
- Create product bundles
- Build upsell sequences
- Optimize pricing

### 7. Email Automation
**Purpose:** Maximize customer lifetime value

**Sequences:**
- Welcome series (6 emails)
- Onboarding
- Cross-sell campaigns
- Re-engagement
- Testimonial requests

**Segmentation:**
- High-value customers
- Engaged subscribers
- Dormant users
- New subscribers

## Data Models

### Signal
```python
{
    "id": int,
    "source": str,  # twitter, reddit, marketplace
    "signal_type": str,  # pain_point, trend, opportunity
    "content": str,
    "confidence_score": float,  # 0-1
    "conversion_potential": float,  # 0-1
    "speed_to_market": float,  # 0-1
    "overall_score": float,  # weighted average
    "status": str  # new, processed, converted
}
```

### MicroOffer
```python
{
    "id": int,
    "signal_id": int,
    "title": str,
    "description": str,
    "offer_type": str,  # guide, template, tool, course
    "price": float,  # 10-50
    "content": dict,  # product details
    "landing_page_url": str,
    "payment_link": str,
    "status": str  # draft, active, paused
}
```

### Analytics
```python
{
    "id": int,
    "offer_id": int,
    "impressions": int,
    "clicks": int,
    "conversions": int,
    "revenue": float,
    "conversion_rate": float
}
```

## API Endpoints

### Signals
- `POST /api/signals/scan` - Trigger signal scan
- `GET /api/signals` - List signals
- `GET /api/signals/{id}` - Get signal details

### Offers
- `POST /api/offers/generate` - Generate offers
- `GET /api/offers` - List offers
- `GET /api/offers/{id}` - Get offer details
- `POST /api/offers/{id}/deploy` - Deploy offer

### Distribution
- `POST /api/offers/{id}/distribute` - Schedule distribution
- `POST /api/distribution/post-scheduled` - Post scheduled content

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/offers/{id}` - Offer analytics

### Scaling
- `GET /api/scaling/winners` - Get winning offers
- `POST /api/scaling/reinvest` - Execute reinvestment

## Automation Schedule

```python
# Signal scanning
every(6).hours.do(scan_signals)

# Offer generation
every().day.at("09:00").do(generate_offers)
every().day.at("15:00").do(generate_offers)

# Content posting
every(2).hours.do(post_content)

# Reinvestment check
every().hour.do(check_reinvestment)

# Daily report
every().day.at("08:00").do(daily_report)
```

## Tech Stack

**Backend:**
- Python 3.8+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- SQLite/PostgreSQL (database)

**AI/ML:**
- OpenAI GPT (content generation)
- Anthropic Claude (alternative)
- Sentence transformers (embeddings)

**Data Collection:**
- httpx (HTTP client)
- BeautifulSoup (scraping)
- Tweepy (Twitter)
- PRAW (Reddit)

**Payment:**
- Stripe (primary)
- PayPal (alternative)

**Frontend:**
- Vanilla HTML/CSS/JS
- No framework dependencies
- Mobile responsive

**Automation:**
- APScheduler (task scheduling)
- Celery (background tasks - optional)

## Deployment

**Development:**
```bash
./scripts/start.sh
```

**Production Options:**
1. VPS (DigitalOcean, Linode)
2. Railway.app (PaaS)
3. Heroku
4. Docker containers

**Requirements:**
- 1 GB RAM minimum
- 10 GB storage
- Python 3.8+
- SSL certificate

## Security

**Best Practices:**
- Environment variables for secrets
- API key rotation
- Rate limiting
- Input validation
- SQL injection prevention
- HTTPS only in production

**Compliance:**
- Platform ToS adherence
- GDPR considerations
- Payment security (PCI)
- Data privacy

## Monitoring

**Metrics:**
- System uptime
- API response times
- Database performance
- Revenue tracking
- Conversion funnels

**Tools:**
- Built-in dashboard
- Log files
- Database queries
- External: UptimeRobot, Sentry

## Scaling Strategy

**Vertical:**
- Increase server resources
- Optimize database queries
- Add caching (Redis)

**Horizontal:**
- Load balancer
- Multiple API instances
- Database replication
- CDN for static files

## Future Enhancements

1. **Advanced AI**
   - Custom LLM fine-tuning
   - Better signal analysis
   - Predictive modeling

2. **More Platforms**
   - TikTok integration
   - YouTube automation
   - Instagram posts

3. **Enhanced Analytics**
   - ML-powered insights
   - Cohort analysis
   - Attribution modeling

4. **Scaling Features**
   - Affiliate system
   - Referral tracking
   - Community building

5. **Optimization**
   - Advanced A/B testing
   - Multivariate testing
   - Dynamic pricing
