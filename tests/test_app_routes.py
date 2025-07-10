class routes_class:

    def index_page(client):
        """Test the index page of the application."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Rack It Up' in response.data

    def propose_match_page(client):
        """Test the propose match page of the application."""
        response = client.get('/ProposeMatch')
        assert response.status_code == 200
        assert b'Propose Match' in response.data

    def show_rankings(client):
        """Test the show rankings page of the application."""
        # Look into mocking the database if needed
        response = client.get('/showRankings')
        assert response.status_code == 200
        assert b'Propose Match' in response.data

    # def get_rankings(client):
    #     """Test the show rankings page of the application."""
    #     # Look into mocking the database if needed
    #     response = client
    #     assert response.status_code == 200
    #     assert b'Propose Match' in response.data