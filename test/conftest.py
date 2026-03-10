"""
Pytest configuration and fixtures for testing.

This module provides fixtures for creating temporary test databases
to avoid interfering with development data.
"""

import pytest
import os
import tempfile
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db_path():
    """
    Create a temporary SQLite database file for testing.
    
    Yields:
        str: Path to the temporary database file.
    """
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield path
    
    # Cleanup after test
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def initialized_db(temp_db_path):
    """
    Create and initialize a temporary database with tables.
    
    Args:
        temp_db_path: Temporary database path fixture.
    
    Yields:
        str: Path to the initialized database.
    """
    from app.db_connections import initialize_sql_database
    
    initialize_sql_database(temp_db_path)
    
    yield temp_db_path


@pytest.fixture
def sample_employee_data():
    """
    Provide sample employee data for testing.
    
    Returns:
        dict: Sample employee information.
    """
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'hire_date': '2024-01-15',
        'department': 'Engineering'
    }


@pytest.fixture
def sample_project_data():
    """
    Provide sample project data for testing.
    
    Returns:
        dict: Sample project information.
    """
    return {
        'project_name': 'Alpha Project',
        'start_date': '2024-02-01',
        'end_date': '2024-12-31',
        'status': 'In Progress'
    }


@pytest.fixture
def populated_db(initialized_db, sample_employee_data, sample_project_data):
    """
    Create a database populated with sample data.
    
    Args:
        initialized_db: Initialized database fixture.
        sample_employee_data: Sample employee data fixture.
        sample_project_data: Sample project data fixture.
    
    Yields:
        dict: Contains db_path, employee_id, and project_id.
    """
    from app.employee_manager import add_employee
    from app.project_manager import add_project
    
    # Add sample employee
    employee_id = add_employee(
        first_name=sample_employee_data['first_name'],
        last_name=sample_employee_data['last_name'],
        email=sample_employee_data['email'],
        hire_date=sample_employee_data['hire_date'],
        department=sample_employee_data['department'],
        db_path=initialized_db
    )
    
    # Add sample project
    project_id = add_project(
        project_name=sample_project_data['project_name'],
        start_date=sample_project_data['start_date'],
        end_date=sample_project_data['end_date'],
        status=sample_project_data['status'],
        db_path=initialized_db
    )
    
    yield {
        'db_path': initialized_db,
        'employee_id': employee_id,
        'project_id': project_id
    }


@pytest.fixture
def mock_mongo_collection(monkeypatch):
    """
    Mock MongoDB collection for testing without actual MongoDB connection.
    
    This fixture creates a mock that simulates MongoDB operations.
    """
    from unittest.mock import MagicMock, patch
    from bson import ObjectId
    
    # Storage for mock documents
    mock_storage = []
    
    class MockCollection:
        def __init__(self):
            self._storage = mock_storage
        
        def insert_one(self, document):
            doc_id = ObjectId()
            document['_id'] = doc_id
            self._storage.append(document.copy())
            
            result = MagicMock()
            result.inserted_id = doc_id
            return result
        
        def find(self, query=None):
            if query is None:
                return iter(self._storage)
            
            results = []
            for doc in self._storage:
                match = True
                for key, value in query.items():
                    if key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    results.append(doc.copy())
            
            mock_cursor = MagicMock()
            mock_cursor.sort = MagicMock(return_value=iter(results))
            mock_cursor.__iter__ = lambda s: iter(results)
            return mock_cursor
        
        def find_one(self, query):
            for doc in self._storage:
                match = True
                for key, value in query.items():
                    if key == '_id':
                        if doc.get('_id') != value:
                            match = False
                            break
                    elif key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    return doc.copy()
            return None
        
        def update_one(self, query, update):
            result = MagicMock()
            result.matched_count = 0
            
            for i, doc in enumerate(self._storage):
                match = True
                for key, value in query.items():
                    if key == '_id':
                        if doc.get('_id') != value:
                            match = False
                            break
                    elif key not in doc or doc[key] != value:
                        match = False
                        break
                
                if match:
                    if '$set' in update:
                        self._storage[i].update(update['$set'])
                    result.matched_count = 1
                    break
            
            return result
        
        def delete_one(self, query):
            result = MagicMock()
            result.deleted_count = 0
            
            for i, doc in enumerate(self._storage):
                match = True
                for key, value in query.items():
                    if key == '_id':
                        if doc.get('_id') != value:
                            match = False
                            break
                    elif key not in doc or doc[key] != value:
                        match = False
                        break
                
                if match:
                    del self._storage[i]
                    result.deleted_count = 1
                    break
            
            return result
        
        def aggregate(self, pipeline):
            # Enhanced mock aggregation to handle more pipeline stages
            results = list(self._storage)
            unwound_field = None
            
            for stage in pipeline:
                if '$match' in stage:
                    query = stage['$match']
                    filtered = []
                    for doc in results:
                        match = True
                        for key, value in query.items():
                            if key not in doc or doc[key] != value:
                                match = False
                                break
                        if match:
                            filtered.append(doc)
                    results = filtered
                
                elif '$unwind' in stage:
                    # Handle $unwind stage for arrays
                    unwind_field = stage['$unwind'].replace('$', '')
                    unwound_field = unwind_field
                    unwound_results = []
                    for doc in results:
                        field_value = doc.get(unwind_field, [])
                        if isinstance(field_value, list):
                            for item in field_value:
                                new_doc = doc.copy()
                                new_doc[unwind_field] = item
                                unwound_results.append(new_doc)
                    results = unwound_results
                
                elif '$group' in stage:
                    group_spec = stage['$group']
                    group_key = group_spec['_id']
                    
                    # Check if this is a count aggregation on unwound field
                    if isinstance(group_key, str) and group_key.startswith('$') and unwound_field:
                        # Group by unwound field and count
                        field_name = group_key.replace('$', '')
                        groups = {}
                        for doc in results:
                            key_value = doc.get(field_name)
                            if key_value not in groups:
                                groups[key_value] = 0
                            groups[key_value] += 1
                        
                        results = [{'_id': k, 'count': v} for k, v in groups.items()]
                    else:
                        # Simple aggregation for average rating
                        if results:
                            total_rating = sum(doc.get('overall_rating', 0) for doc in results)
                            count = len(results)
                            min_rating = min(doc.get('overall_rating', 0) for doc in results)
                            max_rating = max(doc.get('overall_rating', 0) for doc in results)
                            
                            results = [{
                                '_id': group_key,
                                'average_rating': total_rating / count if count > 0 else 0,
                                'review_count': count,
                                'min_rating': min_rating,
                                'max_rating': max_rating
                            }]
                
                elif '$sort' in stage:
                    # Handle sort stage
                    sort_spec = stage['$sort']
                    for field, direction in sort_spec.items():
                        results = sorted(results, key=lambda x: x.get(field, 0), reverse=(direction == -1))
            
            return results
        
        def create_index(self, field):
            pass
    
    mock_collection = MockCollection()
    mock_client = MagicMock()
    
    # Patch the MongoDB connection functions
    with patch('app.performance_reviewer.get_mongo_client', return_value=mock_client):
        with patch('app.performance_reviewer.get_reviews_collection', return_value=mock_collection):
            with patch('app.performance_reviewer.close_mongo_client'):
                yield mock_collection
