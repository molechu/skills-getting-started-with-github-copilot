"""
Tests for the Mergington High School activities API endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure"""
        # Arrange
        # (Test client is set up by fixture with pre-populated activities)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Empty Activity" in data
        
    def test_activity_has_required_fields(self, client):
        """Test that activities have all required fields"""
        # Arrange
        # (Test client is set up by fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
    def test_participants_list_structure(self, client):
        """Test that participants are returned as a list of emails"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        # Assert
        assert isinstance(participants, list)
        assert len(participants) == 2
        assert "michael@mergington.edu" in participants
        assert "daniel@mergington.edu" in participants
        
    def test_empty_activity_has_empty_participants(self, client):
        """Test that activities with no participants return an empty list"""
        # Arrange
        expected_count = 0
        
        # Act
        response = client.get("/activities")
        data = response.json()
        participants = data["Empty Activity"]["participants"]
        
        # Assert
        assert isinstance(participants, list)
        assert len(participants) == expected_count


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful student signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Empty Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Signup response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Assert - Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test signup fails when activity doesn't exist"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_signup_duplicate_student(self, client):
        """Test signup fails when student is already registered"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_activity_full(self, client):
        """Test signup fails when activity is at max capacity"""
        # Arrange
        # Chess Club has max_participants=2 and already has 2 participants
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()
        
    def test_signup_adds_student_to_list(self, client):
        """Test that signup actually adds the student to the participants list"""
        # Arrange
        email = "testuser@mergington.edu"
        activity_name = "Programming Class"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        activities_data = response.json()
        participants = activities_data[activity_name]["participants"]
        
        assert email in participants
        assert len(participants) == 2  # emma + testuser


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful student unregistration from an activity"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Unregister response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Assert - Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
        assert "daniel@mergington.edu" in activities_data[activity_name]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister fails when activity doesn't exist"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_unregister_participant_not_found(self, client):
        """Test unregister fails when participant is not signed up"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
        
    def test_unregister_reduces_participant_count(self, client):
        """Test that unregister actually removes the participant"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        updated_count = len(response.json()[activity_name]["participants"])
        
        assert updated_count == initial_count - 1


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        # Arrange
        expected_status_code = 307
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status_code
        assert expected_redirect_path in response.headers["location"]
