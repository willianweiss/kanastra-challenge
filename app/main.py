import asyncio

from asyncpg import create_pool
from fastapi import FastAPI, HTTPException, Query, UploadFile

from app.db.database import DATABASE_URL, TABLE_NAME, engine
from app.db.models import Base
from app.services.csv_processor import process_csv_file
from app.services.debt_service import (delete_record, get_filtered_data,
                                       save_to_database, update_record)

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

    asyncio.create_task(process_csv_file(pool))

    return {"message": "File uploaded and processing started"}


@app.get("/debts")
async def get_debts(
    debt_id: str = Query(None),
    status: str = Query(None),
):
    """
    GET endpoint para buscar dívidas com filtros.
    """
    debts = await get_filtered_data(pool, debt_id, status)
    return debts


@app.put("/debts/{debt_id}")
async def update_debt(debt_id: str, debt_update: dict):
    """
    PUT endpoint para atualizar uma dívida pelo ID.
    """
    if not debt_update:
        raise HTTPException(
            status_code=400, detail="The update payload cannot be empty."
        )

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
