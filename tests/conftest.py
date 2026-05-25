"""
Pytest configuration and shared fixtures for FastAPI tests
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Create a test client with a fresh app state.
    Resets activities to their initial state before each test.
    """
    # Define the initial state of activities
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Team-based basketball practice and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["nina@mergington.edu", "alex@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events to build athletics skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "noah@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu", "sam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stage production, and theater performances",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["lily@mergington.edu", "mason@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "logan@mergington.edu"]
        }
    }
    
    # Reset the app's activities to initial state
    activities.clear()
    activities.update(initial_activities)
    
    # Return a test client
    return TestClient(app)


@pytest.fixture
def available_activity():
    """Fixture providing an activity name with available slots"""
    return "Programming Class"


@pytest.fixture
def full_activity():
    """Fixture providing an activity that is at capacity. Create one by filling it."""
    activity_name = "Math Olympiad"  # max_participants: 16, currently has 2
    return activity_name


@pytest.fixture
def test_email():
    """Fixture providing a test email not yet registered for activities"""
    return "testuser@mergington.edu"


@pytest.fixture
def registered_email():
    """Fixture providing an email already registered for an activity"""
    return "emma@mergington.edu"  # Registered in "Programming Class"
