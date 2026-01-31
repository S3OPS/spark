"""
Micro-Offer Generation System
Creates digital products based on compressed signals
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
import openai
from ..database.models import MicroOffer, Signal, SessionLocal
from config.settings import settings


class OfferGenerator:
    """Generate micro-offers from signals"""
    
    def __init__(self):
        self.db = SessionLocal()
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        self.offer_templates = {
            'guide': self._generate_guide,
            'template': self._generate_template,
            'tool': self._generate_tool,
            'course': self._generate_mini_course,
            'resource_list': self._generate_resource_list
        }
    
    async def generate_from_signal(self, signal: Signal) -> Optional[MicroOffer]:
        """Generate a micro-offer based on a signal"""
        
        # Determine best offer type for this signal
        offer_type = self._determine_offer_type(signal)
        
        # Generate offer content
        offer_data = await self.offer_templates[offer_type](signal)
        
        if not offer_data:
            return None
        
        # Calculate optimal price point
        price = self._calculate_price(offer_type, offer_data)
        
        # Create offer object
        offer = MicroOffer(
            signal_id=signal.id,
            title=offer_data['title'],
            description=offer_data['description'],
            offer_type=offer_type,
            price=price,
            cost_to_create=0.0,  # All digital, zero marginal cost
            content=offer_data,
            status='draft'
        )
        
        # Save to database
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        
        # Mark signal as processed
        signal.status = 'processed'
        signal.processed_at = datetime.utcnow()
        self.db.commit()
        
        return offer
    
    def _determine_offer_type(self, signal: Signal) -> str:
        """Determine the best offer type for a signal"""
        content = signal.content.lower()
        
        # Simple keyword matching
        if any(word in content for word in ['template', 'spreadsheet', 'notion']):
            return 'template'
        elif any(word in content for word in ['course', 'learn', 'tutorial']):
            return 'course'
        elif any(word in content for word in ['tool', 'script', 'automate']):
            return 'tool'
        elif any(word in content for word in ['resources', 'list', 'collection']):
            return 'resource_list'
        else:
            return 'guide'
    
    async def _generate_guide(self, signal: Signal) -> Dict:
        """Generate a comprehensive guide"""
        
        prompt = f"""
        Based on this user pain point: "{signal.content}"
        
        Create a detailed guide outline that solves this problem. The guide should be:
        - Actionable and practical
        - 10-20 pages long
        - Include step-by-step instructions
        - Have templates and examples
        
        Return a JSON object with:
        - title: Catchy title for the guide
        - description: 2-3 sentence description
        - outline: Array of chapter titles
        - key_deliverables: What the user gets
        - unique_angle: What makes this guide different
        """
        
        if settings.openai_api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert digital product creator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                # Try to parse JSON from the response
                return json.loads(content)
            except Exception as e:
                print(f"Error generating guide with AI: {e}")
        
        # Fallback: Generate basic guide structure
        return {
            'title': f"Complete Guide to {signal.content[:50]}",
            'description': f"Step-by-step guide to solve: {signal.content[:100]}",
            'outline': [
                "Introduction",
                "Understanding the Problem",
                "Step-by-Step Solution",
                "Advanced Techniques",
                "Templates and Resources"
            ],
            'key_deliverables': [
                "Complete PDF guide",
                "Downloadable templates",
                "Action checklist"
            ],
            'unique_angle': "Practical, no-fluff approach with real examples"
        }
    
    async def _generate_template(self, signal: Signal) -> Dict:
        """Generate a template/spreadsheet product"""
        
        return {
            'title': f"Ready-to-Use Template for {signal.content[:50]}",
            'description': f"Plug-and-play template that helps you {signal.content[:100]}",
            'template_type': 'Notion/Spreadsheet/Document',
            'features': [
                "Pre-built formulas and automation",
                "Customizable to your needs",
                "Video walkthrough included",
                "Lifetime updates"
            ],
            'key_deliverables': [
                "Editable template file",
                "Setup instructions",
                "Video tutorial"
            ],
            'unique_angle': "Save 10+ hours with this pre-built system"
        }
    
    async def _generate_tool(self, signal: Signal) -> Dict:
        """Generate an automation tool/script"""
        
        return {
            'title': f"Automation Tool: {signal.content[:50]}",
            'description': f"Automate your workflow with this simple tool for {signal.content[:100]}",
            'tool_type': 'Python Script/Chrome Extension/Web Tool',
            'features': [
                "One-click automation",
                "No coding required",
                "Works on Windows/Mac/Linux",
                "Regular updates"
            ],
            'key_deliverables': [
                "Download link",
                "Installation guide",
                "Usage documentation",
                "Email support"
            ],
            'unique_angle': "Automate what used to take hours in minutes"
        }
    
    async def _generate_mini_course(self, signal: Signal) -> Dict:
        """Generate a mini-course or challenge"""
        
        return {
            'title': f"7-Day Challenge: {signal.content[:50]}",
            'description': f"Master {signal.content[:100]} in just 7 days with daily actionable lessons",
            'format': '7 daily emails + resources',
            'features': [
                "Daily actionable lessons",
                "Worksheets and templates",
                "Private community access",
                "Email support"
            ],
            'key_deliverables': [
                "7-day email course",
                "Downloadable workbook",
                "Resource library",
                "Certificate of completion"
            ],
            'unique_angle': "Results in 7 days with just 15 minutes per day"
        }
    
    async def _generate_resource_list(self, signal: Signal) -> Dict:
        """Generate a curated resource list"""
        
        return {
            'title': f"Ultimate Resource List: {signal.content[:50]}",
            'description': f"Hand-picked collection of the best resources for {signal.content[:100]}",
            'list_type': 'Curated directory',
            'features': [
                "50+ vetted resources",
                "Organized by category",
                "Regular updates",
                "Bonus: exclusive discounts"
            ],
            'key_deliverables': [
                "Comprehensive resource database",
                "Quick-start guide",
                "Exclusive bonuses",
                "Lifetime access"
            ],
            'unique_angle': "Save 20+ hours of research with this curated collection"
        }
    
    def _calculate_price(self, offer_type: str, offer_data: Dict) -> float:
        """Calculate optimal price point ($10-$50 range)"""
        
        base_prices = {
            'guide': 19,
            'template': 15,
            'tool': 29,
            'course': 39,
            'resource_list': 12
        }
        
        base_price = base_prices.get(offer_type, 19)
        
        # Adjust based on deliverables count
        deliverables_count = len(offer_data.get('key_deliverables', []))
        if deliverables_count > 5:
            base_price += 5
        
        # Keep in $10-$50 range
        return min(max(base_price, 10), 50)
    
    def get_ready_offers(self) -> List[MicroOffer]:
        """Get offers ready for deployment"""
        return (
            self.db.query(MicroOffer)
            .filter(MicroOffer.status == 'draft')
            .all()
        )
    
    async def generate_batch(self, limit: int = 5) -> List[MicroOffer]:
        """Generate multiple offers from top signals"""
        from .signal_compression import SignalCompressor
        
        compressor = SignalCompressor()
        top_signals = compressor.get_top_signals(limit)
        
        offers = []
        for signal in top_signals:
            try:
                offer = await self.generate_from_signal(signal)
                if offer:
                    offers.append(offer)
            except Exception as e:
                print(f"Error generating offer for signal {signal.id}: {e}")
        
        return offers


if __name__ == "__main__":
    import asyncio
    
    async def test():
        generator = OfferGenerator()
        offers = await generator.generate_batch(3)
        print(f"Generated {len(offers)} offers")
    
    asyncio.run(test())
