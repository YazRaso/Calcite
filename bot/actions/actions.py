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
        amount_of_money = tracker.get_slot("amount_of_money")
        amount, currency = amount_of_money["value"], amount_of_money["unit"]
        conversion_rate = tracker.get_slot("conversion_rate")
        reference_id = tracker.get_slot("reference_id")
        transaction_id = id_generator.generate_id()
        time = tracker.get_slot("time")

        # Append transaction
        current_workbook = books.ExcelManager(file_path) 
        current_workbook.add_transaction(amount=amount, currency=currency, conversion_rate=conversion_rate,
                                         transaction_id=transaction_id, transaction_date=time)

        if not all([file_path, time, amount, currency, conversion_rate]):
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
        if not file_path or not reference_id:
            dispatcher.utter_message(text="File path or reference ID is missing. Please try again.")
            return []
        # Delete transaction
        current_workbook = books.ExcelManager(file_path)
        current_workbook.delete_transaction(reference_id=reference_id)
        return []

