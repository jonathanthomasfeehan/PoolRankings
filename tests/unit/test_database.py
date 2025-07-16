from app import database as db
from unittest.mock import patch, MagicMock
import pytest
from google.api_core import exceptions as google_exceptions
import google.cloud.firestore_v1 as firestore


@pytest.fixture(scope='function')
def firestore_write_failure():
    """Fixture to simulate Firestore write failure."""
    with patch.object(firestore.DocumentReference, 'set', side_effect=google_exceptions.GoogleAPICallError("Simulated write failure")):
        yield



# TODO: move fixture inside test function
@patch("app.database.database.collection")
def test_database_create_success(mock_collection):
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "mocked_id"
    mock_doc_ref.set.return_value = "mocked_result"

    mock_collection.return_value.document.return_value = mock_doc_ref

    mock_collection_obj = MagicMock()
    mock_collection_obj.id = "users"

    data = {'FirstName': 'John', 'LastName': 'Doe'}
    result, doc_ref = db.database_create(mock_collection_obj, data)

    # Check return values
    assert result == "mocked_result"
    assert doc_ref.id == "mocked_id"

    # Check that doc_ref.set() was called with the correct data
    assert data['id'] == "mocked_id"
    

def test_database_create_failure(firestore_write_failure):
    """Test the database_create function with failure scenario."""
    data = {
        'FirstName': 'John',
        'LastName': 'Doe',
        'Username': 'johndoe',
        'Password': 'hashed_password'
    }
    result = db.database_create(db.USERS, data)
    assert result == (None,None), "Expected database_create to return None on failure"

@patch("app.database.database.collection")
def test_database_create_mutates_data(mock_collection):
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "some-id"
    mock_doc_ref.set.return_value = True

    mock_collection.return_value.document.return_value = mock_doc_ref

    mock_collection_obj = MagicMock()
    mock_collection_obj.id = "posts"

    data = {}
    db.database_create(mock_collection_obj, data)

    assert data["id"] == "some-id"


@patch("app.database.database.collection")
def test_database_update_failure(mock_collection, firestore_write_failure):
    """Test the database_update function with failure scenario."""
    doc_ref = db.USERS.document()

    data = {
        'FirstName': 'John',
        'LastName': 'Doe',
        'Username': 'johndoe',
        'Password': 'hashed_password'
    }
    result = db.database_update(db.USERS, doc_ref, data)
    assert result is False, "Expected database_update to return False on failure"

@patch("app.database.database_update")
def test_database_update_with_query(mock_update):
    """Test the database_update_with_query function."""
    filters = [('field1', '==', 'value1')]
    data = {'field2': 'value2'}

    query_stream_mock = MagicMock()
    query_stream_mock.where.return_value = query_stream_mock

    doc1 = MagicMock()
    doc1.id = "doc1_id"
    doc2 = MagicMock()
    doc2.id = "doc2_id"
    query_stream_mock.stream.return_value = [doc1, doc2]
    mock_update.return_value = True

    db.database_update_with_query(query_stream_mock, filters, data)

    assert mock_update.called, "Expected database update to be called"
    mock_update.assert_any_call(query_stream_mock, "doc1_id", data)
    mock_update.assert_any_call(query_stream_mock, "doc2_id", data)

    # Check that the query was built correctly
@patch("app.database.database_update")
def test_database_update_with_query_failure(mock_update):
    """Test the database_update_with_query function with failure scenario."""
    filters = [('field1', '==', 'value1')]
    data = {'field2': 'value2'}

    query_stream_mock = MagicMock()
    query_stream_mock.where.return_value = query_stream_mock

    doc1 = MagicMock()
    doc1.id = "doc1_id"
    doc2 = MagicMock()
    doc2.id = "doc2_id"
    query_stream_mock.stream.return_value = [doc1, doc2]
    mock_update.side_effect = Exception("Simulated update failure")

    result = db.database_update_with_query(query_stream_mock, filters, data)
    assert result == False 

@patch("app.database.database_update")
def test_database_update_with_query_no_results(mock_update):
    """Test the database_update_with_query function when no results are found."""
    # TODO: Update to handle no results case
    filters = [('field1', '==', 'value1')]
    data = {'field2': 'value2'}

    query_stream_mock = MagicMock()
    query_stream_mock.where.return_value = query_stream_mock


    query_stream_mock.stream.return_value = []

    result = db.database_update_with_query(query_stream_mock, filters, data)
    assert result == False 

@patch("google.cloud.firestore_v1.DocumentReference.get")
def test_database_get(doc_get_mock):
    """Test the database_get function."""
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {'field1': 'value1', 'field2': 'value2'}
    mock_doc.exists = True
    doc_get_mock.return_value = mock_doc
    result = db.database_get(db.USERS, 'some_doc_id')
    assert result == {'field1': 'value1', 'field2': 'value2'}, "Expected database_get to return the document data"

@patch("google.cloud.firestore_v1.DocumentReference.get")
def test_database_get_failure(doc_get_mock):
    """Test the database_get function with failure scenario."""
    doc_get_mock.side_effect = google_exceptions.GoogleAPICallError("Simulated get failure")
    with pytest.raises(google_exceptions.GoogleAPICallError):
        db.database_get(db.USERS, 'some_doc_id')
     
@patch("google.cloud.firestore_v1.DocumentReference.get")
def test_database_get_no_results(doc_get_mock):
    """Test the database_get function when no results are found."""
    mock_doc = MagicMock()
    mock_doc.exists = False
    doc_get_mock.return_value = mock_doc
    result = db.database_get(db.USERS, 'some_doc_id')
    assert result is None, "Expected database_get to return None when no document is found"

@patch("google.cloud.firestore_v1.DocumentReference.delete")
def test_database_delete(mock_delete):
    """Test the database_delete function."""
    mock_delete_result = MagicMock()
    mock_delete.return_value = mock_delete_result
    db.database_delete(db.USERS, 'some_doc_id')

@patch("google.cloud.firestore_v1.DocumentReference.delete")
def test_database_delete_failure(mock_delete):
    """Test the database_delete function with failure scenario."""
    mock_delete.side_effect = google_exceptions.GoogleAPICallError("Simulated delete failure")
    with pytest.raises(google_exceptions.GoogleAPICallError):
        db.database_delete(db.USERS, 'some_doc_id')


def test_database_query():
    """Test the database_query function."""
    filters = [('field1', '==', 'value1')]
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {'field1': 'value1', 'field2': 'value2'}
    mock_query.where.return_value = mock_query
    mock_query.stream.return_value = iter([mock_doc])
    mock_query.get.return_value = []
    mock_collection.where.return_value = mock_query

    result = db.database_query(mock_collection, filters)
    assert result == [{'field1': 'value1', 'field2': 'value2'}], "Expected database_query to return a dict"

def test_database_query_failure():
    """Test the database_query function with failure scenario."""
    filters = [('field1', '==', 'value1')]
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.stream.side_effect = google_exceptions.GoogleAPICallError("Simulated query failure")
    mock_collection.where.return_value = mock_query

    with pytest.raises(google_exceptions.GoogleAPICallError):
        db.database_query(mock_collection, filters)

def test_database_query_no_results():
    """Test the database_query function when no results are found."""
    filters = [('field1', '==', 'value1')]
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.stream.return_value = iter([])
    mock_collection.where.return_value = mock_query

    result = db.database_query(mock_collection, filters)
    assert result == [], "Expected database_query to return an empty list when no results are found"

def test_database_queryOne():
    """Test the database_query_one function."""
    filters = [('field1', '==', 'value1')]
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {'field1': 'value1', 'field2': 'value2'}
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_collection.where.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.get.return_value = [mock_doc]
    result = db.database_query_one(mock_collection, filters)
    assert result == {'field1': 'value1', 'field2': 'value2'}, "Expected database_query_one to return a dict"

def test_database_queryOne_failure():
    """Test the database_query_one function with failure scenario."""
    filters = [('field1', '==', 'value1')]
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_collection.where.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.get.side_effect = google_exceptions.GoogleAPICallError("Simulated query failure")
    with pytest.raises(google_exceptions.GoogleAPICallError):
        result = db.database_query_one(mock_collection, filters)

def test_database_queryOne_no_result():
    """Test the database_query_one function with failure scenario."""
    filters = [('field1', '==', 'value1')]
    mock_collection = MagicMock()
    mock_query = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_collection.where.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.get.return_value = [mock_doc]
    result = db.database_query_one(mock_collection, filters)
    assert result == None, "Expected database_query_one to return a dict"


def test_database_increment_failure():
    """Test the database_increment function with failure scenario."""
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_ref.update.side_effect = google_exceptions.GoogleAPICallError("Simulated increment failure")
    mock_collection.document.return_value = mock_doc_ref
    with pytest.raises(google_exceptions.GoogleAPICallError):
        db.database_increment(mock_collection, 'some_doc_id', 'field', 1)

@patch("app.database.database_query")
def test_database_get_user_by_username_without_fields(mock_databaes_query):
    """Test the get_user_by_username function."""
    username = 'johndoe'
    mock_user = {'Username': username, 'Rating': 1600}
    mock_databaes_query.return_value = [mock_user]
    # TODO: finish implementation
    result = db.get_user_by_username(username)
    assert result == mock_user, "Expected get_user_by_username to return the user data"
    mock_databaes_query.assert_called_once_with(db.USERS, [("Username", "==", username)]), "Expected database_query to be called with the correct parameters"

@patch("app.database.database_query")
def test_database_get_user_by_username_failure_with_fields(mock_databaes_query):
    """Test the get_user_by_username function with failure scenario."""
    fields = ['Username', 'Rating']
    username = 'johndoe'
    mock_user = {'Username': username, 'Rating': 1600}
    mock_databaes_query.return_value = [mock_user]
    result = db.get_user_by_username(username, fields=fields)
    assert result == mock_user, "Expected get_user_by_username to return the user data"
    mock_databaes_query.assert_called_once_with(db.USERS, [("Username", "==", username)], fields), "Expected database_query to be called with the correct parameters"

@patch("app.database.database_query")
def test_database_get_user_by_username_no_results(mock_databaes_query):
    """Test the get_user_by_username function when no results are found."""
    username = 'johndoe'
    mock_databaes_query.return_value = []
    result = db.get_user_by_username(username)
    assert result == None, "Expected get_user_by_username to return the user data"
    mock_databaes_query.assert_called_once_with(db.USERS, [("Username", "==", username)]), "Expected database_query to be called with the correct parameters"


def test_database_update_user_rating():
    """Test the update_user_rating function."""
    user_id = 'user123'
    new_rating = 1800
    with patch('app.database.database_update', return_value=True) as mock_update:
        result = db.update_user_rating(user_id, new_rating)
        assert result is True, "Expected update_user_rating to return True on success"
        mock_update.assert_called_once_with(db.USERS, user_id, {"Rating": new_rating})

def test_database_update_user_rating_failure():
    """Test the update_user_rating function with failure scenario."""
    user_id = 'user123'
    new_rating = 1800
    with patch('app.database.database_update', return_value=False) as mock_update:
        result = db.update_user_rating(user_id, new_rating)
        assert result is False, "Expected update_user_rating to return True on success"
        mock_update.assert_called_once_with(db.USERS, user_id, {"Rating": new_rating})

@patch("app.database.database_increment")
@patch("app.database.update_user_rating")
@patch("app.database.get_user_by_username")
def test_database_update_player_rankings(mock_get_user, mock_update_user_rating, mock_database_incremenet ):
    """Test the update_player_rankings function."""
    mock_user_1 = MagicMock()
    mock_user_2 = MagicMock()
    mock_user_1.data = {"id": "id_1", "username": "testUser1" }
    mock_user_2.data = {"id": "id_2", "username": "testUser2" }
    mock_update_user_rating.return_value = True
    mock_get_user.side_effect = (lambda x: x.data)   
    result = db.update_player_rankings(mock_user_1, mock_user_2, 600, 600)
    assert result == True



@patch("app.database.database_increment")
@patch("app.database.update_user_rating")
@patch("app.database.get_user_by_username")
def test_database_update_player_rankings_failure(mock_get_user, mock_update_user_rating, mock_database_incremenet ):
    """Test the update_player_rankings function with failure scenario."""
    mock_user_1 = MagicMock()
    mock_user_2 = MagicMock()
    mock_user_1.data = {"id": "id_1", "username": "testUser1" }
    mock_user_2.data = {"id": "id_2", "username": "testUser2" }
    mock_update_user_rating.return_value = False
    mock_get_user.side_effect = (lambda x: x.data)   
    result = db.update_player_rankings(mock_user_1, mock_user_2, 600, 600)
    assert result == False

@patch("app.database.database_increment")
@patch("app.database.update_user_rating")
@patch("app.database.get_user_by_username")
def test_database_update_player_rankings_error(mock_get_user, mock_update_user_rating, mock_database_incremenet ):
    """Test the update_player_rankings function when no results are found."""
    mock_user_1 = MagicMock()
    mock_user_2 = MagicMock()
    mock_user_1.data = {"id": "id_1", "username": "testUser1" }
    mock_user_2.data = {"id": "id_2", "username": "testUser2" }
    mock_update_user_rating.return_value = True
    mock_database_incremenet.side_effect = Exception("Simulated update failure")
    mock_get_user.side_effect = (lambda x: x.data)   
    result = db.update_player_rankings(mock_user_1, mock_user_2, 600, 600)
    assert result == False

