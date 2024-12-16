import pytest
from datetime import datetime
from unittest.mock import patch
from app.services.boleto_service import generate_boleto

@pytest.mark.asyncio
async def test_generate_boleto_success():
    """
    Testa a geração de boleto com dados válidos.
    """
    debt = {
        "debt_id": "123e4567-e89b-12d3-a456-426614174000",
        "debt_amount": 100.50,
        "debt_due_date": "2024-01-01",
    }

    with patch("app.services.boleto_service.logger") as mock_logger:
        boleto = await generate_boleto(debt)

        assert "boleto_id" in boleto
        assert "barcode" in boleto
        assert "generated_at" in boleto

        expected_barcode = f"{debt['debt_id'][:10]}-{float(debt['debt_amount']):.2f}-{debt['debt_due_date']}"
        assert boleto["barcode"] == expected_barcode

        mock_logger.info.assert_called_once_with(f"Boleto generated for debt ID {debt['debt_id']}")

@pytest.mark.asyncio
async def test_generate_boleto_missing_key():
    """
    Testa a geração de boleto com uma chave ausente nos dados.
    """
    debt = {
        "debt_amount": 100.50,
        "debt_due_date": "2024-01-01",
    }

    with patch("app.services.boleto_service.logger") as mock_logger:
        with pytest.raises(KeyError) as exc_info:
            await generate_boleto(debt)

        mock_logger.error.assert_called_once_with(f"Missing key 'debt_id' in debt data: {debt}")
        assert str(exc_info.value) == "'debt_id'"

@pytest.mark.asyncio
async def test_generate_boleto_invalid_data():
    """
    Testa a geração de boleto com dados inválidos (debt_amount não é float).
    """
    debt = {
        "debt_id": "123e4567-e89b-12d3-a456-426614174000",
        "debt_amount": "invalid",
        "debt_due_date": "2024-01-01",
    }

    with patch("app.services.boleto_service.logger") as mock_logger:
        with pytest.raises(ValueError) as exc_info:
            await generate_boleto(debt)

        mock_logger.error.assert_called_once_with(f"Error generating boleto for debt: could not convert string to float: 'invalid'")