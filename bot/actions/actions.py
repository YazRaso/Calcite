
from rasa_sdk import Action, Tracker
from typing import Any, Dict
import core as books


class AddTransaction(Action):
    def name(self) -> str:
        return "add_transaction"

    async def run(self, dispatcher, tracker: Tracker, domain: Dict[str, Any]):
        file_path = tracker.get_slot("file_path")
        if file_path:
            file_path = file_path.strip()
            if "EXCEL_FILE" in file_path:
                file_path = file_path.replace("EXCEL_FILE", "")
        amount_of_money = tracker.get_slot("amount_of_money")
        amount, currency = amount_of_money['value'], amount_of_money['unit']
        conversion_rate = tracker.get_slot("conversion_rate")
        reference_id = tracker.get_slot("reference_id")
        if reference_id:
            reference_id = reference_id.strip().lower()
            if "reference" in reference_id:
                reference_id = reference_id.replace("reference", "")
        time = tracker.get_slot("time")
        if not all([file_path, time, amount, currency, conversion_rate]):
            dispatcher.utter_message(text="Some information is missing. Please try again.")
            return []
        dispatcher.utter_message(
            text=f"Adding transaction amount: {amount} {currency}, conversion rate: {conversion_rate}, "
                 f"reference ID: {reference_id}, time: {time}"
        )
        current_workbook = books.ExcelManager(file_path)
        current_workbook.add_transaction(amount=amount, currency=currency, conversion_rate=conversion_rate,
                                         reference_id=reference_id, transaction_date=time)
        dispatcher.utter_message(text="Transaction added successfully.")
        return []


class DeleteTransaction(Action):
    def name(self) -> str:
        return "delete_transaction"

    async def run(self, dispatcher, tracker: Tracker, domain: Dict[str, Any]):
        file_path = tracker.get_slot("file_path")
        if file_path:
            file_path = file_path.strip()
            if "EXCEL_FILE" in file_path:
                file_path = file_path.replace("EXCEL_FILE", "")
        reference_id = tracker.get_slot("reference_id")
        if reference_id:
            reference_id = reference_id.strip().lower()
            if "reference" in reference_id:
                reference_id = reference_id.replace("reference", "")
        if not file_path or not reference_id:
            dispatcher.utter_message(text="File path or reference ID is missing. Please try again.")
            return []
        current_workbook = books.ExcelManager(file_path)
        current_workbook.delete_transaction(reference_id=reference_id)
        return []
