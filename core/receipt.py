from PIL import Image, ImageDraw, ImageFont
import json


def generate_receipt(
        reference_no: str,
        date_str: str,
        amount_paid: float,
        currency: str,
        received_by: str = "",
        text_color: str = "black",
        template_path: str = "./assets/receipt_template.png",
        output_path: str = "./receipts",
):
    """
    Generates a receipt by overlaying dynamic information onto a template image (585x451).
    Uses a default font.

    Args:
        template_path (str): Path to the receipt template image.
        output_path (str): Path to save the generated receipt image.
        reference_no (str): The receipt reference number.
        date_str (str): The date of the transaction.
        from_person (str): The name of the person making the payment (for the "FROM" field).
        amount_paid (float): The amount paid.
        currency (str): The currency of the transaction (e.g., "USD", "AED").
        received_by (str): The name of the person who received the payment.
        text_color (str, optional): Color of the text. Defaults to "black".
    """

    with open("../config/config.json", "r") as file:
        data = json.load(file)
    from_person = data["user"]["name"]
    signature_path = data["user"]["signature"]
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.load_default()
        except IOError:
            print("Error: Could not load default font. Ensure Pillow is correctly installed.")
            # Fallback if default font isn't found (very unlikely)
            # Using a common system font as a last resort, size might not match default.
            try:
                font = ImageFont.truetype("arial.ttf", 10)
                print("Warning: Default font failed. Using Arial 10pt as fallback.")
            except IOError:
                print("Critical Error: No suitable font found. Text will not be rendered.")
                return  # Stop processing if no font can be loaded

        # --- Estimated positions (x, y) for a 585x451 template ---
        # These are top-left anchors for the text. You WILL likely need to adjust these.
        # The labels "DATE:", "FROM:", "FOR:", "PAID", "DUE", "RECEIVED BY"
        # are assumed to be part of your template image. We are placing the *values*.
        positions = {
            "reference_no_value": (460, 80),  # After "No." label
            "date_value": (130, 165),  # After "DATE" label
            "from_person_value": (130, 190),  # After "FROM" (payer) label
            # Table items (assuming labels "PAID", "DUE" are on the template)
            # Value for PAID amount
            "acct_paid_amount_value": (170, 305),  # Column for amount
            # Currency symbol/code text, e.g., "(USD)" or "AED"
            "acct_paid_currency_text": (230, 305),  # Placed after the amount
            # Value for DUE amount
            "acct_due_amount_value": (170, 340),

            # Right-hand side (assuming "RECEIVED BY" label is on template)
            "received_by_value": (400, 308),  # Name of receiver
            # Top-left corner for placing the signature image, under "SIGNATURE" label
            "signature_area": (400, 340)
        }

        # --- Add text to the image ---
        draw.text(positions["reference_no_value"], reference_no, fill=text_color, font=font)
        draw.text(positions["date_value"], date_str, fill=text_color, font=font)
        draw.text(positions["from_person_value"], from_person, fill=text_color, font=font)

        # Amount details in the table
        draw.text(positions["acct_paid_amount_value"], f"{amount_paid:.2f}", fill=text_color, font=font)
        draw.text(positions["acct_paid_currency_text"], currency, fill=text_color, font=font)
        # Assuming 'DUE' is 0 if 'PAID' is the full amount. Adjust if needed.
        draw.text(positions["acct_due_amount_value"], "0.00", fill=text_color, font=font)

        draw.text(positions["received_by_value"], received_by, fill=text_color, font=font)

        # --- Add signature ---
        if signature_path:
            try:
                signature_img = Image.open(signature_path).convert("RGBA")
                # Define a max size for the signature
                max_sig_width = 150  # Adjust as needed
                max_sig_height = 40  # Adjust as needed
                signature_img.thumbnail((max_sig_width, max_sig_height))

                paste_x = positions["signature_area"][0]
                paste_y = positions["signature_area"][1]
                img.paste(signature_img, (paste_x, paste_y), signature_img)
            except FileNotFoundError:
                print(f"Warning: Signature file not found at {signature_path}")
            except Exception as e:
                print(f"Warning: Could not process signature image: {e}")

        # Save the image
        img.save(output_path)

    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")


# if __name__ == "__main__":
#     # --- Create a dummy signature image for testing ---
#     dummy_signature_path = "../assets/dummy_signature.png"
#     try:
#         sig_img = Image.new('RGBA', (200, 60), (255, 255, 255, 0))  # Transparent background
#         sig_draw = ImageDraw.Draw(sig_img)
#         try:
#             # Attempt to load default font, potentially with a size hint if supported
#             # Pillow's default font is bitmap, so "size" might not be directly settable for load_default() itself
#             # but often a slightly larger version can be loaded if available by other means if needed.
#             # For this dummy signature, exact font isn't critical, but legibility is.
#             sig_font = ImageFont.truetype("arial.ttf", 25)  # Using Arial for a clearer dummy sig
#         except IOError:
#             sig_font = ImageFont.load_default()  # Fallback to basic default
#         sig_draw.text((10, 5), "J. Doe", fill="navy", font=sig_font)
#         sig_img.save(dummy_signature_path)
#     except Exception as e:
#         print(f"Could not create dummy signature: {e}")
#         dummy_signature_path = ""
#
#     # --- Example Usage ---
#     template_file = "../assets/receipt_template"
#
#     import os
#
#     if not os.path.exists(template_file):
#         print(f"Template file '{template_file}' not found. Skipping example generation.")
#     elif not dummy_signature_path and os.path.exists(dummy_signature_path):  # check if sig was created
#         print(f"Dummy signature not created or found. Skipping example generation.")
#     else:
#         print(f"Generating example receipt using template: {template_file} with default font.")
#         generate_receipt(
#             template_path=template_file,
#             output_path="generated_receipt_adjusted.png",
#             reference_no="REF78901",
#             date_str="May 23, 2025",
#             from_person="Ms. Example Payer",
#             for_payment="Consultation Services Rendered",
#             amount_paid=350.00,
#             currency="AED",
#             received_by="Receiver Name Here",
#             signature_path=dummy_signature_path,
#             draw_debug_points=True  # Set to True to see where text anchors are
#         )
#         print(
#             "Check 'generated_receipt_adjusted.png'. If positions are off, edit the 'positions' dictionary in the script.")
#         print("Set 'draw_debug_points=False' once positions are good.")
