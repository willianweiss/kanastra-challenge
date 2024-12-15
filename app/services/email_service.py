# app/services/email_service.py
from app.utils.logging import logger

async def send_email(email, debt_id, boleto):
    """
    Envia o e-mail com o boleto.
    """
    logger.info(f"Sending email to {email} for debt ID {debt_id}")
    # Simulação do envio do e-mail