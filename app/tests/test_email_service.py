from unittest.mock import patch

import pytest

from app.services.email_service import send_email


@pytest.mark.asyncio
async def test_send_email_success():
    """
    Testa o envio simulado de e-mail com dados válidos.
    """
    email = "test@example.com"
    debt_id = "123e4567-e89b-12d3-a456-426614174000"
    boleto = {
        "boleto_id": "boleto-12345",
        "barcode": "12345678901234567890",
        "generated_at": "2024-12-15T12:00:00",
    }

    with patch("app.services.email_service.logger") as mock_logger:
        await send_email(email, debt_id, boleto)

        mock_logger.info.assert_called_once_with(
            f"Boleto generated to send email to {email} for debt ID {debt_id}."
        )


@pytest.mark.asyncio
async def test_send_email_missing_key_in_boleto():
    """
    Testa o envio simulado de e-mail quando falta uma chave no boleto.
    """
    email = "test@example.com"
    debt_id = "123e4567-e89b-12d3-a456-426614174000"
    boleto = {"barcode": "12345678901234567890", "generated_at": "2024-12-15T12:00:00"}

    with patch("app.services.email_service.logger") as mock_logger:
        with pytest.raises(KeyError) as exc_info:
            await send_email(email, debt_id, boleto)

        mock_logger.error.assert_called_once()
        assert "boleto_id" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_general_exception():
    """
    Testa o envio simulado de e-mail quando ocorre uma exceção geral.
    """
    email = "test@example.com"
    debt_id = "123e4567-e89b-12d3-a456-426614174000"
    boleto = None

    with patch("app.services.email_service.logger") as mock_logger:
        with pytest.raises(Exception) as exc_info:
            await send_email(email, debt_id, boleto)

        mock_logger.error.assert_called_once()
        assert "Failed to simulate email" in str(mock_logger.error.call_args[0][0])
