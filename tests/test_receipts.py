import pytest
import os
from pathlib import Path
from ..core.receipt import generate_receipt
import json

try:
    img = Image.open('assets/receipt_template.png')
    img.verify()
    print("Image is valid")
except Exception as e:
    print("Image open error:", e)

def test_generate_receipt():
    print("Current working directory:", os.getcwd())
    print("Absolute path to template:", Path('assets/receipt_template.png').resolve())
    print("File exists:", os.path.exists('assets/receipt_template.png'))
    print("File readable:", os.access('assets/receipt_template.png', os.R_OK))
    received_by = "Alice"
    reference_id = "2314"
    transaction_date = "10/06/2025"
    amount = "50.0"
    currency = "USD"
    config_path = (Path(__file__).parent.parent / "config" / "config.json").resolve()
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['user']['name'] = "John Doe"
    config['user']['signaturePath'] = str((Path(__file__).parent / "test_signature.png").resolve())
    with open(config_path, 'w') as f:
        json.dump(config, f)
    receipt_name = generate_receipt(received_by=received_by,
                                            reference_id=reference_id,
                                            transaction_date=transaction_date,
                                            amount=amount,
                                            currency=currency)
    receipt_path = (Path(__file__).parent.parent / "receipts").resolve() / receipt_name
    assert receipt_path.exists()
    
