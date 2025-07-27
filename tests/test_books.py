import pytest
import tempfile
import shutil
from pathlib import Path
from core.books import ExcelManager

FILE_NAME = 'TestBook.xlsx'
ORIGINAL_FILE = (Path(__file__).parent.parent / 'sheet_data' / FILE_NAME).resolve()


@pytest.fixture
def temp_client():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / FILE_NAME
        shutil.copy(ORIGINAL_FILE, temp_path)
        client = ExcelManager(temp_path)
        yield client


def test_load_1(temp_client):
    headers = ['Amount', 'Currency',
               'Conversion Rate', 'Transaction Date',
               'Reference ID']
    assert all(temp_client.ws.cell(row=1, column=i+1).value == headers[i]
               for i in range(5))


def test_add_transaction_1(temp_client):
    amount = 50.0
    currency = "USD"
    conversion_rate = 3.67
    transaction_date = "05/10/2024"
    reference_id = "2431"

    expected_row = [
        amount, currency, conversion_rate,
        transaction_date, reference_id
    ]

    temp_client.add_transaction(amount=amount,
                                currency=currency,
                                conversion_rate=conversion_rate,
                                transaction_date=transaction_date,
                                reference_id=reference_id)
    latest_row = temp_client.ws.max_row
    assert all(temp_client.ws.cell(row=latest_row,
                                   column=i+1).value == expected_row[i]
               for i in range(5))


def test_delete_transaction_1(temp_client):
    amount = 50.0
    currency = "USD"
    conversion_rate = 3.67
    transaction_date = "05/10/2024"
    reference_id = "2431"

    temp_client.add_transaction(amount=amount,
                                currency=currency,
                                conversion_rate=conversion_rate,
                                transaction_date=transaction_date,
                                reference_id=reference_id)

    row_to_check = None
    for row in range(2, temp_client.ws.max_row + 1):
        if temp_client.ws.cell(row=row, column=5).value == reference_id:
            row_to_check = row
            break
    assert row_to_check is not None, "Unable to find reference_id, does the transaction exist?"

    temp_client.delete_transaction(reference_id=reference_id)

    assert all(temp_client.ws.cell(row=row_to_check,
                                   column=i+1).value is None
               for i in range(5))


def test_delete_transaction_2(temp_client):
    non_existent_ref = "This transaction wouldn't exist"
    transaction_deleted = temp_client.delete_transaction(reference_id=non_existent_ref)
    assert not transaction_deleted
