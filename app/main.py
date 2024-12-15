import asyncio
from fastapi import FastAPI, UploadFile, HTTPException
from asyncpg import create_pool
from app.services.csv_processor import process_csv_file, save_to_database
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

    asyncio.create_task(process_csv_file(pool))

    return {"message": "File uploaded and processing started"}