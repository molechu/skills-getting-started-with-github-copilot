"""
Pytest configuration and fixtures for the activity management API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a TestClient instance for the FastAPI app.
    Resets the activities database before each test to ensure test isolation.
    """
    # Reset activities to a clean state before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Mondays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": []
        }
    })
    
    return TestClient(app)
