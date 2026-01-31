"""
Distribution Automation System
Generates and posts content across platforms
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx
import json
from ..database.models import MicroOffer, DistributionPost, SessionLocal
from config.settings import settings


class ContentGenerator:
    """AI-powered content generator for various platforms"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def generate_twitter_thread(self, offer: MicroOffer) -> List[str]:
        """Generate a Twitter thread promoting the offer"""
        
        # Thread structure: Hook → Problem → Solution → Benefits → CTA
        content_data = offer.content or {}
        
        tweets = [
            # Hook tweet
            f"🚀 Struggling with {offer.title.split(':')[-1] if ':' in offer.title else offer.title[:50]}?\n\nI just created something that might help...",
            
            # Problem tweet
            f"The problem: Most people waste hours trying to figure this out.\n\nThere has to be a better way.",
            
            # Solution tweet  
            f"That's why I built {offer.title}.\n\nIt's a {offer.offer_type} that does the heavy lifting for you.",
            
            # Benefits tweet
            f"What you get:\n" + "\n".join(f"✓ {item}" for item in content_data.get('key_deliverables', [])[:3]),
            
            # Social proof / uniqueness
            f"Why this is different:\n{content_data.get('unique_angle', 'Simple, actionable, and proven')}",
            
            # CTA tweet
            f"Ready to solve this once and for all?\n\nGet instant access for just ${offer.price}\n\n{offer.landing_page_url}\n\n30-day money-back guarantee 💯"
        ]
        
        return tweets
    
    async def generate_reddit_post(self, offer: MicroOffer, subreddit: str) -> Dict:
        """Generate a value-add Reddit post (following platform rules)"""
        
        content_data = offer.content or {}
        
        # Reddit posts must provide value first, not be spammy
        title = f"I created a {offer.offer_type} to help with {offer.title.split(':')[-1] if ':' in offer.title else offer.title[:50]}"
        
        body = f"""Hey everyone,

I've been working on solving [the problem] and wanted to share what I learned.

**The Problem:**
{offer.description[:200]}

**What I Built:**
{content_data.get('unique_angle', 'A practical solution')}

**What's Included:**
{chr(10).join(f"- {item}" for item in content_data.get('key_deliverables', []))}

I'm offering this at ${offer.price} with a 30-day money-back guarantee.

Link: {offer.landing_page_url}

Happy to answer any questions!
"""
        
        return {
            'title': title,
            'body': body,
            'subreddit': subreddit
        }
    
    async def generate_linkedin_post(self, offer: MicroOffer) -> str:
        """Generate LinkedIn post"""
        
        content_data = offer.content or {}
        
        post = f"""💡 Quick Win for Entrepreneurs:

After spending countless hours on {offer.title.split(':')[-1] if ':' in offer.title else offer.title[:50]}, I decided to create a solution.

The result? {offer.title}

Here's what makes it different:
{chr(10).join(f"→ {feature}" for feature in content_data.get('features', [])[:3])}

If you're facing this challenge, check it out: {offer.landing_page_url}

Price: ${offer.price} | 30-day guarantee

#entrepreneurship #productivity #automation
"""
        
        return post
    
    async def generate_video_script(self, offer: MicroOffer) -> str:
        """Generate short-form video script for TikTok/YouTube Shorts"""
        
        script = f"""[Hook - 0-3 seconds]
You're wasting hours on {offer.title.split(':')[-1] if ':' in offer.title else 'this'}.

[Problem - 3-10 seconds]
I used to struggle with the same thing until I found a better way.

[Solution - 10-20 seconds]
I created {offer.title} - a {offer.offer_type} that automates the whole process.

[Benefits - 20-30 seconds]
Now you can:
{chr(10).join(f"✓ {item}" for item in (offer.content or {}).get('key_deliverables', [])[:2])}

[CTA - 30-35 seconds]
Link in bio. ${offer.price}. 30-day guarantee.

[Visual suggestions]
- Show before/after comparison
- Screen recording of the tool
- Text overlays with key points
"""
        
        return script


class DistributionScheduler:
    """Schedule and manage content distribution"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.platforms = {
            'twitter': TwitterPoster(),
            'reddit': RedditPoster(),
            'linkedin': LinkedInPoster()
        }
    
    async def schedule_distribution(self, offer: MicroOffer, platforms: List[str]) -> List[DistributionPost]:
        """Schedule content across multiple platforms"""
        
        generator = ContentGenerator()
        posts = []
        
        for platform in platforms:
            try:
                if platform == 'twitter':
                    tweets = await generator.generate_twitter_thread(offer)
                    for i, tweet in enumerate(tweets):
                        post = DistributionPost(
                            offer_id=offer.id,
                            platform='twitter',
                            content=tweet,
                            scheduled_at=datetime.utcnow() + timedelta(hours=i),
                            status='scheduled'
                        )
                        self.db.add(post)
                        posts.append(post)
                
                elif platform == 'reddit':
                    reddit_content = await generator.generate_reddit_post(offer, 'entrepreneur')
                    post = DistributionPost(
                        offer_id=offer.id,
                        platform='reddit',
                        content=json.dumps(reddit_content),
                        scheduled_at=datetime.utcnow() + timedelta(hours=2),
                        status='scheduled'
                    )
                    self.db.add(post)
                    posts.append(post)
                
                elif platform == 'linkedin':
                    linkedin_content = await generator.generate_linkedin_post(offer)
                    post = DistributionPost(
                        offer_id=offer.id,
                        platform='linkedin',
                        content=linkedin_content,
                        scheduled_at=datetime.utcnow() + timedelta(hours=4),
                        status='scheduled'
                    )
                    self.db.add(post)
                    posts.append(post)
            
            except Exception as e:
                print(f"Error scheduling {platform}: {e}")
        
        self.db.commit()
        return posts
    
    async def post_scheduled_content(self):
        """Post all scheduled content that's due"""
        
        if not settings.content_posting_enabled:
            print("Content posting is disabled")
            return
        
        # Get posts that are scheduled and due
        now = datetime.utcnow()
        posts = self.db.query(DistributionPost).filter(
            DistributionPost.status == 'scheduled',
            DistributionPost.scheduled_at <= now
        ).all()
        
        for post in posts:
            try:
                platform_poster = self.platforms.get(post.platform)
                if platform_poster:
                    success = await platform_poster.post(post)
                    
                    if success:
                        post.status = 'posted'
                        post.posted_at = datetime.utcnow()
                    else:
                        post.status = 'failed'
                    
                    self.db.commit()
            
            except Exception as e:
                print(f"Error posting to {post.platform}: {e}")
                post.status = 'failed'
                self.db.commit()


class TwitterPoster:
    """Post content to Twitter"""
    
    async def post(self, post: DistributionPost) -> bool:
        """Post a tweet"""
        
        if not settings.twitter_api_key:
            print("Twitter API not configured")
            return False
        
        try:
            import tweepy
            
            auth = tweepy.OAuthHandler(settings.twitter_api_key, settings.twitter_api_secret)
            auth.set_access_token(settings.twitter_access_token, settings.twitter_access_secret)
            api = tweepy.API(auth)
            
            # Post tweet
            tweet = api.update_status(post.content)
            
            # Store tweet URL
            post.post_url = f"https://twitter.com/user/status/{tweet.id}"
            
            return True
        
        except Exception as e:
            print(f"Error posting to Twitter: {e}")
            return False


class RedditPoster:
    """Post content to Reddit"""
    
    async def post(self, post: DistributionPost) -> bool:
        """Post to Reddit"""
        
        if not settings.reddit_client_id:
            print("Reddit API not configured")
            return False
        
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
            
            content = json.loads(post.content)
            subreddit = reddit.subreddit(content['subreddit'])
            
            # Post to subreddit
            submission = subreddit.submit(
                title=content['title'],
                selftext=content['body']
            )
            
            post.post_url = submission.url
            
            return True
        
        except Exception as e:
            print(f"Error posting to Reddit: {e}")
            return False


class LinkedInPoster:
    """Post content to LinkedIn"""
    
    async def post(self, post: DistributionPost) -> bool:
        """Post to LinkedIn"""
        
        # LinkedIn API requires OAuth setup
        # For MVP, we can just store the content for manual posting
        # or use a service like Buffer/Hootsuite API
        
        print(f"LinkedIn post ready (manual posting required):\n{post.content}")
        
        # For now, mark as posted
        return True


class EngagementAutomation:
    """Automate engagement on posts"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def respond_to_comments(self, post: DistributionPost):
        """Auto-respond to comments with helpful information"""
        
        # This would integrate with each platform's API
        # For safety and ToS compliance, responses should be:
        # 1. Helpful and add value
        # 2. Not spammy
        # 3. Follow platform rules
        
        # Example response templates
        responses = {
            'question': "Great question! {answer}. Let me know if you need more details.",
            'positive': "Thanks so much! Really appreciate the feedback 🙏",
            'concern': "That's a fair point. Here's how we address that: {explanation}",
            'interest': "Awesome! You can check it out here: {link}. Happy to answer any questions!"
        }
        
        # Implementation would fetch comments and respond appropriately
        pass
    
    async def track_engagement(self, post: DistributionPost):
        """Track engagement metrics on posts"""
        
        # Fetch engagement data from platform APIs
        # Update post.engagement_count
        
        pass


if __name__ == "__main__":
    # Test the distribution system
    async def test():
        from ..database.models import MicroOffer
        
        db = SessionLocal()
        offer = db.query(MicroOffer).first()
        
        if offer:
            scheduler = DistributionScheduler()
            posts = await scheduler.schedule_distribution(offer, ['twitter', 'reddit', 'linkedin'])
            print(f"Scheduled {len(posts)} posts")
    
    asyncio.run(test())
