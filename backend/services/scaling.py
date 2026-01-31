"""
Scaling and Revenue Optimization System
Handles auto-reinvestment and upsell funnels
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from ..database.models import (
    MicroOffer, Revenue, Analytics, EmailSubscriber,
    AutomationConfig, SessionLocal
)
from config.settings import settings


class ScalingEngine:
    """Automates scaling decisions based on performance"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def identify_winners(self) -> List[MicroOffer]:
        """Identify offers converting above threshold (>5%)"""
        
        # Get offers with sufficient data (at least 100 clicks)
        offers_with_analytics = (
            self.db.query(
                MicroOffer.id,
                func.sum(Analytics.clicks).label('total_clicks'),
                func.sum(Analytics.conversions).label('total_conversions')
            )
            .join(Analytics, MicroOffer.id == Analytics.offer_id)
            .filter(MicroOffer.status == 'active')
            .group_by(MicroOffer.id)
            .having(func.sum(Analytics.clicks) >= 100)
            .all()
        )
        
        winners = []
        for offer_id, clicks, conversions in offers_with_analytics:
            conversion_rate = conversions / clicks if clicks > 0 else 0
            
            if conversion_rate >= settings.min_conversion_threshold:
                offer = self.db.query(MicroOffer).get(offer_id)
                winners.append(offer)
        
        return winners
    
    def get_total_revenue(self) -> float:
        """Get total revenue across all offers"""
        
        total = self.db.query(func.sum(Revenue.net_amount)).filter(
            Revenue.status == 'completed'
        ).scalar()
        
        return total or 0.0
    
    async def check_reinvestment_threshold(self):
        """Check if we've hit the $310 reinvestment threshold"""
        
        total_revenue = self.get_total_revenue()
        
        # Check if we have a reinvestment config
        config = self.db.query(AutomationConfig).filter(
            AutomationConfig.name == 'first_reinvestment',
            AutomationConfig.is_active == True
        ).first()
        
        if total_revenue >= settings.auto_reinvest_threshold and not config:
            # Trigger reinvestment
            await self.execute_reinvestment()
    
    async def execute_reinvestment(self):
        """Execute the $310 reinvestment strategy"""
        
        allocation = {
            'paid_traffic': 100,
            'content_amplification': 100,
            'tool_subscriptions': 110
        }
        
        # Create reinvestment config
        config = AutomationConfig(
            name='first_reinvestment',
            config_type='reinvestment',
            settings={
                'allocation': allocation,
                'executed_at': datetime.utcnow().isoformat(),
                'total_amount': 310
            },
            is_active=True
        )
        
        self.db.add(config)
        self.db.commit()
        
        print(f"💰 Reinvestment executed: {allocation}")
        
        # TODO: Integrate with ad platforms for automatic campaign setup
        return allocation
    
    def create_product_suite(self, winner_offers: List[MicroOffer]) -> Dict:
        """Stack successful offers into a product suite"""
        
        if len(winner_offers) < 2:
            return {}
        
        # Create bundles at different price points
        suite = {
            'entry_offer': min(winner_offers, key=lambda x: x.price),
            'mid_tier_bundle': {
                'offers': winner_offers[:3],
                'price': sum(offer.price for offer in winner_offers[:3]) * 0.7,  # 30% discount
                'title': 'Complete Starter Bundle'
            },
            'premium_bundle': {
                'offers': winner_offers,
                'price': sum(offer.price for offer in winner_offers) * 0.5,  # 50% discount
                'title': 'Premium All-Access Bundle',
                'bonuses': ['Priority support', 'Lifetime updates', 'Exclusive community']
            }
        }
        
        return suite
    
    async def optimize_pricing(self, offer: MicroOffer):
        """Use data to optimize pricing"""
        
        # Get conversion data at current price
        metrics = self.db.query(
            func.sum(Analytics.conversions).label('conversions'),
            func.sum(Analytics.clicks).label('clicks'),
            func.sum(Analytics.revenue).label('revenue')
        ).filter(Analytics.offer_id == offer.id).first()
        
        if not metrics or metrics.clicks < 100:
            return  # Not enough data
        
        conversion_rate = metrics.conversions / metrics.clicks
        
        # If conversion rate is very high (>15%), we can test higher price
        if conversion_rate > 0.15:
            suggested_price = min(offer.price * 1.2, 50)  # Max $50
            print(f"💡 Suggestion: Test higher price ${suggested_price:.2f} for offer {offer.id}")
        
        # If conversion rate is low (<3%), test lower price
        elif conversion_rate < 0.03:
            suggested_price = max(offer.price * 0.8, 10)  # Min $10
            print(f"💡 Suggestion: Test lower price ${suggested_price:.2f} for offer {offer.id}")


class UpsellFunnel:
    """Manage upsell sequences"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_funnel(self, entry_offer: MicroOffer, upsell_offers: List[MicroOffer]):
        """Create an upsell funnel"""
        
        funnel = {
            'entry': {
                'offer_id': entry_offer.id,
                'price': entry_offer.price,
                'next_step': 'order_bump'
            },
            'order_bump': {
                'offer_id': upsell_offers[0].id if upsell_offers else None,
                'price': upsell_offers[0].price if upsell_offers else 0,
                'discount': 0.2,  # 20% off
                'next_step': 'upsell_1'
            },
            'upsell_1': {
                'offer_id': upsell_offers[1].id if len(upsell_offers) > 1 else None,
                'price': upsell_offers[1].price if len(upsell_offers) > 1 else 0,
                'discount': 0.15,
                'next_step': 'upsell_2'
            },
            'upsell_2': {
                'offer_id': upsell_offers[2].id if len(upsell_offers) > 2 else None,
                'price': upsell_offers[2].price if len(upsell_offers) > 2 else 0,
                'discount': 0.3,  # Premium bundle at 30% off
                'next_step': 'thank_you'
            }
        }
        
        return funnel
    
    def calculate_average_order_value(self, funnel: Dict) -> float:
        """Calculate expected average order value"""
        
        # Simplified calculation
        entry_price = funnel['entry']['price']
        
        # Assume 30% take order bump, 20% take upsell 1, 10% take upsell 2
        bump_value = funnel['order_bump'].get('price', 0) * 0.8 * 0.3
        upsell1_value = funnel['upsell_1'].get('price', 0) * 0.85 * 0.2
        upsell2_value = funnel['upsell_2'].get('price', 0) * 0.7 * 0.1
        
        aov = entry_price + bump_value + upsell1_value + upsell2_value
        
        return aov


class EmailAutomation:
    """Email sequences for customer lifetime value"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_welcome_sequence(self, subscriber: EmailSubscriber) -> List[Dict]:
        """Create welcome email sequence"""
        
        sequence = [
            {
                'day': 0,
                'subject': '🎉 Welcome! Here\'s what you just got...',
                'template': 'welcome',
                'goal': 'onboarding'
            },
            {
                'day': 1,
                'subject': 'Quick question: Are you stuck anywhere?',
                'template': 'check_in',
                'goal': 'engagement'
            },
            {
                'day': 3,
                'subject': 'Pro tip: How to get the most value',
                'template': 'value_tips',
                'goal': 'activation'
            },
            {
                'day': 7,
                'subject': 'People are also getting this...',
                'template': 'cross_sell',
                'goal': 'upsell'
            },
            {
                'day': 14,
                'subject': 'Special offer: Complete your collection',
                'template': 'bundle_offer',
                'goal': 'upsell'
            },
            {
                'day': 30,
                'subject': 'Quick favor: Share your results?',
                'template': 'testimonial_request',
                'goal': 'social_proof'
            }
        ]
        
        return sequence
    
    def segment_subscribers(self) -> Dict[str, List[EmailSubscriber]]:
        """Segment subscribers for targeted campaigns"""
        
        # Get all active subscribers
        subscribers = self.db.query(EmailSubscriber).filter(
            EmailSubscriber.status == 'active'
        ).all()
        
        segments = {
            'high_value': [],  # Purchased multiple products
            'engaged': [],     # Opened recent emails
            'dormant': [],     # No activity in 30 days
            'new': []          # Subscribed in last 7 days
        }
        
        now = datetime.utcnow()
        
        for sub in subscribers:
            # High value customers
            if sub.total_purchases > 50:
                segments['high_value'].append(sub)
            
            # New subscribers
            elif (now - sub.subscribed_at).days <= 7:
                segments['new'].append(sub)
            
            # Dormant
            elif sub.last_email_sent and (now - sub.last_email_sent).days > 30:
                segments['dormant'].append(sub)
            
            # Engaged
            else:
                segments['engaged'].append(sub)
        
        return segments
    
    async def send_campaign(self, segment: str, template: str):
        """Send targeted campaign to a segment"""
        
        # This would integrate with SendGrid or similar
        print(f"📧 Sending {template} campaign to {segment} segment")
        
        # TODO: Implement actual email sending
        pass


class RevenuePredictor:
    """Predict path to monthly revenue goals"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def predict_time_to_goal(self, target: float = 8700) -> Dict:
        """Predict days to reach monthly revenue goal"""
        
        # Get revenue from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_revenue = self.db.query(func.sum(Revenue.net_amount)).filter(
            Revenue.created_at >= thirty_days_ago,
            Revenue.status == 'completed'
        ).scalar() or 0
        
        # Calculate daily average
        daily_avg = recent_revenue / 30
        
        # Current total
        total_revenue = self.db.query(func.sum(Revenue.net_amount)).filter(
            Revenue.status == 'completed'
        ).scalar() or 0
        
        # Calculate days to goal
        remaining = target - (total_revenue % target)  # Remaining this month
        
        if daily_avg > 0:
            days_to_goal = remaining / daily_avg
        else:
            days_to_goal = float('inf')
        
        return {
            'current_monthly_revenue': total_revenue,
            'target': target,
            'daily_average': daily_avg,
            'days_to_goal': days_to_goal,
            'projected_monthly': daily_avg * 30,
            'on_track': (daily_avg * 30) >= target
        }
    
    def get_growth_recommendations(self) -> List[str]:
        """Get AI-powered growth recommendations"""
        
        recommendations = []
        
        # Analyze winning offers
        engine = ScalingEngine()
        winners = engine.identify_winners()
        
        if len(winners) > 0:
            recommendations.append(f"✅ {len(winners)} offers converting above 5% - scale these with paid ads")
        else:
            recommendations.append("⚠️ No offers above 5% conversion - optimize landing pages and pricing")
        
        # Check total revenue
        total_revenue = engine.get_total_revenue()
        
        if total_revenue >= 310:
            recommendations.append("💰 Revenue threshold hit - execute reinvestment strategy")
        
        # Check email list size
        subscriber_count = self.db.query(func.count(EmailSubscriber.id)).scalar()
        
        if subscriber_count < 100:
            recommendations.append("📧 Build email list - add lead magnets to high-traffic offers")
        
        # Check content distribution
        from ..database.models import DistributionPost
        
        posted_count = self.db.query(func.count(DistributionPost.id)).filter(
            DistributionPost.status == 'posted',
            DistributionPost.posted_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar()
        
        if posted_count < 10:
            recommendations.append("📱 Increase content distribution - aim for 2-3 posts daily")
        
        return recommendations


if __name__ == "__main__":
    # Test scaling engine
    engine = ScalingEngine()
    winners = engine.identify_winners()
    print(f"Found {len(winners)} winning offers")
    
    predictor = RevenuePredictor()
    prediction = predictor.predict_time_to_goal()
    print(f"Revenue prediction: {prediction}")
    
    recommendations = predictor.get_growth_recommendations()
    print("Recommendations:")
    for rec in recommendations:
        print(f"  {rec}")
