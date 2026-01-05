import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test"""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Tennis Club"
    email = "testuser@example.com"

    # Ensure the test email is not present initially
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]

    # Sign up
    r = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert r.status_code == 200
    assert f"Signed up {email}" in r.json().get("message", "")

    # Confirm added
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Unregister
    r = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert r.status_code == 200
    assert f"Unregistered {email}" in r.json().get("message", "")

    # Confirm removed
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_unregister_nonexistent():
    activity = "Chess Club"
    email = "notfound@example.com"
    r = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert r.status_code == 404


def test_signup_existing_user():
    activity = "Chess Club"
    existing = "michael@mergington.edu"
    r = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(existing)}")
    assert r.status_code == 400
