import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import DebtStatus
from app.services.csv_processor import (process_batch, process_csv_file,
                                        process_debt)

MAX_WORKERS = 1000


@pytest.fixture
def mock_pool():
    """
    Cria um mock para o pool de conexões, configurando o suporte para contexto assíncrono.
    """
    async_conn = AsyncMock()
    pool = MagicMock()
    pool.acquire.return_value = async_conn
    async_conn.fetch = AsyncMock()
    async_conn.executemany = AsyncMock()
    async_conn.__aenter__.return_value = async_conn
    async_conn.__aexit__.return_value = None
    return pool


@pytest.fixture
def mock_debts():
    """
    Mock das dívidas pendentes.
    """
    return [
        {
            "debt_id": "1",
            "email": "test1@example.com",
            "debt_amount": 100.0,
            "status": DebtStatus.PENDING.value,
        },
        {
            "debt_id": "2",
            "email": "test2@example.com",
            "debt_amount": 200.0,
            "status": DebtStatus.PENDING.value,
        },
        {
            "debt_id": "3",
            "email": "test3@example.com",
            "debt_amount": 300.0,
            "status": DebtStatus.PENDING.value,
        },
    ]


@patch("app.services.csv_processor.generate_boleto", new_callable=AsyncMock)
@patch("app.services.csv_processor.send_email", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_csv_file(
    mock_send_email, mock_generate_boleto, mock_pool, mock_debts
):
    """
    Testa o processamento completo de dívidas.
    """
    mock_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = (
        mock_debts
    )

    mock_generate_boleto.return_value = {
        "boleto_id": "123",
        "barcode": "barcode",
        "generated_at": "2024-12-31",
    }
    mock_send_email.return_value = None

    await process_csv_file(mock_pool)

    assert mock_generate_boleto.call_count == len(mock_debts)
    assert mock_send_email.call_count == len(mock_debts)


@patch("app.services.csv_processor.generate_boleto", new_callable=AsyncMock)
@patch("app.services.csv_processor.send_email", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_batch(
    mock_send_email, mock_generate_boleto, mock_pool, mock_debts
):
    """
    Testa o processamento de um único batch.
    """
    mock_generate_boleto.return_value = {
        "boleto_id": "123",
        "barcode": "barcode",
        "generated_at": "2024-12-31",
    }
    mock_send_email.return_value = None

    await process_batch(mock_debts, mock_pool)

    mock_pool.acquire.return_value.__aenter__.return_value.executemany.assert_called_once()

    assert mock_generate_boleto.call_count == len(mock_debts)
    assert mock_send_email.call_count == len(mock_debts)


@patch("app.services.csv_processor.generate_boleto", new_callable=AsyncMock)
@patch("app.services.csv_processor.send_email", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_debt(mock_send_email, mock_generate_boleto, mock_pool):
    """
    Testa o processamento de uma única dívida.
    """
    debt = {"debt_id": "1", "email": "test1@example.com", "debt_amount": 100.0}

    semaphore = asyncio.Semaphore(MAX_WORKERS)

    await process_debt(debt, semaphore, mock_pool)

    mock_generate_boleto.assert_called_once_with(debt)

    mock_send_email.assert_called_once_with(
        debt["email"], debt["debt_id"], mock_generate_boleto.return_value
    )
