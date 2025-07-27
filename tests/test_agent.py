import pytest
import tempfile
import shutil
import requests
from pathlib import Path
from core.books import ExcelManager

FILE_NAME = 'TestBook.xlsx'
FILE_DOCKER_NAME = "/app/sheet_data/TestBoox.xlsx"
ORIGINAL_FILE = Path("sheet_data/TestBook.xlsx")
CORE_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"


@pytest.fixture
def client_temp_excel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir) / FILE_NAME
        shutil.copy(ORIGINAL_FILE, temp_path)
        client = ExcelManager(temp_path)
        yield client


def agent_delete_transaction(reference_id):
    prompt = (f"Delete transaction reference {reference_id}"
              f"EXCEL_FILE_PATH{FILE_DOCKER_NAME}")

    response = requests.post(url=CORE_SERVER_URL,
                             json={"sender": "user1", "message": prompt})
    return response.status_code == 200


def agent_add_transaction():
    amount = 50.0
    currency = "USD"
    conversion_rate = 3.67
    transaction_date = "05/10/2024"
    reference_id = "2431"
    prompt = (
        f"Add a transaction for {amount} {currency} at rate {conversion_rate} "
        f"for {transaction_date} reference {reference_id}"
        f"EXCEL_FILE_PATH/app/sheet_data/TestBoox.xlsx for today"
    )

    response = requests.post(url=CORE_SERVER_URL,
                             json={"sender": "user1", "message": prompt})
    return response.status_code == 200


def test_agent_add_transaction_1(client_temp_excel):
    client = client_temp_excel
    reference_id = "2431"
    amount = 50.0
    currency = "USD"
    conversion_rate = 3.67
    transaction_date = "05/10/2024"

    expected_row = [
        amount, currency, conversion_rate,
        transaction_date, reference_id
    ]

    assert agent_add_transaction(), "Server did not accept request"
    latest_row = client.ws.max_row

    assert all(
        client.ws.cell(row=latest_row, column=i+1).value == expected_row[i]
        for i in range(5)
    )


def test_agent_delete_transaction_1(client_temp_excel):
    client = client_temp_excel
    reference_id = "2431"

    assert agent_add_transaction(), "Server did not accept request"

    row_to_check = None
    for row in range(2, client.ws.max_row + 1):
        if client.ws.cell(row=row, column=5).value == reference_id:
            row_to_check = row
            break

    assert row_to_check is not None, "Reference ID not found before deletion"
    agent_delete_transaction(reference_id=reference_id)
    assert all(
        client.ws.cell(row=row_to_check, column=i+1).value is None
        for i in range(5)
    )
