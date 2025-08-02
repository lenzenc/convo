#!/usr/bin/env python3
"""
Pytest configuration and fixtures for the conversation analytics tests.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_view_data():
    """Sample view data for testing."""
    return {
        "name": "test_view",
        "description": "Test view for unit tests",
        "sql_query": "SELECT 1 as test_column",
        "tags": ["test"],
        "created": "2025-01-01T00:00:00",
        "updated": "2025-01-01T00:00:00"
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return [
        {
            "entry_id": "test_session_1",
            "session_id": "test_session",
            "interaction_id": 1,
            "question": "Test question",
            "answer": "Test answer",
            "action": "test",
            "user_id": "test_user"
        }
    ]