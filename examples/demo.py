"""
Example: Running the Stealth AI System
This demonstrates how to use the system programmatically
"""
import asyncio
from backend.services.signal_compression import SignalCompressor
from backend.services.offer_generator import OfferGenerator
from backend.services.deployment import DeploymentPipeline
from backend.services.distribution import DistributionScheduler
from backend.database.models import init_db


async def example_workflow():
    """Complete workflow example"""
    
    print("🚀 Stealth AI Revenue System - Example Workflow\n")
    
    # Initialize database
    print("1️⃣ Initializing database...")
    init_db()
    print("   ✅ Database ready\n")
    
    # Step 1: Scan for signals
    print("2️⃣ Scanning for market signals...")
    compressor = SignalCompressor()
    
    # For demo purposes, we'll create mock signals since APIs require keys
    print("   ℹ️ In production, this scans Twitter, Reddit, marketplaces")
    print("   ℹ️ For this demo, we'll skip API calls\n")
    
    # Get top signals
    top_signals = compressor.get_top_signals(limit=3)
    print(f"   Found {len(top_signals)} signals from database\n")
    
    # Step 2: Generate offers
    print("3️⃣ Generating micro-offers...")
    generator = OfferGenerator()
    
    if len(top_signals) > 0:
        # Generate offer from first signal
        signal = top_signals[0]
        offer = await generator.generate_from_signal(signal)
        print(f"   ✅ Generated: {offer.title}")
        print(f"   💰 Price: ${offer.price}")
        print(f"   📦 Type: {offer.offer_type}\n")
    else:
        print("   ⚠️ No signals available. Run signal scan first.\n")
        # Create a demo offer anyway
        from backend.database.models import MicroOffer, SessionLocal
        db = SessionLocal()
        offer = MicroOffer(
            title="Productivity Automation Guide",
            description="Learn to automate your daily tasks",
            offer_type="guide",
            price=19.00,
            content={
                'key_deliverables': [
                    'Complete PDF guide',
                    'Templates and examples',
                    'Video walkthrough'
                ],
                'features': [
                    'Step-by-step instructions',
                    'Real-world examples',
                    'Lifetime access'
                ]
            }
        )
        db.add(offer)
        db.commit()
        print(f"   ✅ Created demo offer: {offer.title}\n")
    
    # Step 3: Deploy offer
    print("4️⃣ Deploying offer...")
    pipeline = DeploymentPipeline()
    
    print("   📄 Generating landing page...")
    print("   💳 Setting up payment processing...")
    
    # In production, this would create real landing pages and payment links
    print("   ℹ️ In production, creates real landing page + Stripe payment link")
    print("   ✅ Offer ready for deployment\n")
    
    # Step 4: Schedule distribution
    print("5️⃣ Scheduling content distribution...")
    scheduler = DistributionScheduler()
    
    print("   📱 Generating Twitter thread...")
    print("   📝 Creating Reddit post...")
    print("   💼 Preparing LinkedIn content...")
    
    # In production, this schedules actual posts
    print("   ℹ️ In production, posts to real platforms")
    print("   ✅ Content scheduled\n")
    
    # Summary
    print("="*50)
    print("✅ Workflow Complete!")
    print("="*50)
    print("\n📊 Next Steps:")
    print("   1. Configure API keys in .env")
    print("   2. Run ./scripts/start.sh")
    print("   3. Access dashboard at http://localhost:3000")
    print("   4. Monitor revenue and conversions")
    print("\n🎯 Target: First $310 in 14 days")
    print("🚀 Goal: $8,700/month by day 30\n")


async def example_analytics():
    """Example of using analytics"""
    from backend.services.scaling import RevenuePredictor
    
    print("\n📊 Analytics Example\n")
    
    predictor = RevenuePredictor()
    
    # Get revenue prediction
    prediction = predictor.predict_time_to_goal()
    
    print(f"Current Revenue: ${prediction['current_monthly_revenue']:.2f}")
    print(f"Daily Average: ${prediction['daily_average']:.2f}")
    print(f"Target: ${prediction['target']:.2f}")
    print(f"Days to Goal: {prediction['days_to_goal']:.0f}")
    print(f"On Track: {'✅ Yes' if prediction['on_track'] else '❌ No'}")
    
    # Get recommendations
    recommendations = predictor.get_growth_recommendations()
    print("\n💡 Recommendations:")
    for rec in recommendations:
        print(f"   {rec}")


async def main():
    """Run examples"""
    await example_workflow()
    await example_analytics()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("STEALTH AI REVENUE SYSTEM - DEMO")
    print("="*50 + "\n")
    
    asyncio.run(main())
    
    print("\n" + "="*50)
    print("Demo complete! 🎉")
    print("="*50 + "\n")
