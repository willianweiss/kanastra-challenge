import csv
import uuid
from datetime import datetime
from io import StringIO

from app.utils.logging import logger

BATCH_SIZE = 100000


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
                batch = debts[i : i + BATCH_SIZE]
                await conn.executemany(query, batch)
                logger.info(f"Inserted batch {i // BATCH_SIZE + 1}, size: {len(batch)}")

        logger.info("Data successfully saved to the database.")
    except Exception as e:
        logger.error(f"Error while saving data: {e}")
        raise


async def get_filtered_data(pool, debt_id=None, status=None):
    """
    Busca dívidas com filtros opcionais.
    """
    query = "SELECT * FROM debt WHERE 1=1"
    conditions = []
    values = []

    if debt_id:
        conditions.append("CAST(debt_id AS TEXT) ILIKE $1")
        values.append(f"%{debt_id}%")
    if status:
        conditions.append(f"status = ${len(values) + 1}")
        values.append(status)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    async with pool.acquire() as conn:
        return await conn.fetch(query, *values)


async def update_record(pool, debt_id: str, debt_update: dict):
    """
    Atualiza um registro pelo ID.
    """
    if not debt_update:
        raise ValueError("debt_update cannot be empty")

    for key, value in debt_update.items():
        if "date" in key.lower() and isinstance(value, str):
            try:
                debt_update[key] = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format for field '{key}': {value}")

    set_clause = ", ".join(
        [f"{key} = ${i+2}" for i, key in enumerate(debt_update.keys())]
    )
    query = f"UPDATE debt SET {set_clause} WHERE debt_id = $1"
    values = [debt_id] + list(debt_update.values())

    async with pool.acquire() as conn:
        result = await conn.execute(query, *values)
        return result == "UPDATE 1"


async def delete_record(pool, debt_id: str):
    """
    Remove um registro pelo ID.
    """
    query = "DELETE FROM debt WHERE debt_id = $1"

    async with pool.acquire() as conn:
        result = await conn.execute(query, debt_id)
        return result == "DELETE 1"
