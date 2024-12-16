import asyncio
from fastapi import FastAPI, UploadFile, HTTPException, Query
from asyncpg import create_pool
from app.services.debt_service import (
    save_to_database,
    get_filtered_data,
    update_record,
    delete_record,
)
from app.db.models import Base
from app.db.database import DATABASE_URL, TABLE_NAME, engine

pool = None

async def lifespan(app: FastAPI):
    """
    Define o ciclo de vida da aplicação.
    """
    global pool

    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    print("Database tables created.")

    pool = await create_pool(dsn=DATABASE_URL)
    print("Connection pool initialized.")

    yield

    if pool:
        await pool.close()
        print("Connection pool closed.")

    engine.dispose()
    print("Database engine disposed.")

app = FastAPI(lifespan=lifespan)

@app.post("/upload-csv")
async def upload_csv(file: UploadFile):
    """
    Endpoint para upload de arquivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()

    await save_to_database(content, TABLE_NAME, pool)

    # Processamento assíncrono
    asyncio.create_task(process_csv_file(pool))

    return {"message": "File uploaded and processing started"}

@app.get("/debts")
async def get_debts(
    name: str = Query(None),
    government_id: str = Query(None),
    email: str = Query(None),
    status: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None)
):
    """
    GET endpoint para buscar dívidas com filtros.
    """
    debts = await get_filtered_data(pool, name, government_id, email, status, min_amount, max_amount)
    return {"debts": debts}

@app.put("/debts/{debt_id}")
async def update_debt(debt_id: str, debt_update: dict):
    """
    PUT endpoint para atualizar uma dívida pelo ID.
    """
    result = await update_record(pool, debt_id, debt_update)
    if not result:
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"message": "Debt updated successfully"}

@app.delete("/debts/{debt_id}")
async def delete_debt(debt_id: str):
    """
    DELETE endpoint para remover uma dívida pelo ID.
    """
    result = await delete_record(pool, debt_id)
    if not result:
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"message": "Debt deleted successfully"}