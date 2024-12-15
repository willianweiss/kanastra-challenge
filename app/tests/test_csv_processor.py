from io import BytesIO
from app.services.csv_processor import process_csv

async def test_process_csv():
    file_content = b"name,governmentId,email,debtAmount,debtDueDate,debtId\nJohn Doe,11111111111,johndoe@kanastra.com.br,1000.00,2022-10-12,1adb6ccf-ff16-467f-bea7-5f05d494280f"
    file = BytesIO(file_content)
    file.filename = "test.csv"
    await process_csv(file)