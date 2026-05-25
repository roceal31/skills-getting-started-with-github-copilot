"""
Integration tests for the Mergington High School API

Tests cover all endpoints including happy paths and error scenarios:
- GET / (redirect to static files)
- GET /activities (retrieve all activities)
- POST /activities/{activity_name}/signup (enroll in activity)
- DELETE /activities/{activity_name}/withdraw (unenroll from activity)
"""
import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Track and Field" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Science Club" in data
        assert "Math Olympiad" in data
        
        # Total of 9 activities
        assert len(data) == 9
    
    def test_activities_have_correct_structure(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity {activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_activities_have_participants(self, client):
        """Test that activities include their participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have michael and daniel
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Programming Class should have emma and sophia
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client, available_activity, test_email):
        """Test successful signup for an activity"""
        response = client.post(
            f"/activities/{available_activity}/signup",
            params={"email": test_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert available_activity in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[available_activity]["participants"]
    
    def test_signup_activity_not_found(self, client, test_email):
        """Test signup returns 404 when activity doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": test_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client, available_activity, registered_email):
        """Test signup returns 400 when email is already registered"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": registered_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"]
    
    def test_signup_activity_full(self, client, test_email):
        """Test signup returns 400 when activity is at capacity"""
        # Use Chess Club which has max_participants=12 and currently 2 enrolled
        # Fill it up to capacity
        activity_name = "Chess Club"
        
        # Add participants until full
        for i in range(10):  # Add 10 more (2 + 10 = 12, which is max)
            email = f"student{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Now try to add one more - should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Activity is full" in data["detail"]
    
    def test_signup_updates_participant_count(self, client, available_activity, test_email):
        """Test that signup properly updates the participant count"""
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[available_activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{available_activity}/signup",
            params={"email": test_email}
        )
        
        # Check updated state
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[available_activity]["participants"])
        
        assert updated_count == initial_count + 1


class TestWithdrawFromActivity:
    """Tests for DELETE /activities/{activity_name}/withdraw endpoint"""
    
    def test_withdraw_successfully_removes_participant(self, client):
        """Test successful withdrawal from an activity"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already registered
        
        response = client.delete(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_withdraw_activity_not_found(self, client):
        """Test withdraw returns 404 when activity doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/withdraw",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_withdraw_email_not_registered(self, client, test_email):
        """Test withdraw returns 400 when email is not registered for activity"""
        response = client.delete(
            "/activities/Chess Club/withdraw",
            params={"email": test_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_withdraw_updates_participant_count(self, client):
        """Test that withdrawal properly updates the participant count"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Withdraw
        client.delete(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        
        # Check updated state
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        
        assert updated_count == initial_count - 1


class TestSignupAndWithdrawFlow:
    """Integration tests for signup and withdraw workflows"""
    
    def test_signup_then_withdraw_workflow(self, client, available_activity, test_email):
        """Test complete workflow: signup then withdraw"""
        # Verify user is not registered initially
        initial_response = client.get("/activities")
        assert test_email not in initial_response.json()[available_activity]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{available_activity}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200
        
        # Verify user is registered
        after_signup_response = client.get("/activities")
        assert test_email in after_signup_response.json()[available_activity]["participants"]
        
        # Withdraw
        withdraw_response = client.delete(
            f"/activities/{available_activity}/withdraw",
            params={"email": test_email}
        )
        assert withdraw_response.status_code == 200
        
        # Verify user is no longer registered
        final_response = client.get("/activities")
        assert test_email not in final_response.json()[available_activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client, test_email):
        """Test signing up for multiple different activities"""
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": test_email}
            )
            assert response.status_code == 200
        
        # Verify signed up for all
        final_response = client.get("/activities")
        activities_data = final_response.json()
        for activity in activities_to_join:
            assert test_email in activities_data[activity]["participants"]
    
    def test_signup_after_someone_withdraws(self, client, test_email):
        """Test that signup works for full activity after someone withdraws"""
        activity_name = "Chess Club"
        other_email = "newstudent@mergington.edu"
        
        # Fill the activity to capacity
        for i in range(10):  # Currently has 2, max is 12, so add 10 to reach capacity
            email = f"filler{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Verify it's full
        full_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert full_response.status_code == 400
        
        # Someone withdraws
        client.delete(
            f"/activities/{activity_name}/withdraw",
            params={"email": "michael@mergington.edu"}
        )
        
        # Now signup should work
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200
