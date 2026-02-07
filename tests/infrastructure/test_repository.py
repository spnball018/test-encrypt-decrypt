import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from infrastructure.repository import Repository

@pytest.fixture
def mock_db_conn():
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_connect, mock_conn, mock_cursor

def test_save_user_profile_success(mock_db_conn):
    mock_connect, mock_conn, mock_cursor = mock_db_conn
    
    repo = Repository()
    repo.save_user_profile("encrypted_blob", "hashed_index")
    
    # Verify execute called twice (CREATE TABLE, INSERT)
    assert mock_cursor.execute.call_count == 2
    # Verify commit called
    mock_conn.commit.assert_called_once()
    # Verify close called
    mock_conn.close.assert_called_once()

def test_save_user_profile_duplicate(mock_db_conn):
    mock_connect, mock_conn, mock_cursor = mock_db_conn
    
    # Simulate UniqueViolation on INSERT (2nd call)
    mock_cursor.execute.side_effect = [None, psycopg2.errors.UniqueViolation("Duplicate")]
    
    repo = Repository()
    
    with pytest.raises(ValueError, match="National ID already exists"):
        repo.save_user_profile("blob", "index")
        
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_find_by_hash_success(mock_db_conn):
    mock_connect, mock_conn, mock_cursor = mock_db_conn
    
    # Setup return value
    mock_cursor.fetchall.return_value = [(1, "blob_data")]
    
    repo = Repository()
    result = repo.find_by_hash("some_hash")
    
    assert len(result) == 1
    assert result[0] == (1, "blob_data")
    mock_conn.close.assert_called_once()
