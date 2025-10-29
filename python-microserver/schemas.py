"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, Dict, List
from datetime import datetime, date, time


class GenericResponse(BaseModel):
    """Generic response wrapper"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error: str


class ItemResponse(BaseModel):
    """Generic item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[Any] = None


class ListResponse(BaseModel):
    """Generic list response"""
    success: bool
    message: str
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int