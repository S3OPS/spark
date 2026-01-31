"""
FastAPI Main Application
API endpoints for the Stealth AI Revenue System
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn

from backend.database.models import (
    Signal, MicroOffer, Analytics, DistributionPost,
    Revenue, EmailSubscriber, get_db, init_db
)
from backend.services.signal_compression import SignalCompressor, run_signal_scan
from backend.services.offer_generator import OfferGenerator
from backend.services.deployment import DeploymentPipeline, AnalyticsTracker
from backend.services.distribution import DistributionScheduler, ContentGenerator
from backend.services.scaling import ScalingEngine, RevenuePredictor, UpsellFunnel, EmailAutomation
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Stealth AI Revenue System",
    description="Automated revenue generation through signal compression and micro-offers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


# ==================== Signal Compression Endpoints ====================

@app.post("/api/signals/scan")
async def scan_signals(background_tasks: BackgroundTasks):
    """Trigger a signal scan across all platforms"""
    background_tasks.add_task(run_signal_scan)
    return {"status": "Signal scan initiated"}


@app.get("/api/signals")
async def get_signals(
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get signals with optional filtering"""
    query = db.query(Signal)
    
    if status:
        query = query.filter(Signal.status == status)
    
    signals = query.order_by(Signal.overall_score.desc()).limit(limit).all()
    
    return {
        "signals": [
            {
                "id": s.id,
                "source": s.source,
                "signal_type": s.signal_type,
                "content": s.content[:200],
                "confidence_score": s.confidence_score,
                "conversion_potential": s.conversion_potential,
                "overall_score": s.overall_score,
                "status": s.status,
                "created_at": s.created_at
            }
            for s in signals
        ]
    }


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: int, db: Session = Depends(get_db)):
    """Get detailed signal information"""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return {
        "id": signal.id,
        "source": signal.source,
        "signal_type": signal.signal_type,
        "content": signal.content,
        "compressed_data": signal.compressed_data,
        "confidence_score": signal.confidence_score,
        "conversion_potential": signal.conversion_potential,
        "speed_to_market": signal.speed_to_market,
        "overall_score": signal.overall_score,
        "status": signal.status,
        "created_at": signal.created_at
    }


# ==================== Offer Generation Endpoints ====================

@app.post("/api/offers/generate")
async def generate_offers(
    signal_id: Optional[int] = None,
    batch_size: int = 3,
    db: Session = Depends(get_db)
):
    """Generate micro-offers from signals"""
    generator = OfferGenerator()
    
    if signal_id:
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        offer = await generator.generate_from_signal(signal)
        return {"offer": {"id": offer.id, "title": offer.title}}
    
    else:
        offers = await generator.generate_batch(batch_size)
        return {
            "offers": [
                {"id": o.id, "title": o.title, "price": o.price}
                for o in offers
            ]
        }


@app.get("/api/offers")
async def get_offers(
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all offers"""
    query = db.query(MicroOffer)
    
    if status:
        query = query.filter(MicroOffer.status == status)
    
    offers = query.order_by(MicroOffer.created_at.desc()).limit(limit).all()
    
    return {
        "offers": [
            {
                "id": o.id,
                "title": o.title,
                "description": o.description,
                "offer_type": o.offer_type,
                "price": o.price,
                "status": o.status,
                "landing_page_url": o.landing_page_url,
                "payment_link": o.payment_link,
                "created_at": o.created_at,
                "deployed_at": o.deployed_at
            }
            for o in offers
        ]
    }


@app.get("/api/offers/{offer_id}")
async def get_offer(offer_id: int, db: Session = Depends(get_db)):
    """Get detailed offer information"""
    offer = db.query(MicroOffer).filter(MicroOffer.id == offer_id).first()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Get analytics
    tracker = AnalyticsTracker()
    metrics = tracker.get_offer_metrics(offer_id)
    
    return {
        "id": offer.id,
        "title": offer.title,
        "description": offer.description,
        "offer_type": offer.offer_type,
        "price": offer.price,
        "content": offer.content,
        "status": offer.status,
        "landing_page_url": offer.landing_page_url,
        "payment_link": offer.payment_link,
        "metrics": metrics,
        "created_at": offer.created_at,
        "deployed_at": offer.deployed_at
    }


# ==================== Deployment Endpoints ====================

@app.post("/api/offers/{offer_id}/deploy")
async def deploy_offer(offer_id: int, db: Session = Depends(get_db)):
    """Deploy an offer"""
    offer = db.query(MicroOffer).filter(MicroOffer.id == offer_id).first()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    pipeline = DeploymentPipeline()
    success = await pipeline.deploy_offer(offer)
    
    if success:
        return {
            "status": "deployed",
            "landing_page_url": offer.landing_page_url,
            "payment_link": offer.payment_link
        }
    else:
        raise HTTPException(status_code=500, detail="Deployment failed")


# ==================== Distribution Endpoints ====================

@app.post("/api/offers/{offer_id}/distribute")
async def distribute_offer(
    offer_id: int,
    platforms: List[str],
    db: Session = Depends(get_db)
):
    """Schedule content distribution for an offer"""
    offer = db.query(MicroOffer).filter(MicroOffer.id == offer_id).first()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    scheduler = DistributionScheduler()
    posts = await scheduler.schedule_distribution(offer, platforms)
    
    return {
        "scheduled_posts": len(posts),
        "platforms": platforms
    }


@app.post("/api/distribution/post-scheduled")
async def post_scheduled():
    """Post all scheduled content that's due"""
    scheduler = DistributionScheduler()
    await scheduler.post_scheduled_content()
    
    return {"status": "Scheduled content posted"}


@app.get("/api/distribution/posts")
async def get_posts(
    offer_id: Optional[int] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get distribution posts"""
    query = db.query(DistributionPost)
    
    if offer_id:
        query = query.filter(DistributionPost.offer_id == offer_id)
    
    if platform:
        query = query.filter(DistributionPost.platform == platform)
    
    posts = query.order_by(DistributionPost.scheduled_at.desc()).limit(50).all()
    
    return {
        "posts": [
            {
                "id": p.id,
                "offer_id": p.offer_id,
                "platform": p.platform,
                "content": p.content[:200],
                "status": p.status,
                "scheduled_at": p.scheduled_at,
                "posted_at": p.posted_at,
                "post_url": p.post_url
            }
            for p in posts
        ]
    }


# ==================== Analytics Endpoints ====================

@app.get("/api/analytics/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get main dashboard metrics"""
    from sqlalchemy import func
    
    # Total revenue
    total_revenue = db.query(func.sum(Revenue.net_amount)).filter(
        Revenue.status == 'completed'
    ).scalar() or 0
    
    # Active offers
    active_offers = db.query(func.count(MicroOffer.id)).filter(
        MicroOffer.status == 'active'
    ).scalar() or 0
    
    # Total conversions
    total_conversions = db.query(func.sum(Analytics.conversions)).scalar() or 0
    
    # Email subscribers
    subscribers = db.query(func.count(EmailSubscriber.id)).filter(
        EmailSubscriber.status == 'active'
    ).scalar() or 0
    
    # Revenue prediction
    predictor = RevenuePredictor()
    prediction = predictor.predict_time_to_goal()
    recommendations = predictor.get_growth_recommendations()
    
    return {
        "total_revenue": total_revenue,
        "active_offers": active_offers,
        "total_conversions": total_conversions,
        "email_subscribers": subscribers,
        "prediction": prediction,
        "recommendations": recommendations
    }


@app.get("/api/analytics/offers/{offer_id}")
async def get_offer_analytics(offer_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific offer"""
    offer = db.query(MicroOffer).filter(MicroOffer.id == offer_id).first()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    tracker = AnalyticsTracker()
    metrics = tracker.get_offer_metrics(offer_id)
    
    return metrics


# ==================== Scaling Endpoints ====================

@app.get("/api/scaling/winners")
async def get_winners():
    """Get winning offers (>5% conversion)"""
    engine = ScalingEngine()
    winners = engine.identify_winners()
    
    return {
        "winners": [
            {
                "id": w.id,
                "title": w.title,
                "price": w.price,
                "status": w.status
            }
            for w in winners
        ]
    }


@app.post("/api/scaling/reinvest")
async def execute_reinvestment():
    """Execute reinvestment strategy"""
    engine = ScalingEngine()
    
    total_revenue = engine.get_total_revenue()
    
    if total_revenue < settings.auto_reinvest_threshold:
        raise HTTPException(
            status_code=400,
            detail=f"Revenue threshold not met. Current: ${total_revenue:.2f}, Required: ${settings.auto_reinvest_threshold}"
        )
    
    allocation = await engine.execute_reinvestment()
    
    return {
        "status": "executed",
        "allocation": allocation
    }


@app.post("/api/scaling/create-suite")
async def create_suite():
    """Create product suite from winners"""
    engine = ScalingEngine()
    winners = engine.identify_winners()
    
    if len(winners) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 winning offers to create a suite"
        )
    
    suite = engine.create_product_suite(winners)
    
    return suite


# ==================== Email Automation Endpoints ====================

@app.post("/api/email/subscribe")
async def subscribe_email(
    email: str,
    source_offer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Subscribe an email"""
    
    # Check if already exists
    existing = db.query(EmailSubscriber).filter(
        EmailSubscriber.email == email
    ).first()
    
    if existing:
        return {"status": "already_subscribed"}
    
    subscriber = EmailSubscriber(
        email=email,
        source_offer_id=source_offer_id
    )
    
    db.add(subscriber)
    db.commit()
    
    return {"status": "subscribed"}


@app.get("/api/email/segments")
async def get_segments():
    """Get email subscriber segments"""
    automation = EmailAutomation()
    segments = automation.segment_subscribers()
    
    return {
        "segments": {
            name: len(subs)
            for name, subs in segments.items()
        }
    }


# ==================== Webhook Endpoints ====================

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: dict):
    """Handle Stripe webhooks"""
    
    # Verify webhook signature (in production)
    # event = stripe.Webhook.construct_event(...)
    
    event_type = request.get('type')
    
    if event_type == 'checkout.session.completed':
        # Handle successful payment
        session = request.get('data', {}).get('object', {})
        
        offer_id = session.get('metadata', {}).get('offer_id')
        amount = session.get('amount_total', 0) / 100  # Convert from cents
        
        tracker = AnalyticsTracker()
        tracker.track_conversion(
            offer_id=int(offer_id),
            amount=amount,
            transaction_id=session.get('id')
        )
    
    return {"status": "received"}


# ==================== Health Check ====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Stealth AI Revenue System",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
