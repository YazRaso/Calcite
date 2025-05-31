from openpyxl import Workbook, load_workbook
from pathlib import Path
from .receipt import generate_receipt


class ExcelManager:
    """
    A class representing an Excel workbook.
    Attributes:
        filepath (str): Path to the Excel workbook
    Methods:
        load_or_create(): Creates a new Excel workbook if it doesn't exist else loads it.
        add_transaction(
        amount, currency, conversion_rate, transaction_id, transaction_date, reference_id
        ): Adds a transaction to the Excel workbook.
        delete_transaction(): Deletes a transaction from the Excel workbook.
        check_summary(): checks if the workbook has a summary row
    """

    def __init__(self, filepath: str) -> None:
        """
        Initializes the Excel workbook, with a given filepath.
        :param filepath (str): Path to the Excel workbook:
        """
        super().__init__()
        self.filepath = Path(filepath)
        self.headers = ['Amount', 'Currency',
                        'Conversion Rate', 'Transaction ID',
                        'Transaction Date']

        self.load_or_create()

    def load_or_create(self) -> None:
        """
        Loads a given Excel workbook, if it doesn't exist then creates one.
        :return: None
        """
        if self.filepath.exists():
            self.wb = load_workbook(self.filepath)
            self.ws = self.wb.active
            for col_num, header in enumerate(self.headers, start=1):
                self.ws.cell(row=1, column=col_num, value=header)

            self.save()
        else:
            self.wb = Workbook()
            self.ws = self.wb.active
            self.ws.append(self.headers)
            self.save()

    def check_summary(self) -> bool:
        """
        check_summary checks whether the workbook has a summary row
        :return:
        """
        last_row_idx = self.ws.max_row
        # The workbook is either empty, or only contains the headers
        if not last_row_idx or last_row_idx <= 1:
            return False
        possible_words = {"summary", "total", "sum"}  # We could use NLP for this, but that could be overkill.
        for row in self.ws.iter_rows(min_row=2, max_row=last_row_idx, max_col=7):
            for cell in row:
                if cell.data_type == 'f' or (cell.value and isinstance(cell.value, str)
                                             and cell.value.lower() in possible_words):
                    return True
        return False

    def add_transaction(self, amount: float, currency: str, conversion_rate: float,
                        transaction_id: str, transaction_date: str, reference_id: str) -> None:
        """
        Adds a transaction to the last row of Excel workbook.
        :param amount:
        :param currency:
        :param conversion_rate:
        :param transaction_id:
        :param transaction_date:
        :param reference_id:
        :return: None
        """
        row = [
            amount,
            currency,
            conversion_rate,
            transaction_id,
            transaction_date,
            reference_id
        ]
        # If the last row is a summary,
        if self.check_summary():
            last_row_idx = self.ws.max_row
            self.ws.insert_rows(idx=last_row_idx, amount=1)
            for i in range(6):
                # indices in openpyxl are 1-based
                self.ws.cell(row=last_row_idx, column=(i + 1)).value = row[i]
        else:
            self.ws.append(row)
        self.save()

    def delete_transaction(self, reference_id: str) -> bool:
        first_row_number = 2
        number_of_cols = 6
        reference_id_column = 5
        for row in self.ws.iter_rows(min_row=first_row_number, max_col=number_of_cols):
            # Get transaction ID
            if row[reference_id_column].value == reference_id:
                self.ws.delete_rows(row[0].row)
                self.save()
                return True
        return False

    def generate_receipt(self) -> None:
        last_row = self.ws.max_row  # 1 based index of latest transaction
        if last_row <= 1:
            return
        if self.check_summary():
            last_row -= 1
        amount = self.ws.cell(row=last_row, column=1).value
        currency = self.ws.cell(row=last_row, column=2).value
        transaction_date = self.ws.cell(row=last_row, column=5).value
        reference_id = self.ws.cell(row=last_row, column=6).value
        if None in (amount, currency, transaction_date, reference_id):
            return
        generate_receipt(reference_no=reference_id, amount_paid=amount, currency=currency,
                         date_str=transaction_date)

    def save(self) -> None:
        self.wb.save(self.filepath)
