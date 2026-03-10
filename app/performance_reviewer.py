# filepath: /Users/divyanshuraj/Downloads/Synergy/app/performance_reviewer.py
"""
Performance Reviewer Module

This module manages all performance review data in MongoDB (NoSQL database).
Provides functions to submit, retrieve, and analyze performance reviews.

NoSQL is ideal for performance reviews because:
- Review structures may vary (different roles have different criteria)
- Flexible schema allows adding new fields without migrations
- Reviews contain nested data (arrays of strengths, areas for improvement)
- Good for document-centric data that doesn't require complex joins
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import ConnectionFailure

from .db_connections import get_mongo_client, get_reviews_collection, close_mongo_client


class ReviewNotFoundError(Exception):
    """Custom exception raised when a review is not found."""
    pass


class MongoDBConnectionError(Exception):
    """Custom exception raised when MongoDB connection fails."""
    pass


def submit_performance_review(employee_id, reviewer_name, overall_rating, 
                              strengths=None, areas_for_improvement=None,
                              comments=None, goals_for_next_period=None,
                              review_date=None, additional_fields=None):
    """
    Submit a new performance review to MongoDB.
    
    The flexibility of NoSQL allows this function to accept additional fields
    without changing the schema - useful for role-specific review criteria.
    
    Args:
        employee_id (int): The employee being reviewed.
        reviewer_name (str): Name of the person conducting the review.
        overall_rating (float): Rating score (typically 1-5).
        strengths (list, optional): List of employee strengths.
        areas_for_improvement (list, optional): List of areas needing improvement.
        comments (str, optional): Additional comments about the employee.
        goals_for_next_period (list, optional): List of goals for the next review period.
        review_date (str, optional): Date of review (YYYY-MM-DD). Defaults to today.
        additional_fields (dict, optional): Any additional fields to include in the review.
    
    Returns:
        str: The ID of the inserted review document.
    
    Raises:
        ValueError: If required fields are invalid.
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    # Validate required fields
    if not employee_id:
        raise ValueError("employee_id is required.")
    if not reviewer_name:
        raise ValueError("reviewer_name is required.")
    if overall_rating is None:
        raise ValueError("overall_rating is required.")
    
    # Validate rating range
    try:
        rating = float(overall_rating)
        if rating < 1 or rating > 5:
            raise ValueError("overall_rating must be between 1 and 5.")
    except (TypeError, ValueError) as e:
        if "must be between" in str(e):
            raise
        raise ValueError("overall_rating must be a number.")
    
    # Set default review date
    if review_date is None:
        review_date = datetime.now().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(review_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("review_date must be in YYYY-MM-DD format.")
    
    # Build the review document
    review_document = {
        'employee_id': int(employee_id),
        'reviewer_name': reviewer_name.strip(),
        'overall_rating': rating,
        'review_date': review_date,
        'created_at': datetime.now(),
        'strengths': strengths if strengths else [],
        'areas_for_improvement': areas_for_improvement if areas_for_improvement else [],
        'comments': comments.strip() if comments else '',
        'goals_for_next_period': goals_for_next_period if goals_for_next_period else []
    }
    
    # Add any additional fields (NoSQL flexibility)
    if additional_fields and isinstance(additional_fields, dict):
        review_document.update(additional_fields)
    
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        result = reviews.insert_one(review_document)
        review_id = str(result.inserted_id)
        
        print(f"Performance review submitted successfully with ID: {review_id}")
        close_mongo_client(client)
        
        return review_id
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_performance_reviews_for_employee(employee_id):
    """
    Retrieve all performance reviews for a specific employee.
    
    Args:
        employee_id (int): The employee's unique identifier.
    
    Returns:
        list: A list of review documents for the employee.
    
    Raises:
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        # Query for all reviews matching the employee_id
        cursor = reviews.find(
            {'employee_id': int(employee_id)}
        ).sort('review_date', -1)  # Sort by date, newest first
        
        # Convert cursor to list and ObjectId to string
        review_list = []
        for review in cursor:
            review['_id'] = str(review['_id'])
            if 'created_at' in review:
                review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            review_list.append(review)
        
        close_mongo_client(client)
        return review_list
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_review_by_id(review_id):
    """
    Retrieve a specific performance review by its ID.
    
    Args:
        review_id (str): The review's unique identifier.
    
    Returns:
        dict: The review document.
    
    Raises:
        ReviewNotFoundError: If no review with the given ID exists.
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        review = reviews.find_one({'_id': ObjectId(review_id)})
        
        if review is None:
            close_mongo_client(client)
            raise ReviewNotFoundError(f"Review with ID {review_id} not found.")
        
        review['_id'] = str(review['_id'])
        if 'created_at' in review:
            review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        close_mongo_client(client)
        return review
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def update_review(review_id, **kwargs):
    """
    Update an existing performance review.
    
    Args:
        review_id (str): The review's unique identifier.
        **kwargs: Fields to update (e.g., overall_rating=4.5, comments="Updated").
    
    Returns:
        bool: True if update was successful.
    
    Raises:
        ReviewNotFoundError: If no review with the given ID exists.
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    if not kwargs:
        return True  # Nothing to update
    
    # Validate rating if provided
    if 'overall_rating' in kwargs:
        try:
            rating = float(kwargs['overall_rating'])
            if rating < 1 or rating > 5:
                raise ValueError("overall_rating must be between 1 and 5.")
            kwargs['overall_rating'] = rating
        except (TypeError, ValueError) as e:
            if "must be between" in str(e):
                raise
            raise ValueError("overall_rating must be a number.")
    
    # Add updated timestamp
    kwargs['updated_at'] = datetime.now()
    
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        result = reviews.update_one(
            {'_id': ObjectId(review_id)},
            {'$set': kwargs}
        )
        
        if result.matched_count == 0:
            close_mongo_client(client)
            raise ReviewNotFoundError(f"Review with ID {review_id} not found.")
        
        print(f"Review {review_id} updated successfully.")
        close_mongo_client(client)
        return True
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def delete_review(review_id):
    """
    Delete a performance review.
    
    Args:
        review_id (str): The review's unique identifier.
    
    Returns:
        bool: True if deletion was successful.
    
    Raises:
        ReviewNotFoundError: If no review with the given ID exists.
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        result = reviews.delete_one({'_id': ObjectId(review_id)})
        
        if result.deleted_count == 0:
            close_mongo_client(client)
            raise ReviewNotFoundError(f"Review with ID {review_id} not found.")
        
        print(f"Review {review_id} deleted successfully.")
        close_mongo_client(client)
        return True
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_average_rating_for_employee(employee_id):
    """
    Calculate the average rating for an employee across all reviews.
    
    Args:
        employee_id (int): The employee's unique identifier.
    
    Returns:
        dict: Contains average_rating, review_count, and rating breakdown.
    
    Raises:
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        # Use aggregation pipeline for efficient calculation
        pipeline = [
            {'$match': {'employee_id': int(employee_id)}},
            {'$group': {
                '_id': '$employee_id',
                'average_rating': {'$avg': '$overall_rating'},
                'review_count': {'$sum': 1},
                'min_rating': {'$min': '$overall_rating'},
                'max_rating': {'$max': '$overall_rating'}
            }}
        ]
        
        result = list(reviews.aggregate(pipeline))
        
        close_mongo_client(client)
        
        if not result:
            return {
                'employee_id': employee_id,
                'average_rating': None,
                'review_count': 0,
                'min_rating': None,
                'max_rating': None
            }
        
        return {
            'employee_id': employee_id,
            'average_rating': round(result[0]['average_rating'], 2),
            'review_count': result[0]['review_count'],
            'min_rating': result[0]['min_rating'],
            'max_rating': result[0]['max_rating']
        }
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_all_strengths_for_employee(employee_id):
    """
    Aggregate all strengths mentioned across an employee's reviews.
    
    Args:
        employee_id (int): The employee's unique identifier.
    
    Returns:
        list: A list of all strengths mentioned in reviews.
    
    Raises:
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        pipeline = [
            {'$match': {'employee_id': int(employee_id)}},
            {'$unwind': '$strengths'},
            {'$group': {
                '_id': '$strengths',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        result = list(reviews.aggregate(pipeline))
        
        close_mongo_client(client)
        
        return [{'strength': item['_id'], 'count': item['count']} for item in result]
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_all_areas_for_improvement_for_employee(employee_id):
    """
    Aggregate all areas for improvement mentioned across an employee's reviews.
    
    Args:
        employee_id (int): The employee's unique identifier.
    
    Returns:
        list: A list of all areas for improvement mentioned in reviews.
    
    Raises:
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        pipeline = [
            {'$match': {'employee_id': int(employee_id)}},
            {'$unwind': '$areas_for_improvement'},
            {'$group': {
                '_id': '$areas_for_improvement',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        result = list(reviews.aggregate(pipeline))
        
        close_mongo_client(client)
        
        return [{'area': item['_id'], 'count': item['count']} for item in result]
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")


def get_reviews_by_date_range(employee_id=None, start_date=None, end_date=None):
    """
    Retrieve performance reviews within a date range.
    
    Args:
        employee_id (int, optional): Filter by specific employee.
        start_date (str, optional): Start of date range (YYYY-MM-DD).
        end_date (str, optional): End of date range (YYYY-MM-DD).
    
    Returns:
        list: A list of review documents matching the criteria.
    
    Raises:
        MongoDBConnectionError: If unable to connect to MongoDB.
    """
    query = {}
    
    if employee_id:
        query['employee_id'] = int(employee_id)
    
    if start_date or end_date:
        query['review_date'] = {}
        if start_date:
            query['review_date']['$gte'] = start_date
        if end_date:
            query['review_date']['$lte'] = end_date
    
    try:
        client = get_mongo_client()
        reviews = get_reviews_collection(client)
        
        cursor = reviews.find(query).sort('review_date', -1)
        
        review_list = []
        for review in cursor:
            review['_id'] = str(review['_id'])
            if 'created_at' in review:
                review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            review_list.append(review)
        
        close_mongo_client(client)
        return review_list
        
    except ConnectionFailure as e:
        raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")
