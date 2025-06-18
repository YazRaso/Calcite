import pytest
from pathlib import Path
from ..core.receipt import generate_receipt


def test_generate_receipt():
    received_by = "Alice"
    reference_id = "2314"
    transaction_date = "10/06/2025"
    amount = "50.0"
    currency = "USD"
    receipt_name = generate_receipt(received_by=received_by,
                                            reference_id=reference_id,
                                            transaction_date=transaction_date,
                                            amount=amount,
                                            currency=currency)
    receipt_path = (Path(__file__).parent.parent / "receipts").resolve() / receipt_name
    assert receipt_path.exists()
