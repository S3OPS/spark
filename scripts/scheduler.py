"""
Automation Scheduler
Runs periodic tasks for the Stealth AI system
"""
import asyncio
import schedule
import time
from datetime import datetime
from backend.services.signal_compression import SignalCompressor, run_signal_scan
from backend.services.offer_generator import OfferGenerator
from backend.services.distribution import DistributionScheduler
from backend.services.scaling import ScalingEngine, RevenuePredictor
from config.settings import settings


async def job_scan_signals():
    """Scan signals from all platforms"""
    print(f"[{datetime.now()}] Starting signal scan...")
    try:
        await run_signal_scan()
        print(f"[{datetime.now()}] ✅ Signal scan completed")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Signal scan failed: {e}")


async def job_generate_offers():
    """Generate offers from top signals"""
    print(f"[{datetime.now()}] Generating offers...")
    try:
        generator = OfferGenerator()
        offers = await generator.generate_batch(limit=3)
        print(f"[{datetime.now()}] ✅ Generated {len(offers)} offers")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Offer generation failed: {e}")


async def job_post_content():
    """Post scheduled content"""
    print(f"[{datetime.now()}] Posting scheduled content...")
    try:
        scheduler = DistributionScheduler()
        await scheduler.post_scheduled_content()
        print(f"[{datetime.now()}] ✅ Content posted")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Content posting failed: {e}")


async def job_check_reinvestment():
    """Check if reinvestment threshold is met"""
    print(f"[{datetime.now()}] Checking reinvestment threshold...")
    try:
        engine = ScalingEngine()
        await engine.check_reinvestment_threshold()
        print(f"[{datetime.now()}] ✅ Reinvestment check completed")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Reinvestment check failed: {e}")


async def job_daily_report():
    """Generate daily performance report"""
    print(f"[{datetime.now()}] Generating daily report...")
    try:
        predictor = RevenuePredictor()
        prediction = predictor.predict_time_to_goal()
        recommendations = predictor.get_growth_recommendations()
        
        print("\n" + "="*50)
        print("📊 DAILY REPORT")
        print("="*50)
        print(f"Total Revenue: ${prediction['current_monthly_revenue']:.2f}")
        print(f"Daily Average: ${prediction['daily_average']:.2f}")
        print(f"Days to Goal: {prediction['days_to_goal']:.0f}")
        print(f"On Track: {'✅' if prediction['on_track'] else '❌'}")
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  {rec}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Daily report failed: {e}")


def run_async_job(job_func):
    """Wrapper to run async jobs"""
    asyncio.run(job_func())


def setup_schedule():
    """Set up the automation schedule"""
    
    # Signal scanning - every N hours
    interval_hours = settings.signal_scan_interval_hours
    schedule.every(interval_hours).hours.do(lambda: run_async_job(job_scan_signals))
    
    # Generate offers - twice daily
    schedule.every().day.at("09:00").do(lambda: run_async_job(job_generate_offers))
    schedule.every().day.at("15:00").do(lambda: run_async_job(job_generate_offers))
    
    # Post content - every 2 hours during active hours
    schedule.every(2).hours.do(lambda: run_async_job(job_post_content))
    
    # Check reinvestment - hourly
    schedule.every().hour.do(lambda: run_async_job(job_check_reinvestment))
    
    # Daily report - every morning
    schedule.every().day.at("08:00").do(lambda: run_async_job(job_daily_report))
    
    print("✅ Automation scheduler configured")
    print(f"   - Signal scan: Every {interval_hours} hours")
    print(f"   - Offer generation: 9 AM and 3 PM daily")
    print(f"   - Content posting: Every 2 hours")
    print(f"   - Reinvestment check: Hourly")
    print(f"   - Daily report: 8 AM daily")


def run_scheduler():
    """Run the scheduler (blocking)"""
    setup_schedule()
    
    print("\n🚀 Scheduler started. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n⏹️  Scheduler stopped")


if __name__ == "__main__":
    run_scheduler()
