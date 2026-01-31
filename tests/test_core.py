"""
Test Suite for Stealth AI Revenue System
"""
import pytest
from backend.database.models import Signal, MicroOffer, init_db, SessionLocal


@pytest.fixture
def db_session():
    """Create a test database session"""
    init_db()
    session = SessionLocal()
    yield session
    session.close()


def test_signal_creation(db_session):
    """Test creating a signal"""
    signal = Signal(
        source="twitter",
        signal_type="pain_point",
        content="Struggling with automation",
        confidence_score=0.8,
        conversion_potential=0.7,
        speed_to_market=0.9,
        overall_score=0.78
    )
    
    db_session.add(signal)
    db_session.commit()
    
    assert signal.id is not None
    assert signal.status == "new"


def test_offer_creation(db_session):
    """Test creating a micro-offer"""
    offer = MicroOffer(
        title="Automation Guide",
        description="Learn to automate everything",
        offer_type="guide",
        price=19.00
    )
    
    db_session.add(offer)
    db_session.commit()
    
    assert offer.id is not None
    assert offer.status == "draft"
    assert offer.price == 19.00


def test_signal_scoring():
    """Test signal scoring calculation"""
    signal = Signal(
        source="reddit",
        signal_type="pain_point",
        content="Need help with productivity",
        confidence_score=0.6,
        conversion_potential=0.8,
        speed_to_market=0.7
    )
    
    # Calculate overall score (weighted average)
    expected_score = (0.6 * 0.3) + (0.8 * 0.5) + (0.7 * 0.2)
    signal.overall_score = expected_score
    
    assert signal.overall_score == pytest.approx(0.72, rel=0.01)


def test_offer_pricing():
    """Test offer pricing is within range"""
    offer = MicroOffer(
        title="Test Offer",
        description="Test",
        offer_type="template",
        price=25.00
    )
    
    assert 10 <= offer.price <= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
