"""
FastAPI Microserver for Northwind Database
Auto-generated CRUD endpoints for all tables
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import inspect, func, text
from typing import List, Dict, Any, Optional
import logging

from config import API_TITLE, API_VERSION, API_DESCRIPTION, DATABASE_URL
from database import get_db, engine
from models import get_all_tables, get_model_class
from schemas import GenericResponse, ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Store available tables
AVAILABLE_TABLES = []


def serialize_row(row: Any, columns: List[str]) -> Dict[str, Any]:
    """Convert SQLAlchemy row to dictionary"""
    result = {}
    for col in columns:
        value = getattr(row, col, None)
        if value is None:
            result[col] = None
        elif isinstance(value, (bytes, bytearray)):
            result[col] = value.decode('utf-8', errors='ignore')
        else:
            result[col] = value
    return result


def get_table_columns(table_name: str) -> List[str]:
    """Get column names for a table"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [col['name'] for col in columns]


def get_primary_keys(table_name: str) -> List[str]:
    """Get primary key columns for a table"""
    inspector = inspect(engine)
    pk = inspector.get_pk_constraint(table_name)
    return pk.get('constrained_columns', [])


@app.on_event("startup")
async def startup_event():
    """Initialize available tables on startup"""
    global AVAILABLE_TABLES
    try:
        AVAILABLE_TABLES = get_all_tables()
        logger.info(f"✓ Database connected. Available tables: {AVAILABLE_TABLES}")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {e}")
        logger.error(f"Connection string: {DATABASE_URL}")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status"""
    return GenericResponse(
        success=True,
        message="Northwind Microserver API is running",
        data={"version": API_VERSION, "tables": AVAILABLE_TABLES}
    )


@app.get("/api/tables", tags=["Metadata"])
async def list_tables():
    """Get list of all available tables"""
    return GenericResponse(
        success=True,
        message=f"Found {len(AVAILABLE_TABLES)} tables",
        data={"tables": AVAILABLE_TABLES}
    )


@app.get("/api/tables/{table_name}/schema", tags=["Metadata"])
async def get_table_schema(table_name: str):
    """Get schema information for a specific table"""
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        pk = inspector.get_pk_constraint(table_name)
        fk = inspector.get_foreign_keys(table_name)
        
        return GenericResponse(
            success=True,
            message=f"Schema for table '{table_name}'",
            data={
                "table_name": table_name,
                "columns": columns,
                "primary_keys": pk.get('constrained_columns', []),
                "foreign_keys": fk
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dynamic CRUD Endpoints

@app.get("/api/{table_name}", tags=["Read"])
async def read_items(
    table_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all records from a table with pagination
    """
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        model_class = get_model_class(table_name)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Could not load model for table '{table_name}'")
        
#        total = db.query(func.count(model_class)).scalar()
        items = db.query(model_class).offset(skip).limit(limit).all()

        columns = get_table_columns(table_name)
        serialized_items = [serialize_row(item, columns) for item in items]
        
        return GenericResponse(
            success=True,
            message=f"Retrieved {len(items)} records from '{table_name}'",
            data={
                "table": table_name,
                "items": serialized_items,
 #               "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading from table '{table_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{table_name}/{record_id}", tags=["Read"])
async def read_item(
    table_name: str,
    record_id: Any,
    db: Session = Depends(get_db)
):
    """
    Get a single record by ID
    """
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        model_class = get_model_class(table_name)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Could not load model for table '{table_name}'")
        
        pk_columns = get_primary_keys(table_name)
        if not pk_columns:
            raise HTTPException(status_code=400, detail=f"Table '{table_name}' has no primary key")
        
        # Try to get by primary key
        item = db.query(model_class).filter_by(**{pk_columns[0]: record_id}).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Record not found in '{table_name}' with {pk_columns[0]}={record_id}")
        
        columns = get_table_columns(table_name)
        serialized_item = serialize_row(item, columns)
        
        return GenericResponse(
            success=True,
            message=f"Retrieved record from '{table_name}'",
            data=serialized_item
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading record from table '{table_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/{table_name}", tags=["Create"])
async def create_item(
    table_name: str,
    item_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new record in a table
    """
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        model_class = get_model_class(table_name)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Could not load model for table '{table_name}'")
        
        # Create new instance
        new_item = model_class(**item_data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        
        columns = get_table_columns(table_name)
        serialized_item = serialize_row(new_item, columns)
        
        return GenericResponse(
            success=True,
            message=f"Record created in '{table_name}'",
            data=serialized_item
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating record in table '{table_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/{table_name}/{record_id}", tags=["Update"])
async def update_item(
    table_name: str,
    record_id: Any,
    item_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update an existing record
    """
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        model_class = get_model_class(table_name)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Could not load model for table '{table_name}'")
        
        pk_columns = get_primary_keys(table_name)
        if not pk_columns:
            raise HTTPException(status_code=400, detail=f"Table '{table_name}' has no primary key")
        
        # Find the record
        item = db.query(model_class).filter_by(**{pk_columns[0]: record_id}).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Record not found in '{table_name}'")
        
        # Update fields
        for key, value in item_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        db.commit()
        db.refresh(item)
        
        columns = get_table_columns(table_name)
        serialized_item = serialize_row(item, columns)
        
        return GenericResponse(
            success=True,
            message=f"Record updated in '{table_name}'",
            data=serialized_item
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating record in table '{table_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/{table_name}/{record_id}", tags=["Delete"])
async def delete_item(
    table_name: str,
    record_id: Any,
    db: Session = Depends(get_db)
):
    """
    Delete a record
    """
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    try:
        model_class = get_model_class(table_name)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Could not load model for table '{table_name}'")
        
        pk_columns = get_primary_keys(table_name)
        if not pk_columns:
            raise HTTPException(status_code=400, detail=f"Table '{table_name}' has no primary key")
        
        # Find and delete
        item = db.query(model_class).filter_by(**{pk_columns[0]: record_id}).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Record not found in '{table_name}'")
        
        db.delete(item)
        db.commit()
        
        return GenericResponse(
            success=True,
            message=f"Record deleted from '{table_name}'",
            data={"deleted_id": record_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting record from table '{table_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting Northwind Microserver API")
    print("📊 Database: {DATABASE_URL.split('@')[1]}")
    print("📖 Docs: http://10.1.2.18:8000/api/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="10.1.2.18",
        port=8000,
        log_level="info"
    )