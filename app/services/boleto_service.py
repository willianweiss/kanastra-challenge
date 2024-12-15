from datetime import datetime
import uuid
from app.utils.logging import logger

async def generate_boleto(debt):
    """
    Gera um boleto para o débito informado.
    """
    try:
        boleto_id = str(uuid.uuid4())
        barcode = f"{str(debt['debt_id'])[:10]}-{float(debt['debt_amount']):.2f}-{debt['debt_due_date']}"
        generated_at = datetime.now().isoformat()

        logger.info(f"Boleto generated for debt ID {str(debt['debt_id'])}")
        return {"boleto_id": boleto_id, "barcode": barcode, "generated_at": generated_at}
    except KeyError as e:
        logger.error(f"Missing key {e} in debt data: {debt}")
        raise
    except Exception as e:
        logger.error(f"Error generating boleto for debt: {str(e)}")
        raise