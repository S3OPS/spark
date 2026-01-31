"""
Signal Compression Engine
Analyzes data from multiple sources and extracts high-conversion patterns
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import json
from ..database.models import Signal, SessionLocal
from config.settings import settings


class SignalCompressor:
    """Main signal compression engine"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.collectors = [
            TwitterSignalCollector(),
            RedditSignalCollector(),
            MarketplaceSignalCollector()
        ]
    
    async def scan_all_sources(self) -> List[Signal]:
        """Scan all configured data sources"""
        signals = []
        
        for collector in self.collectors:
            try:
                source_signals = await collector.collect()
                signals.extend(source_signals)
            except Exception as e:
                print(f"Error collecting from {collector.__class__.__name__}: {e}")
        
        # Compress and score signals
        compressed_signals = self.compress_signals(signals)
        
        # Store in database
        for signal in compressed_signals:
            self.save_signal(signal)
        
        return compressed_signals
    
    def compress_signals(self, raw_signals: List[Dict]) -> List[Signal]:
        """Compress raw signals and calculate scores"""
        compressed = []
        
        for raw in raw_signals:
            signal = Signal(
                source=raw.get('source'),
                signal_type=raw.get('signal_type'),
                content=raw.get('content'),
                compressed_data=raw.get('data'),
                confidence_score=self.calculate_confidence(raw),
                conversion_potential=self.calculate_conversion_potential(raw),
                speed_to_market=self.calculate_speed_to_market(raw),
            )
            
            # Overall score is weighted average
            signal.overall_score = (
                signal.confidence_score * 0.3 +
                signal.conversion_potential * 0.5 +
                signal.speed_to_market * 0.2
            )
            
            compressed.append(signal)
        
        return sorted(compressed, key=lambda x: x.overall_score, reverse=True)
    
    def calculate_confidence(self, signal: Dict) -> float:
        """Calculate confidence score based on data quality and consistency"""
        score = 0.5  # Base score
        
        # Increase score if we have engagement metrics
        if signal.get('engagement_count', 0) > 100:
            score += 0.2
        if signal.get('engagement_count', 0) > 1000:
            score += 0.2
        
        # Increase score if multiple sources confirm
        if signal.get('cross_platform_validation'):
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_conversion_potential(self, signal: Dict) -> float:
        """Estimate conversion potential based on pain point intensity"""
        score = 0.5
        
        # Check for pain point keywords
        pain_keywords = ['struggling', 'need', 'help', 'how to', 'can\'t', 'frustrated', 'problem']
        content = signal.get('content', '').lower()
        
        pain_count = sum(1 for keyword in pain_keywords if keyword in content)
        score += min(pain_count * 0.1, 0.3)
        
        # Check for urgency
        urgency_keywords = ['now', 'urgent', 'asap', 'today', 'immediately']
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in content)
        score += min(urgency_count * 0.05, 0.2)
        
        return min(score, 1.0)
    
    def calculate_speed_to_market(self, signal: Dict) -> float:
        """Estimate how quickly we can create an offer for this signal"""
        score = 0.5
        
        # Digital products can be created quickly
        if signal.get('signal_type') in ['tool_need', 'template_request']:
            score += 0.3
        
        # Simple pain points are faster to address
        content_length = len(signal.get('content', ''))
        if content_length < 500:  # Simple, focused problem
            score += 0.2
        
        return min(score, 1.0)
    
    def save_signal(self, signal: Signal):
        """Save signal to database"""
        try:
            self.db.add(signal)
            self.db.commit()
            self.db.refresh(signal)
        except Exception as e:
            self.db.rollback()
            print(f"Error saving signal: {e}")
    
    def get_top_signals(self, limit: int = 10) -> List[Signal]:
        """Get top-scoring unprocessed signals"""
        return (
            self.db.query(Signal)
            .filter(Signal.status == "new")
            .order_by(Signal.overall_score.desc())
            .limit(limit)
            .all()
        )


class TwitterSignalCollector:
    """Collect signals from Twitter/X"""
    
    async def collect(self) -> List[Dict]:
        """Collect trending topics and pain points from Twitter"""
        signals = []
        
        if not settings.twitter_bearer_token:
            return signals
        
        try:
            # Search for pain point tweets
            search_queries = [
                "struggling with -is:retweet",
                "need help with -is:retweet",
                "how to automate -is:retweet",
                "looking for a tool -is:retweet",
                "template for -is:retweet"
            ]
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}
                
                for query in search_queries:
                    try:
                        # Twitter API v2 search
                        url = "https://api.twitter.com/2/tweets/search/recent"
                        params = {
                            "query": query,
                            "max_results": 10,
                            "tweet.fields": "public_metrics,created_at"
                        }
                        
                        response = await client.get(url, headers=headers, params=params, timeout=10.0)
                        
                        if response.status_code == 200:
                            data = response.json()
                            for tweet in data.get('data', []):
                                signals.append({
                                    'source': 'twitter',
                                    'signal_type': 'pain_point',
                                    'content': tweet.get('text'),
                                    'engagement_count': (
                                        tweet.get('public_metrics', {}).get('like_count', 0) +
                                        tweet.get('public_metrics', {}).get('retweet_count', 0)
                                    ),
                                    'data': tweet
                                })
                    except Exception as e:
                        print(f"Error searching Twitter for '{query}': {e}")
        
        except Exception as e:
            print(f"Twitter collection error: {e}")
        
        return signals


class RedditSignalCollector:
    """Collect signals from Reddit"""
    
    async def collect(self) -> List[Dict]:
        """Collect pain points and opportunities from Reddit"""
        signals = []
        
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return signals
        
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
            
            # Target subreddits with high intent
            subreddits = [
                'entrepreneur', 'smallbusiness', 'productivity',
                'learnprogramming', 'marketing', 'passive_income'
            ]
            
            for subreddit_name in subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    
                    # Get hot posts
                    for submission in subreddit.hot(limit=10):
                        if self._is_pain_point(submission.title) or self._is_pain_point(submission.selftext):
                            signals.append({
                                'source': 'reddit',
                                'signal_type': 'pain_point',
                                'content': f"{submission.title}\n{submission.selftext[:500]}",
                                'engagement_count': submission.score + submission.num_comments,
                                'data': {
                                    'subreddit': subreddit_name,
                                    'url': submission.url,
                                    'score': submission.score,
                                    'comments': submission.num_comments
                                }
                            })
                except Exception as e:
                    print(f"Error collecting from r/{subreddit_name}: {e}")
        
        except Exception as e:
            print(f"Reddit collection error: {e}")
        
        return signals
    
    def _is_pain_point(self, text: str) -> bool:
        """Check if text contains pain point indicators"""
        if not text:
            return False
        
        pain_keywords = [
            'how do i', 'how can i', 'help with', 'struggling',
            'need advice', 'recommendations', 'looking for',
            'best way to', 'tips for'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in pain_keywords)


class MarketplaceSignalCollector:
    """Collect signals from marketplace trends"""
    
    async def collect(self) -> List[Dict]:
        """Collect trending product needs from marketplaces"""
        signals = []
        
        try:
            # Scrape Gumroad trending (publicly available)
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get("https://gumroad.com/discover", timeout=10.0)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract trending product categories
                        # This is a simplified example
                        categories = soup.find_all(class_='product-category')
                        
                        for cat in categories[:10]:
                            signals.append({
                                'source': 'marketplace',
                                'signal_type': 'trend',
                                'content': cat.get_text(strip=True),
                                'engagement_count': 0,
                                'data': {'platform': 'gumroad'}
                            })
                
                except Exception as e:
                    print(f"Error scraping marketplace: {e}")
        
        except Exception as e:
            print(f"Marketplace collection error: {e}")
        
        return signals


async def run_signal_scan():
    """Run a full signal scan across all sources"""
    compressor = SignalCompressor()
    signals = await compressor.scan_all_sources()
    print(f"Collected and compressed {len(signals)} signals")
    return signals


if __name__ == "__main__":
    # Test the signal compression engine
    asyncio.run(run_signal_scan())
