
# Kanastra Challenge

A FastAPI project for managing debts, providing endpoints for uploading, processing, and querying debt data.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Running the Project](#running-the-project)
- [Endpoints](#endpoints)
- [Usage](#usage)
- [Testing](#testing)

---

## Features
- **Upload CSV**: Upload debt data in bulk and process it asynchronously.
- **Batch Processing**: Efficient processing of large datasets with error handling.
- **CRUD Operations**:
  - GET: Query debts with optional filters (e.g., `debt_id`, `status`).
  - PUT: Update a debt by its ID.
  - DELETE: Remove a debt by its ID.

---

## Setup
### Prerequisites
- **Docker**: Ensure Docker is installed on your system.
- **Docker Compose**: Required for container orchestration.

### Environment Variables
Create a `.env` file in the root of the project with the following content:
```env
# Database configuration
POSTGRES_USER=kanastra_user
POSTGRES_PASSWORD=kanastra_pass
POSTGRES_DB=kanastra_db
POSTGRES_HOST=localhost
```

---

## Running the Project
### Using Docker Compose

1. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Endpoints

### 1. **Upload CSV**
Upload a CSV file to process debts.
- **POST** `/upload-csv`
- **Request**:
  - `file` (required): CSV file containing debt data.
- **Response**:
  ```json
  {
    "message": "File uploaded and processing started"
  }
  ```

### 2. **Query Debts**
Fetch debts with optional filters.
- **GET** `/debts`
- **Query Parameters**:
  - `debt_id` (optional): Filter by debt ID.
  - `status` (optional): Filter by status (`PENDING`, `PROCESSED`, `FAILED`).
- **Response**:
  ```json
  [
    {
        "debt_id": "1",
        "name": "John Doe",
        "email": "john@example.com",
        "status": "PENDING"
    }
  ]
  ```

### 3. **Update Debt**
Update a specific debt by ID.
- **PUT** `/debts/{debt_id}`
- **Request Body**:
  ```json
  {
    "name": "New Name",
    "status": "PROCESSED"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Debt updated successfully"
  }
  ```

### 4. **Delete Debt**
Delete a specific debt by ID.
- **DELETE** `/debts/{debt_id}`
- **Response**:
  ```json
  {
    "message": "Debt deleted successfully"
  }
  ```

---

## Usage
### Example: Query Debts
Check for any debts with errors:
```bash
curl -X GET "http://localhost:8000/debts?status=FAILED"
```

### Example: Update a Debt
Mark a debt as processed:
```bash
curl -X PUT "http://localhost:8000/debts/1" -H "Content-Type: application/json" -d '{"status": "PROCESSED"}'
```

---

## Testing
Run the tests using `pytest`:
1. Install dependencies (if running locally):
   ```bash
   pip install -r requirements.txt
   ```
2. Run tests:
   ```bash
   pytest
   ```

---

## Notes
- **Environment Configuration**: Ensure the `.env` file is present and configured correctly.
- **Monitoring**: Use the **GET /debts** endpoint to monitor processing results or check for errors (`status=FAILED`).
- **Manual Fixes**: Use the **PUT /debts/{debt_id}** and **DELETE /debts/{debt_id}** endpoints to manually fix or remove problematic entries.
