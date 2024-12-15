import asyncio
import csv
from io import StringIO
from app.db.models import DebtStatus
from app.services.boleto_service import generate_boleto
from app.services.email_service import send_email
from datetime import datetime
import uuid
from app.utils.logging import logger

BATCH_SIZE = 10000
MAX_WORKERS = 1000

async def save_to_database(content: bytes, table_name: str, pool):
    """
    Insere dados do CSV diretamente no banco usando asyncpg e um pool de conexões.

    Args:
        content (bytes): Conteúdo do arquivo CSV.
        table_name (str): Nome da tabela no banco.
    """
    logger.info("Saving data to the database...")
    reader = csv.DictReader(StringIO(content.decode("utf-8")))
    debts = [
        (
            uuid.UUID(row["debtId"]),
            row["name"],
            row["governmentId"],
            row["email"],
            float(row["debtAmount"]),
            datetime.strptime(row["debtDueDate"], "%Y-%m-%d").date(),
            "PENDING",
        )
        for row in reader
    ]

    try:
        async with pool.acquire() as conn:
            query = f"""
                INSERT INTO {table_name} 
                (debt_id, name, government_id, email, debt_amount, debt_due_date, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (debt_id) DO NOTHING
            """
            for i in range(0, len(debts), BATCH_SIZE):
                batch = debts[i:i + BATCH_SIZE]
                await conn.executemany(query, batch)
                logger.info(f"Inserted batch {i // BATCH_SIZE + 1}, size: {len(batch)}")

        logger.info("Data successfully saved to the database.")
    except Exception as e:
        logger.error(f"Error while saving data: {e}")
        raise

async def process_csv_file(pool):
    """
    Processa dívidas em status PENDING em batches usando asyncio.
    """
    logger.info("Starting debt processing...")

    async with pool.acquire() as conn:
        debts = await conn.fetch(
            "SELECT * FROM debt WHERE status = $1", DebtStatus.PENDING.value
        )
        logger.info(f"Loaded {len(debts)} debts to process.")

    if not debts:
        logger.info("No pending debts to process. Exiting.")
        return

    batches = [debts[i:i + BATCH_SIZE] for i in range(0, len(debts), BATCH_SIZE)]

    for batch in batches:
        await process_batch(batch, pool)

    logger.info("Debt processing completed.")

async def process_batch(batch, pool):
    """
    Processa um batch de dívidas em paralelo.
    """
    semaphore = asyncio.Semaphore(MAX_WORKERS)

    tasks = [process_debt(debt, semaphore, pool) for debt in batch]
    await asyncio.gather(*tasks)

    async with pool.acquire() as conn:
        debt_ids = [str(debt["debt_id"]) for debt in batch]
        await conn.executemany(
            "UPDATE debt SET status = $1 WHERE debt_id = $2",
            [(DebtStatus.PROCESSED.value, debt_id) for debt_id in debt_ids],
        )
        logger.info(f"Updated {len(debt_ids)} debts to PROCESSED.")

async def process_debt(debt, semaphore, pool):
    """
    Processa uma única dívida.

    Args:
        debt: Linha de resultado do banco.
        semaphore (asyncio.Semaphore): Controle de concorrência.
        pool: Pool de conexões.
    """
    async with semaphore:
        try:
            debt_id = str(debt["debt_id"])
            email = debt["email"]

            boleto = await generate_boleto(debt)
            await send_email(email, debt_id, boleto)
            logger.info(f"Successfully processed debt ID {debt_id}")
        except Exception as e:
            logger.error(f"Error processing debt ID {debt['debt_id']}: {e}")

            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE debt SET status = $1 WHERE debt_id = $2",
                    DebtStatus.FAILED.value,
                    str(debt["debt_id"]),
                )