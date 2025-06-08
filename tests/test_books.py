import pytest
from pathlib import Path
from app.core.books import ExcelManager
import tempfile


@pytest.fixture
def temp_excel_file():
    # Create a temporary file path for Excel
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.xlsx"
        yield filepath


def test_summary(temp_excel_file):
    manager = ExcelManager(str(temp_excel_file))
    manager.ws["A2"] = 10
    manager.ws["A3"] = 10
    manager.ws["A4"] = "=A2+A3"
    manager.add_transaction(100.0, 'USD', 1.0, 'TXN123', '2025-05-27', 'REF123')
    assert manager.ws["A4"].value == 100


def test_create_excel_file(temp_excel_file):
    # Test loading or creating the Excel file
    manager = ExcelManager(str(temp_excel_file))
    assert temp_excel_file.exists()
    # Check headers
    headers = [cell.value for cell in manager.ws[1]]
    expected_headers = ['Amount', 'Currency', 'Conversion Rate', 'Transaction ID', 'Transaction Date']
    assert headers[:len(expected_headers)] == expected_headers


def test_add_transaction(temp_excel_file):
    manager = ExcelManager(str(temp_excel_file))
    manager.add_transaction(100.0, 'USD', 1.0, 'TXN123', '2025-05-27', 'REF123')

    # Verify transaction was added to the sheet
    last_row = list(manager.ws.iter_rows(values_only=True))[-1]
    assert last_row[0] == 100.0
    assert last_row[1] == 'USD'
    assert last_row[3] == 'TXN123'
    assert last_row[5] == 'REF123'


def test_delete_transaction(temp_excel_file):
    manager = ExcelManager(str(temp_excel_file))
    # Add two transactions
    manager.add_transaction(50, 'EUR', 0.9, 'TXN001', '2025-05-26', 'REF001')
    manager.add_transaction(75, 'USD', 1.0, 'TXN002', '2025-05-27', 'REF002')

    # Delete one transaction by reference ID
    deleted = manager.delete_transaction('REF001')
    assert deleted is True

    # Try deleting a non-existent one
    deleted = manager.delete_transaction('REF999')
    assert deleted is False

    # Confirm REF001 no longer exists in sheet
    reference_ids = [row[5].value for row in manager.ws.iter_rows(min_row=2)]
    assert 'REF001' not in reference_ids
