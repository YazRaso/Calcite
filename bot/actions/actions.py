from rasa_sdk import Action, Tracker
from typing import Any, Dict
from core import books


class AddTransaction(Action):
    def name(self) -> str:
        return "add_transaction"

    # Add transaction and save it
    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[str, Any],
            ):
        # Get slots
        file_path = tracker.get_slot("file_path") 
        file_path = file_path.strip().replace("\n", "").replace("EXCEL_FILE_PATH", "")
        amount_of_money = tracker.get_slot("amount_of_money")
        if isinstance(amount_of_money, str):
            if " " in amount_of_money:
                amount_of_money = amount_of_money.split(" ", 1)
                amount = amount_of_money[0]
                currency = amount_of_money[1]
            else:
                for i, character in enumerate(amount_of_money):
                    if character.isalpha():
                        amount = amount_of_money[:i]
                        currency = amount_of_money[i:]
                        break
        elif isinstance(amount_of_money, Dict):
            amount = amount_of_money.get("value", 0)
            currency = amount_of_money.get("unit", "None")
        else:
            amount = amount_of_money
            currency = "None"
        conversion_rate = tracker.get_slot("number")
        reference_id = tracker.get_slot("reference_id")
        reference_id = reference_id.strip().lower()
        if "reference" in reference_id:
            reference_id = reference_id.replace("reference", "")
        time = tracker.get_slot("time")
        dispatcher.utter_message(
            text=f"Adding transaction"
                 f"amount: {amount} {currency}, conversion rate: {conversion_rate}, "
                 f"reference ID: {reference_id}, time: {time}"
        )
        # Append transaction
        current_workbook = books.ExcelManager(file_path) 
        current_workbook.add_transaction(amount=amount, currency=currency, conversion_rate=conversion_rate,
                                         reference_id=reference_id, transaction_date=time)

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
        file_path = file_path.replace("EXCEL_FILE_PATH", "")
        reference_id = tracker.get_slot("reference_id")
        reference_id = reference_id.strip().lower().replace("reference", "")
        if not file_path or not reference_id:
            dispatcher.utter_message(text="File path or reference ID is missing. Please try again.")
            return []
        # Delete transaction
        current_workbook = books.ExcelManager(file_path)
        current_workbook.delete_transaction(reference_id=reference_id)
        return []

