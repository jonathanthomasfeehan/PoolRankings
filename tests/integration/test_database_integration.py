from app import database as db
from unittest.mock import patch, MagicMock
import pytest
import json
import google.cloud.firestore_v1 as firestore
import os
import google.auth.credentials
from google.api_core import exceptions as google_exceptions

@pytest.fixture(scope='module', autouse=True)
def seed_database():
    """Fixure to seed the database for integration tests."""
    with open('tests/integration/database_seed.json', 'r') as f:
        seed_data = json.load(f)
    
    for collection_name, documents in seed_data.items():
        collection=db.database.collection(collection_name) 
        # ???
        for doc in documents:
            doc_ref = collection.document(doc['id'])
            doc_ref.set(doc)
    


def test_emulator_environment():
    """Test if the Firestore emulator is being used."""
    assert os.getenv("FIRESTORE_EMULATOR_HOST"), "Firestore emulator not set"
    assert os.getenv("FIRESTORE_PROJECT_ID") == "demo-project", "Incorrect project ID"

def test_emulator_has_seed_data():
    users = db.database.collection("USERS").get()
    assert len(users) > 0, "Expected USERS seed data present"


def test_database_create():
    """Test the database_create function."""
    data = {
        'FirstName': 'John',
        'LastName': 'Doe',
        'Username': 'johndoe',
        'Password': 'hashed_password'
    }

    result = db.database_create(db.USERS, data)
    assert result is not None, "Expected database_create to return a result"
    doc = db.USERS.document(result[1].id).get()
    assert doc.exists, "Expected document to be created in USERS collection"
    doc = doc.to_dict()
    assert doc['FirstName'] == 'John', "Expected FirstName to be 'John' in created document"
    assert doc['LastName'] == 'Doe', "Expected LastName to be 'Doe' in created document"
    assert doc['Username'] == 'johndoe', "Expected Username to be 'johndoe' in created document"
    assert 'Password' in doc, "Expected Password field to be present in created document"
    # db.database_create()





def database_update():
    """Test the database_update function."""

def test_database_update_failure():
    """Test the database_update function with failure scenario."""

def test_database_update_with_query():
    """Test the database_update_with_query function."""

def test_database_update_with_query_failure():
    """Test the database_update_with_query function with failure scenario."""

def test_database_update_with_query_no_results():
    """Test the database_update_with_query function when no results are found."""

def test_database_get():
    """Test the database_get function."""

def test_database_get_failure():
    """Test the database_get function with failure scenario."""

def test_database_get_no_results():
    """Test the database_get function when no results are found."""

def test_database_delete():
    """Test the database_delete function."""

def test_database_delete_failure():
    """Test the database_delete function with failure scenario."""

def test_database_query():
    """Test the database_query function."""

def test_database_queryOne():
    """Test the database_query_one function."""

def test_database_query_one_failure():
    """Test the database_query_one function with failure scenario."""

def test_database_increment():
    """Test the database_increment function."""

def test_database_increment_failure():
    """Test the database_increment function with failure scenario."""

def test_database_get_user_by_username():
    """Test the get_user_by_username function."""

def test_database_get_user_by_username_failure():
    """Test the get_user_by_username function with failure scenario."""

def test_database_get_user_by_username_no_results():
    """Test the get_user_by_username function when no results are found."""

def test_database_update_user_rating():
    """Test the update_user_rating function."""

def test_database_update_user_rating_failure():
    """Test the update_user_rating function with failure scenario."""

def test_database_get_pending_matches():
    """Test the get_pending_matches function."""
def test_database_get_pending_matches_failure():
    """Test the get_pending_matches function with failure scenario."""
def test_database_get_pending_matches_no_results():
    """Test the get_pending_matches function when no results are found."""
def test_database_get_pending_matches_empty():
    """Test the get_pending_matches function when the collection is empty."""
def test_database_update_player_rankings():
    """Test the update_player_rankings function."""
def test_database_update_player_rankings_failure():
    """Test the update_player_rankings function with failure scenario."""
def test_database_update_player_rankings_no_results():
    """Test the update_player_rankings function when no results are found."""
