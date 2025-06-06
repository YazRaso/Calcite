from rasa_sdk import Action, Tracker
from typing import Any, Dict
import app.core.books as books
import app.core.id_generator as id_generator


class AddTransaction(Action):
    def name(self) -> str:
        return "add_transaction"

    # Add transaction and save it
    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[str, Any],
            ):
        # Get slots
        file_path = tracker.get_slot("file_path")
        amount, currency = tracker.get_slot("amount")["value"]["value"], tracker.get_slot("currency")["value"]["unit"]
        conversion_rate = tracker.get_slot("conversion_rate")
        reference_id = tracker.get_slot("reference_id")
        date = tracker.get_slot("date")

        # Append transaction
        current_workbook = books.ExcelManager(file_path) 
        current_workbook.add_transaction(amount=amount, currency=currency, conversion_rate=conversion_rate,
                                         transaction_id=transaction_id, transaction_date=date)

        if not all([file_path, date, amount, currency, conversion_rate]):
            dispatcher.utter_message(text="Some information is missing. Please try again.")
        else:
            dispatcher.utter_message(text="Transaction added successfully.")
        return []


class DeleteTransaction(Action):
    def name(self) -> str:
        return "delete_transaction"

    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[str, Any],
    ):
        # Get slots
        file_path = tracker.get_slot("file_path")
        reference_id = tracker.get_slot("reference_id")

        # Delete transaction
        current_workbook = books.ExcelManager(file_path)
        current_workbook.delete_transaction(reference_id=reference_id)
        return []

