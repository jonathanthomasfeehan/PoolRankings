import os

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore
import google.cloud.firestore_v1 as firestore_v1
from google.cloud.firestore_v1 import Increment
from google.auth import credentials as google_credentials


# firebase_credentials = credentials.Certificate(os.getenv('FIREBASE_SECRET_KEY'))
# firebase_admin.initialize_app(firebase_credentials)
# database = firestore.client()


# Updated to handle both emulator and production environments
def initialize_database():
        # Running with Firestore Emulator
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        print("Using Firestore Emulator")
        return firestore_v1.Client(
            project=os.getenv("FIRESTORE_PROJECT_ID", "test-project"),
            credentials=google_credentials.AnonymousCredentials()
        )
    else:
        # Running in production
        cred_path = os.getenv("FIREBASE_SECRET_KEY")
        if not cred_path:
            raise RuntimeError("FIREBASE_SECRET_KEY must be set in production")
        return firestore_v1.Client.from_service_account_json(cred_path)
    
database = initialize_database()
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
        return db_create_result, doc_ref
    # TODO: Handle specific exceptions
    except Exception as e:
        print(f"Error creating document in collection {collection.id}: {e}")
        print(f"Data: {data}")
        print(f"Document ID: {doc_ref.id}")
        return None, None  # Return None if creation fails

def database_update(collection, doc_id, data):
    """
    Updates a document in the specified Firestore collection.
    """
    try:
        result = collection.document(doc_id).set(data, merge=True)
        print(f"Updated document {doc_id} in collection {collection.id} with data: {data}")
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
        docs_returned = False
        docs = list(docs)  # Convert to list to evaluate the query
        for doc in docs:
            docs_returned = True
            result = database_update(collection, doc.id, data)
            print(f'Result of updating document {doc.id} in collection {collection.id}: {result}')
            # FIXME: investigate rolling back if one update fails
            if result == False:
                print(f"Failed to update document {doc.id} in collection {collection.id}")
                return False
        if not docs_returned:
            return False
    except Exception as e:
        print(f"Error updating documents: {e}")
        return False

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
        raise

def database_delete(collection, doc_id) -> None:
    """
    Deletes a document from the specified Firestore collection.
    """
    try:
        collection.document(doc_id).delete()
    except Exception as e:
        print(f"Error deleting document {doc_id} from collection {collection.id}: {e}")
        raise

def database_query(collection, filters, fields=None) -> list:
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
        # TODO: handle with integration tests
        if fields:
            print(f"Selecting fields: {fields}")
            query = query.select(fields)
        result = query.stream()
        final_list = [doc.to_dict() for doc in result]
        if len(final_list) == 0:
            print(f"No documents found in collection {collection.id} with filters: {filters}")
            return []
        else:
            print(f"Found {len(final_list)} documents in collection {collection.id} with filters: {filters}")
            return final_list
    except Exception as e:
        print(f"Error querying documents in collection {collection.id}: {e}")
        # TODO: Include custom exceptions
        raise e
    
def database_query_one(collection, filters) -> dict:
    """
    Queries documents in the specified Firestore collection based on filters.
    Filters should be a list of tuples: [(field, operator, value), ...].
    """
    # TODO: include logic that ensures filters are on Primary Key
    try:
        query = collection
        for field, operator, value in filters:
            query = query.where(filter=firestore_v1.FieldFilter(field, operator, value))
        # result = query.stream()
        result = query.get()
        if (result)[0].exists:
            return (result)[0].to_dict()
        return None
        # return next(result).to_dict()
    except Exception as e:
        print(f"Error querying one document in collection {collection.id}: {e}")
        raise
    
def database_increment(collection, doc_id, field, increment_value):
    """
    Increments a field in a document by a specified value.
    """
    try:
        collection.document(doc_id).update({field: Increment(increment_value)})
    except Exception as e:
        print(f"Error incrementing field {field} in document {doc_id} in collection {collection.id}: {e}")
        raise

def get_user_by_username(username, fields = None) ->dict:
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

# TODO: Delete this is not used anywhere
def get_pending_matches(username):
    """
    Retrieves all pending matches for a given user.
    """
    return database_query(PENDING_MATCHES, [
        ("player1", "==", username),
        ("status", "!=", "4")
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
    try:
        database_increment(USERS, player1_docid, "Matches", 1)
        database_increment(USERS, player2_docid, "Matches", 1)
        return True
    except Exception as e:
        print(f'Caught {e} in Update_Player_rankings')
        return False

# Elo scaling constants
# TODO: move to logic
STARTING_RATING = 500
K = 32
D = 400