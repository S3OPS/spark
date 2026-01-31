from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/stealth_ai.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Signal(Base):
    """Stores compressed signals from various platforms"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), index=True)  # twitter, reddit, marketplace
    signal_type = Column(String(50))  # trend, pain_point, opportunity
    content = Column(Text)
    compressed_data = Column(JSON)
    confidence_score = Column(Float)
    conversion_potential = Column(Float)
    speed_to_market = Column(Float)
    overall_score = Column(Float, index=True)
    status = Column(String(20), default="new")  # new, processed, converted, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class MicroOffer(Base):
    """Stores generated micro-offers"""
    __tablename__ = "micro_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, nullable=True)
    title = Column(String(200))
    description = Column(Text)
    offer_type = Column(String(50))  # guide, template, tool, course, resource_list
    price = Column(Float)
    cost_to_create = Column(Float, default=0.0)
    content = Column(JSON)  # Generated content/outline
    landing_page_url = Column(String(500), nullable=True)
    payment_link = Column(String(500), nullable=True)
    status = Column(String(20), default="draft")  # draft, deployed, active, paused, retired
    created_at = Column(DateTime, default=datetime.utcnow)
    deployed_at = Column(DateTime, nullable=True)


class Analytics(Base):
    """Tracks performance metrics for each offer"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    refunds = Column(Float, default=0.0)
    platform_fees = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    click_through_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    
class DistributionPost(Base):
    """Tracks content distributed across platforms"""
    __tablename__ = "distribution_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, index=True)
    platform = Column(String(50))  # twitter, reddit, linkedin, tiktok
    content = Column(Text)
    media_url = Column(String(500), nullable=True)
    post_url = Column(String(500), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    engagement_count = Column(Integer, default=0)
    status = Column(String(20), default="scheduled")  # scheduled, posted, failed


class Revenue(Base):
    """Tracks all revenue transactions"""
    __tablename__ = "revenue"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, index=True)
    amount = Column(Float)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50))  # stripe, paypal, crypto
    transaction_id = Column(String(200), unique=True)
    customer_email = Column(String(200), nullable=True)
    platform_fee = Column(Float, default=0.0)
    net_amount = Column(Float)
    status = Column(String(20), default="pending")  # pending, completed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)


class EmailSubscriber(Base):
    """Email list for customer lifetime value"""
    __tablename__ = "email_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True)
    source_offer_id = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    last_email_sent = Column(DateTime, nullable=True)
    total_purchases = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, unsubscribed


class AutomationConfig(Base):
    """Configuration for automation rules"""
    __tablename__ = "automation_config"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    config_type = Column(String(50))  # reinvestment, scaling, content_schedule
    settings = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
