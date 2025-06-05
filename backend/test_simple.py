"""Simple test to verify environment is working."""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database_connection():
    """Test that we can connect to the test database."""
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    
    # Test connection
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_basic_math():
    """Test that pytest is working."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 