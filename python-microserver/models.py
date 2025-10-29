"""
SQLAlchemy models auto-generated from database schema
Models are created using reflection from existing database tables
"""
from sqlalchemy import MetaData, inspect, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from database import engine

# Base for models
Base = declarative_base()

# Metadata for reflection
metadata = MetaData()

def reflect_models():
    """
    Reflect all tables from the database and create model classes
    """
    from sqlalchemy.ext.automap import automap_base
    
    AutoBase = automap_base()
    AutoBase.prepare(engine, reflect=True)
    
    return AutoBase.registry.mappers


def get_all_tables():
    """
    Get list of all tables in the database
    """
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_model_class(table_name: str):
    """
    Dynamically get a model class for a specific table
    Uses SQLAlchemy's automap feature
    """
    from sqlalchemy.ext.automap import automap_base
    
    AutoBase = automap_base()
    AutoBase.prepare(engine, reflect=True)
    
    # Get the model class if it exists
    return getattr(AutoBase.classes, table_name, None)


# Initialize auto-mapped models
try:
    from sqlalchemy.ext.automap import automap_base
    
    AutoBase = automap_base()
    AutoBase.prepare(engine, reflect=True)
    
    # Create module-level references to all reflected models
    for table_name in get_all_tables():
        model_class = getattr(AutoBase.classes, table_name, None)
        if model_class:
            globals()[table_name] = model_class
            
except Exception as e:
    print(f"Warning: Could not reflect models: {e}")
    print("Models will be loaded dynamically at runtime")