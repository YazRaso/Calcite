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
        file_path = tracker.get_slot("file_path")
        current_workbook = books.ExcelManager(file_path)
        date = tracker.get_slot("date")
        amount = tracker.get_slot("amount")
        currency = tracker.get_slot("currency")
        conversion_rate = tracker.get_slot("conversion_rate")
        reference_id = tracker.get_slot("reference_id")
        # Ensure function arguments are in correct format
        if file_path.startswith("EXCEL_FILE_PATH:"):
            file_path = file_path[len("EXCEL_FILE_PATH:"):]
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        if "rate " in conversion_rate:
            conversion_rate = conversion_rate.replace("rate ", "")
        if "reference " in reference_id:
            reference_id = reference_id.replace("reference", "")
        # Add client name to transaction ID
        transaction_id = file_path[:-5] + id_generator.generate_id()
        print("Latest user message:", tracker.latest_message.get('text'))
        print("Extracted intent:", tracker.latest_message.get('intent'))
        print("Extracted entities:", tracker.latest_message.get('entities'))
        print("Slots:")
        print(f"  file_path: {tracker.get_slot('file_path')}")
        print(f"  date: {tracker.get_slot('date')}")
        print(f"  amount: {tracker.get_slot('amount')}")
        print(f"  currency: {tracker.get_slot('currency')}")
        print(f"  conversion_rate: {tracker.get_slot('conversion_rate')}")
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
        file_path = tracker.get_slot("file_path")
        reference_id = tracker.get_slot("reference_id")
        if file_path.startswith("EXCEL_FILE_PATH:"):
            file_path = file_path[len("EXCEL_FILE_PATH:"):]
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        current_workbook = books.ExcelManager(file_path)
        if current_workbook.delete_transaction(reference_id=reference_id):
            dispatcher.utter_message(text="Transaction deleted successfully.")
        else:
            dispatcher.utter_message(text="Failed to delete transaction.")
        return []


class SimpleAction(Action):
    def name(self) -> str:
        return "simple_action"

    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[str, Any],
    ):
        dispatcher.utter_message(text="hey there")
