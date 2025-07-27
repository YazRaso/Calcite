from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path


CONFIG_FILE_PATH = (Path(__file__).parent.parent / 'config' / 'config.json').resolve()


def generate_receipt(
        received_by: str,
        reference_id: str,
        transaction_date: str,
        amount: float,
        currency: str,
        text_color: str = "black",
):
    """
    Generates a receipt by overlaying dynamic information onto a template image (585x451).
    Uses a default font.

    Args:
        filepath (str): Path to the spreadsheet file
        reference_id (str): The receipt reference number.
        transaction_date (str): The date of the transaction.
        amount (float): The amount paid.
        currency (str): The currency of the transaction (e.g., "USD", "AED").
        text_color (str, optional): Color of the text. Defaults to "black".
    """
    with open(CONFIG_FILE_PATH, "r") as file:
        data = json.load(file)
    from_person = data["user"]["name"]
    signature_path = data["user"]["signaturePath"]
    try:
        receipt_template_path = (Path(__file__).parent.parent / "assets" / "receipt_template.png").resolve() 
        img = Image.open(receipt_template_path).convert("RGB")
        font_path = (Path(__file__).parent.parent / 'fonts' / 'ttf' / 'JetBrainsMono-Regular.ttf').resolve()
        font = ImageFont.truetype(font_path, size=12) 
        draw = ImageDraw.Draw(img)

        positions = {
            "reference_id_value": (460, 77),  # After "No." label
            "date_value": (130, 162),  # After "DATE" label
            "from_person_value": (130, 187),  # After "FROM" (payer) label
            "acct_paid_amount_value": (170, 302),  # Column for amount
            "acct_paid_currency_text": (230, 302),  # Placed after the amount
            "received_by_value": (400, 305),  # Name of receiver
            "signature_area": (400, 330)
        }

        draw.text(positions["reference_id_value"], reference_id, fill=text_color, font=font)
        draw.text(positions["date_value"], transaction_date, fill=text_color, font=font)
        draw.text(positions["from_person_value"], from_person, fill=text_color, font=font)

        draw.text(positions["acct_paid_amount_value"], amount, fill=text_color, font=font)
        draw.text(positions["acct_paid_currency_text"], currency, fill=text_color, font=font)

        draw.text(positions["received_by_value"], received_by, fill=text_color, font=font)

        try:
            signature_img = Image.open(signature_path).convert("RGBA")
            max_sig_width = 170
            max_sig_height = 70
            signature_img.thumbnail((max_sig_width, max_sig_height))

            paste_x = positions["signature_area"][0]
            paste_y = positions["signature_area"][1]
            img.paste(signature_img, (paste_x, paste_y), signature_img)
        except FileNotFoundError:
            print(f"Warning: Signature file not found at {signature_path}")
        except Exception as e:
            print(f"Warning: Could not process signature image: {e}")

        receipt_name = f"{received_by}{reference_id}.png"
        output_path = (Path(__file__).parent.parent / "receipts" / receipt_name).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        img.save(output_path)
        return receipt_name

    except FileNotFoundError as e:
        print(f"Error: Template file not found at {receipt_template_path}. Exception: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")