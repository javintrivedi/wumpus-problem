import pytest
import json
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_tictactoe_move_reset_set_options(client):
    # Reset game
    rv = client.post('/reset')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'reset'
    assert data['player_score'] == 0
    assert data['ai_score'] == 0

    # Set options
    rv = client.post('/set_options', json={'player_symbol': 'X', 'difficulty': 'easy'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'options_set'

    # Make a move
    rv = client.post('/move', json={'move': [0, 0]})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'status' in data
    assert 'board' in data
    assert 'player_score' in data
    assert 'ai_score' in data

def test_wumpus_start_move_shoot(client):
    # Start game
    rv = client.post('/wumpus/start')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'started'
    assert 'game' in data

    # Move player
    rv = client.post('/wumpus/move', json={'direction': 'up'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'moved'
    assert 'game' in data

    # Shoot arrow
    rv = client.post('/wumpus/shoot', json={'direction': 'up'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'shot'
    assert 'hit' in data
    assert 'game' in data
