import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpTest import cleanup_database

@pytest.fixture(autouse=True, scope="function")
def auto_cleanup():
    print("Очистка БД перед тестом")
    cleanup_database()
    yield
    print("Очистка БД после теста")
    cleanup_database()