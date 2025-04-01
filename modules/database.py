import os
import datetime
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.cloud.firestore_v1 as firestore_v1
from google.cloud.firestore_v1 import Increment


firebase_credentials = credentials.Certificate(os.getenv('FIREBASE_SECRET_KEY'))
firebase_admin.initialize_app(firebase_credentials)
database = firestore.client()

USERS = database.collection('USERS')
MATCHES = database.collection('MATCHES')
PENDING_MATCHES = database.collection('PENDING_MATCHES')

def database_create(collection, data):
    """
    Creates a new document in the specified Firestore collection.
    """
    try:
        # TODO: Verify data contains all required fields
        print(f"Creating document in collection {collection.id} with data: {data}")
        doc_ref = database.collection(collection.id).document()  # Auto-generate ID
        data['id'] = doc_ref.id  # Store the document ID inside the data
        db_create_result = doc_ref.set(data)
        return db_create_result
    except Exception as e:
        print(f"Error creating document in collection {collection.id}: {e}")
        print(f"Data: {data}")
        print(f"Document ID: {doc_ref.id}")

def database_update(collection, doc_id, data):
    """
    Updates a document in the specified Firestore collection.
    """
    try:
        print(f"Updating document {doc_id} in collection {collection.id} with data: {str(data)}")
        result = collection.document(doc_id).set(data, merge=True)
        return True
    except Exception as e:
        print(f"Error updating document {doc_id} in collection {collection.id}: {e}")
        return False

def database_update_with_query(collection, filters, data):
    """
    Queries for documents using filters and updates them.
    """
    try:
        query = collection
        for field, operator, value in filters:
            query = query.where(filter = firestore_v1.FieldFilter(field, operator, value))
        
        docs = query.stream()
        for doc in docs:
            database_update(collection, doc.id, data)
    except Exception as e:
        print(f"Error updating documents: {e}")

def database_get(collection, doc_id):
    """
    Retrieves a document from the specified Firestore collection.
    """
    try:
        doc = collection.document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"Document {doc_id} does not exist in collection {collection.id}.")
            return None
    except Exception as e:
        print(f"Error retrieving document {doc_id} from collection {collection.id}: {e}")
        return None

def database_delete(collection, doc_id):
    """
    Deletes a document from the specified Firestore collection.
    """
    try:
        collection.document(doc_id).delete()
    except Exception as e:
        print(f"Error deleting document {doc_id} from collection {collection.id}: {e}")

def database_query(collection, filters, fields=None):
    """
    Queries documents in the specified Firestore collection based on filters.
    Filters should be a list of tuples: [(field, operator, value), ...].
    """
    # TODO: differentiate between fields arg and field in filters loop
    try:
        print(f"Querying collection {collection.id}")
        query = collection
        for field, operator, value in filters:
            print(f"Querying field: {field}, operator: {operator}, value: {value}")
            query = query.where(filter = firestore_v1.FieldFilter(field, operator, value))
        # If fields is provided, select only those fields
        # Otherwise, select all fields by default
        if fields:
            print(f"Selecting fields: {fields}")
            query = query.select(fields)
        result = query.stream()
        if not result:
            print(f"No documents found in collection {collection.id} with filters: {filters}")
            return []
        return [doc.to_dict() for doc in result]
    except Exception as e:
        print(f"Error querying documents in collection {collection.id}: {e}")
        return []
    
def database_query_one(collection, filters):
    """
    Queries documents in the specified Firestore collection based on filters.
    Filters should be a list of tuples: [(field, operator, value), ...].
    """
    try:
        query = collection
        for field, operator, value in filters:
            query = query.where(filter=firestore_v1.FieldFilter(field, operator, value))
        result = query.stream()
        if not result:
            print(f"No documents found in collection {collection.id} with filters: {filters}")
            return None
        return next(result).to_dict()
    except Exception as e:
        print(f"Error querying one document in collection {collection.id}: {e}")
        return None
    
def database_increment(collection, doc_id, field, increment_value):
    """
    Increments a field in a document by a specified value.
    """
    try:
        collection.document(doc_id).update({field: Increment(increment_value)})
    except Exception as e:
        print(f"Error incrementing field {field} in document {doc_id} in collection {collection.id}: {e}")

def get_user_by_username(username, fields = None):
    """
    Retrieves a user document by username.
    """

    if fields:
        results = database_query(USERS, [("Username", "==", username)], fields)
    else:
        results = database_query(USERS, [("Username", "==", username)])
    if results:
        return results[0]
    else:
        print(f"No user found with username: {username}")
        return None

def update_user_rating(user_id, new_rating):
    """
    Updates the rating of a user.
    """
    if database_update(USERS, user_id, {"Rating": new_rating}):
        return True
    else:
        print(f"Failed to update rating for user {user_id}")
        return False

def get_pending_matches(username):
    """
    Retrieves all pending matches for a given user.
    """
    return database_query(PENDING_MATCHES, [
        ("player1", "==", username),
        ("status", "==", "pending")
    ])

def update_player_rankings(player1_username, player2_username, player1_new_rating, player2_new_rating):
    """
    Updates the rankings of two players after a match.
    """
    # Should this be passed in as a list of tuples instead?

    # Get the document IDs for the players
    player1_docid = get_user_by_username(player1_username)['id']
    player2_docid = get_user_by_username(player2_username)['id']
    # Update the ratings in the database
    # TODO: Look into doing both of these as a transaction
    if not update_user_rating(player1_docid, player1_new_rating):
        return False
    if not update_user_rating(player2_docid, player2_new_rating):
        return False
    database_increment(USERS, player1_docid, "Matches", 1)
    database_increment(USERS, player2_docid, "Matches", 1)
    return True

# Elo scaling constants
STARTING_RATING = 500
K = 32
D = 400