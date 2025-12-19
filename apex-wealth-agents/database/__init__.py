"""
Database module for ApexWealth
"""
from .mongodb_service import MongoDBService, get_mongodb_service

__all__ = ["MongoDBService", "get_mongodb_service"]

