"""
Deployment Pipeline
Automates landing page generation and payment integration
"""
from typing import Dict, Optional
from datetime import datetime
import stripe
from ..database.models import MicroOffer, SessionLocal
from config.settings import settings


class DeploymentPipeline:
    """Handles offer deployment"""
    
    def __init__(self):
        self.db = SessionLocal()
        if settings.stripe_api_key:
            stripe.api_key = settings.stripe_api_key
    
    async def deploy_offer(self, offer: MicroOffer) -> bool:
        """Deploy a micro-offer"""
        
        try:
            # Generate landing page
            landing_page_url = await self.generate_landing_page(offer)
            
            # Set up payment processing
            payment_link = await self.create_payment_link(offer)
            
            # Update offer
            offer.landing_page_url = landing_page_url
            offer.payment_link = payment_link
            offer.status = 'active'
            offer.deployed_at = datetime.utcnow()
            
            self.db.commit()
            
            return True
        
        except Exception as e:
            print(f"Error deploying offer {offer.id}: {e}")
            return False
    
    async def generate_landing_page(self, offer: MicroOffer) -> str:
        """Generate a landing page for the offer"""
        
        # Generate HTML content
        html_content = self._create_landing_page_html(offer)
        
        # Save to file system
        filename = f"offer_{offer.id}.html"
        filepath = f"./frontend/public/pages/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        # Return URL
        return f"{settings.landing_page_domain}/pages/{filename}"
    
    def _create_landing_page_html(self, offer: MicroOffer) -> str:
        """Create landing page HTML"""
        
        content_data = offer.content or {}
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{offer.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #2d3748;
        }}
        .price {{
            font-size: 3em;
            color: #667eea;
            font-weight: bold;
            margin: 20px 0;
        }}
        .description {{
            font-size: 1.2em;
            margin-bottom: 30px;
            color: #4a5568;
        }}
        .features {{
            list-style: none;
            margin: 30px 0;
        }}
        .features li {{
            padding: 15px;
            margin: 10px 0;
            background: #f7fafc;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .features li:before {{
            content: "✓ ";
            color: #48bb78;
            font-weight: bold;
            margin-right: 10px;
        }}
        .cta-button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 20px 40px;
            font-size: 1.3em;
            border-radius: 50px;
            text-decoration: none;
            transition: transform 0.2s;
            margin: 20px 0;
        }}
        .cta-button:hover {{
            transform: scale(1.05);
            background: #5a67d8;
        }}
        .guarantee {{
            background: #fef5e7;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            border: 2px solid #f39c12;
        }}
        .deliverables {{
            background: #e6fffa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{offer.title}</h1>
        
        <div class="description">
            {offer.description}
        </div>
        
        <div class="price">
            ${offer.price}
        </div>
        
        <a href="{offer.payment_link or '#'}" class="cta-button">
            Get Instant Access Now
        </a>
        
        <div class="deliverables">
            <h2>What You'll Get:</h2>
            <ul class="features">
                {"".join(f"<li>{item}</li>" for item in content_data.get('key_deliverables', []))}
            </ul>
        </div>
        
        <div class="features">
            <h2>Features:</h2>
            {"".join(f"<li>{feature}</li>" for feature in content_data.get('features', []))}
        </div>
        
        <div class="guarantee">
            <h3>💯 30-Day Money-Back Guarantee</h3>
            <p>Try it risk-free. If you're not satisfied, get a full refund within 30 days.</p>
        </div>
        
        <a href="{offer.payment_link or '#'}" class="cta-button">
            Get Started Now - ${offer.price}
        </a>
        
        <div style="text-align: center; margin-top: 40px; color: #718096;">
            <p>Secure payment powered by Stripe</p>
        </div>
    </div>
    
    <script>
        // Track analytics
        if (window.gtag) {{
            gtag('event', 'page_view', {{
                'offer_id': {offer.id},
                'offer_title': '{offer.title}'
            }});
        }}
    </script>
</body>
</html>
"""
        return html
    
    async def create_payment_link(self, offer: MicroOffer) -> str:
        """Create Stripe payment link"""
        
        if not settings.stripe_api_key:
            # Fallback to Gumroad or manual link
            return f"https://gumroad.com/l/offer_{offer.id}"
        
        try:
            # Create Stripe product
            product = stripe.Product.create(
                name=offer.title,
                description=offer.description[:500],
                metadata={'offer_id': offer.id}
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(offer.price * 100),  # Convert to cents
                currency='usd'
            )
            
            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{'price': price.id, 'quantity': 1}],
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        'url': f'{settings.landing_page_domain}/thank-you?offer={offer.id}'
                    }
                },
                metadata={'offer_id': offer.id}
            )
            
            return payment_link.url
        
        except Exception as e:
            print(f"Error creating payment link: {e}")
            return f"https://gumroad.com/l/offer_{offer.id}"
    
    async def create_ab_test(self, offer_id: int, variations: list) -> Dict:
        """Create A/B test for offer optimization"""
        
        # Simple A/B testing framework
        test_config = {
            'offer_id': offer_id,
            'variations': variations,
            'traffic_split': [50, 50],  # 50/50 split
            'metrics_to_track': ['ctr', 'conversion_rate', 'revenue'],
            'status': 'active'
        }
        
        return test_config


class AnalyticsTracker:
    """Track offer performance"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def track_impression(self, offer_id: int):
        """Track page view"""
        from ..database.models import Analytics
        
        today = datetime.utcnow().date()
        
        analytics = self.db.query(Analytics).filter(
            Analytics.offer_id == offer_id,
            Analytics.date >= today
        ).first()
        
        if analytics:
            analytics.impressions += 1
        else:
            analytics = Analytics(
                offer_id=offer_id,
                impressions=1
            )
            self.db.add(analytics)
        
        self.db.commit()
    
    def track_click(self, offer_id: int):
        """Track CTA click"""
        from ..database.models import Analytics
        
        today = datetime.utcnow().date()
        
        analytics = self.db.query(Analytics).filter(
            Analytics.offer_id == offer_id,
            Analytics.date >= today
        ).first()
        
        if analytics:
            analytics.clicks += 1
            analytics.click_through_rate = (analytics.clicks / analytics.impressions) if analytics.impressions > 0 else 0
        
        self.db.commit()
    
    def track_conversion(self, offer_id: int, amount: float, transaction_id: str):
        """Track successful purchase"""
        from ..database.models import Analytics, Revenue
        
        today = datetime.utcnow().date()
        
        # Update analytics
        analytics = self.db.query(Analytics).filter(
            Analytics.offer_id == offer_id,
            Analytics.date >= today
        ).first()
        
        if analytics:
            analytics.conversions += 1
            analytics.revenue += amount
            
            # Calculate conversion rate
            if analytics.clicks > 0:
                analytics.conversion_rate = analytics.conversions / analytics.clicks
            
            # Calculate net profit (assume 5% platform fees)
            platform_fee = amount * 0.05
            analytics.platform_fees += platform_fee
            analytics.net_profit = analytics.revenue - analytics.platform_fees
        
        # Record revenue transaction
        revenue = Revenue(
            offer_id=offer_id,
            amount=amount,
            payment_method='stripe',
            transaction_id=transaction_id,
            platform_fee=amount * 0.05,
            net_amount=amount * 0.95,
            status='completed'
        )
        self.db.add(revenue)
        
        self.db.commit()
    
    def get_offer_metrics(self, offer_id: int) -> Dict:
        """Get comprehensive metrics for an offer"""
        from ..database.models import Analytics
        from sqlalchemy import func
        
        metrics = self.db.query(
            func.sum(Analytics.impressions).label('total_impressions'),
            func.sum(Analytics.clicks).label('total_clicks'),
            func.sum(Analytics.conversions).label('total_conversions'),
            func.sum(Analytics.revenue).label('total_revenue'),
            func.sum(Analytics.net_profit).label('total_profit')
        ).filter(Analytics.offer_id == offer_id).first()
        
        return {
            'impressions': metrics.total_impressions or 0,
            'clicks': metrics.total_clicks or 0,
            'conversions': metrics.total_conversions or 0,
            'revenue': metrics.total_revenue or 0,
            'profit': metrics.total_profit or 0,
            'ctr': (metrics.total_clicks / metrics.total_impressions * 100) if metrics.total_impressions else 0,
            'conversion_rate': (metrics.total_conversions / metrics.total_clicks * 100) if metrics.total_clicks else 0
        }
