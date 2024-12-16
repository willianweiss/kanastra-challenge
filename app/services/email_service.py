from app.utils.logging import logger

async def send_email(email, debt_id, boleto):
    """
    Simula o envio de e-mail com o boleto e gera logs detalhados.

    Args:
        email (str): Endereço de e-mail do destinatário.
        debt_id (str): ID da dívida associada ao boleto.
        boleto (dict): Dados do boleto, incluindo `boleto_id`, `barcode` e `generated_at`.
    """
    try:
        logger.info(f"Preparing to send email to {email} for debt ID {debt_id}.")

        logger.info(
            f"Email sent to {email}:\n"
            f"Subject: Boleto de pagamento - Dívida {debt_id}\n"
            f"Body:\n"
            f"Prezado(a),\n\n"
            f"Segue abaixo o boleto para pagamento referente à dívida com ID {debt_id}.\n\n"
            f"ID do Boleto: {boleto['boleto_id']}\n"
            f"Código de Barras: {boleto['barcode']}\n"
            f"Gerado em: {boleto['generated_at']}\n\n"
            f"Por favor, realize o pagamento antes da data de vencimento.\n\n"
            f"Atenciosamente,\nEquipe de Cobrança"
        )

    except Exception as e:
        logger.error(f"Failed to simulate email to {email} for debt ID {debt_id}: {e}")
        raise