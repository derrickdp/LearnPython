# Northwind Microserver API

A FastAPI-based microserver that provides RESTful API endpoints for the Northwind database with auto-generated models and CRUD operations.

## Features

- 🚀 **FastAPI** - High-performance async API framework
- 🗄️ **Auto-Generated Models** - SQLAlchemy models reflected from database schema
- 📊 **Dynamic CRUD** - Automatic endpoints for all tables
- 🔄 **Pagination** - Built-in pagination support
- 📖 **Auto Documentation** - Swagger UI and ReDoc
- 🔌 **MySQL Support** - PyMySQL driver for database connectivity

## Installation

### 1. Install Dependencies

```bash
cd microserver
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

The default configuration connects to:
- **Host**: 10.1.2.3
- **User**: dba1
- **Password**: xKAHai1AiEiKktM
- **Database**: northwind

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Available Endpoints

### Health & Metadata

- `GET /` - API status and available tables
- `GET /api/tables` - List all available tables
- `GET /api/tables/{table_name}/schema` - Get table schema information

### CRUD Operations

All endpoints follow the same pattern:

- `GET /api/{table_name}` - List all records (with pagination)
  - Query parameters: `skip` (default: 0), `limit` (default: 10, max: 100)
  
- `GET /api/{table_name}/{record_id}` - Get single record
  
- `POST /api/{table_name}` - Create new record
  - Body: JSON object with column values
  
- `PUT /api/{table_name}/{record_id}` - Update record
  - Body: JSON object with fields to update
  
- `DELETE /api/{table_name}/{record_id}` - Delete record

## Examples

### List all products (first 10)

```bash
curl http://localhost:8000/api/products
```

### Get specific product

```bash
curl http://localhost:8000/api/products/1
```

### Create new product

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "ProductName": "New Product",
    "SupplierID": 1,
    "CategoryID": 1,
    "QuantityPerUnit": "10 boxes",
    "UnitPrice": 99.99
  }'
```

### Update product

```bash
curl -X PUT http://localhost:8000/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "UnitPrice": 89.99
  }'
```

### Delete product

```bash
curl -X DELETE http://localhost:8000/api/products/1
```

## Project Structure

```
microserver/
├── main.py              # FastAPI app and CRUD endpoints
├── config.py            # Configuration and database URL
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy model reflection
├── schemas.py           # Pydantic response schemas
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Database Connection

The application uses SQLAlchemy with PyMySQL to connect to MySQL. Models are automatically reflected from the database schema at startup, allowing dynamic CRUD endpoints for any table.

### Connection Features

- Connection pooling with pre-ping verification
- Automatic connection recycling every hour
- SQL query logging (configurable in `database.py`)
- Support for foreign key relationships

## Error Handling

All endpoints return standardized JSON responses:

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error occurred",
  "error": "Detailed error message"
}
```

## Troubleshooting

### Database Connection Failed

1. Verify MySQL is running on 10.1.2.3
2. Check credentials in `.env` file
3. Ensure firewall allows connections to port 3306
4. Check network connectivity: `ping 10.1.2.3`

### Table Not Found

1. Verify table exists in the database
2. Restart the server to refresh table cache
3. Check table name spelling (case-sensitive)

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Performance Tips

- Use pagination with reasonable `limit` values
- Database indexes improve query performance
- Consider caching frequently accessed data
- Monitor connection pool usage

## Future Enhancements

- [ ] Authentication & authorization
- [ ] Query filtering and advanced search
- [ ] Batch operations (bulk insert/update/delete)
- [ ] Relationship loading strategies
- [ ] Database migrations
- [ ] Caching layer (Redis)
- [ ] Async request processing
- [ ] API rate limiting

## License

This project is provided as-is for educational purposes.