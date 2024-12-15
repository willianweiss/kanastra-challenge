import asyncio
from fastapi import FastAPI, UploadFile, HTTPException
from asyncpg import create_pool
from app.services.csv_processor import process_csv_file, save_to_database
from app.db.models import Base
from app.db.database import engine
from app.utils.config import settings
import os

# Definição das configurações do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:5432/{settings.POSTGRES_DB}"
)
TABLE_NAME = 'debt'

# Pool de conexões global
pool = None


async def lifespan(app: FastAPI):
    """
    Define o ciclo de vida da aplicação.
    """
    global pool  # Certifique-se de declarar global aqui

    # Executado no startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Cria as tabelas do banco
    print("Database tables created.")

    # Inicializa o pool de conexões
    pool = await create_pool(dsn=DATABASE_URL)
    print("Connection pool initialized.")

    yield  # A aplicação estará rodando após este ponto

    # Executado no shutdown
    if pool:
        await pool.close()
        print("Connection pool closed.")  # Log opcional para confirmar o encerramento

    await engine.dispose()
    print("Database engine disposed.")  # Log opcional para confirmar o encerramento


# Instancia o FastAPI e aplica o ciclo de vida definido
app = FastAPI(lifespan=lifespan)


@app.post("/upload-csv")
async def upload_csv(file: UploadFile):
    """
    Endpoint para upload de arquivo CSV.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Lê o conteúdo do arquivo CSV
    content = await file.read()

    # Salva os dados no banco
    await save_to_database(content, TABLE_NAME, pool)

    # Processa as dívidas em segundo plano
    asyncio.create_task(process_csv_file(pool))

    return {"message": "File uploaded and processing started"}