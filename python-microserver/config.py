"""
Database configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database credentials
DB_USER = os.getenv("DB_USER", "dba1")
DB_PASSWORD = os.getenv("DB_PASSWORD", "xKAHai1AiEiKktM")
DB_HOST = os.getenv("DB_HOST", "10.1.2.3")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "northwind")

# SQLAlchemy Database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# API Configuration
API_TITLE = "Northwind Microserver API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "RESTful API for Northwind Database"