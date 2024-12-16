import asyncio

from app.db.models import DebtStatus
from app.services.boleto_service import generate_boleto
from app.services.email_service import send_email
from app.utils.logging import logger

BATCH_SIZE = 100000
MAX_WORKERS = 1000


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

    batches = [debts[i : i + BATCH_SIZE] for i in range(0, len(debts), BATCH_SIZE)]

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
