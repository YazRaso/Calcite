import unittest
from pathlib import Path
import os
from PyPDF2 import PdfReader
from receipts import ReceiptGenerator  # Ensure this is the correct import path

class TestReceiptGenerator(unittest.TestCase):

    def setUp(self):
        # Create a temporary file path for testing
        self.test_file = 'test_client_data.xlsx'
        self.receipt_generator = ReceiptGenerator(self.test_file)
        self.receipt_path = Path(self.receipt_generator.filepath)

    def tearDown(self):
        # Clean up any generated files after the tests
        if self.receipt_path.exists():
            os.remove(self.receipt_path)

    def test_client_name_extraction(self):
        # Check if the client name is correctly extracted
        expected_client_name = 'test_client_data'
        self.assertEqual(self.receipt_generator.client_name, expected_client_name)

    def test_generate_receipt_creates_pdf(self):
        # Generate the receipt
        self.receipt_generator.generate_receipt(100.5, 'USD', 1.1, 'T123', '2025-05-13')

        # Check if the receipt file was created
        self.assertTrue(self.receipt_path.exists())

    def test_receipt_file_name(self):
        # Ensure the receipt file has the correct name
        expected_file_name = 'test_client_data_receipt.pdf'
        self.assertEqual(self.receipt_path.name, expected_file_name)

    def test_pdf_content(self):
        # Generate the receipt
        self.receipt_generator.generate_receipt(100.5, 'USD', 1.1, 'T123', '2025-05-13')

        # Open the generated PDF and extract text
        with open(self.receipt_path, "rb") as f:
            reader = PdfReader(f)
            page = reader.pages[0]
            text = page.extract_text()

        # Check if the expected text is in the PDF content
        self.assertIn("Amount: 100.5 USD", text)
        self.assertIn("Conversion Rate: 1.1", text)
        self.assertIn("Transaction ID: T123", text)
        self.assertIn("Total: 110.55 USD", text)  # Based on amount * conversion rate


if __name__ == '__main__':
    unittest.main()
