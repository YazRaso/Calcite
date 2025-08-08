# Calcite
![License](https://img.shields.io/github/license/YazRaso/Calcite)
![Last Commit](https://img.shields.io/github/last-commit/YazRaso/Calcite)
![Issues](https://img.shields.io/github/issues/YazRaso/Calcite)
![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9-blue)
![Tests](https://github.com/YazRaso/Calcite/actions/workflows/test.yml/badge.svg)


> 🧮 Like Copilot, but for bookkeeping.  
> A local-first, AI agent that writes transactions and generates receipts, with heavy emphasis on user privacy.

**Calcite** is a production-grade desktop app that manages your financial records via natural language.  
It parses commands like:  
`"Add a transaction for 5000 USD at rate 0.25 reference 4392 for today"`  
and updates your Excel file, generates a receipt image — all processed locally.

---

## 🧱 Requirements
- Python 3.9
- Docker
- ✅ Supported: x86_64 architecture (e.g., most Windows/Linux PCs and Intel-based Macs)
- ⚠️ Not Supported: ARM-based systems (e.g., Apple Silicon/M1/M2)

## 🔧 Features

- 🧠 Intent parsing with Rasa and Duckling
- 🧾 Excel transaction management via `openpyxl`
- 🖼️ Receipt image generation with `Pillow`
- 🖥️ Desktop GUI built using PySide6 (Qt)
- 🐳 Dockerized deployment
- ✅ CI integration with GitHub Actions

## 🚀 Quick Start (Unix Systems: Linux, Mac)
```bash
git clone https://github.com/YazRaso/calcite.git
python3.9 -m venv .venv
source .venv/bin/activate
cd Calcite/bot/actions
pip install -r requirements_core.txt
chmod u+x ./start.sh
./start.sh
```
## 🚀 Quick Start (Windows)
```bash
git clone https://github.com/YazRaso/calcite.git
python3.9 -m venv .venv
source .venv/scripts/activate
cd Calcite/bot/actions
pip install -r requirements_core.txt
chmod u+x ./start.sh
./start.sh
```

---
## 😄 Welcome to Calcite
Upload your name and signature (displayed on receipts)

## ⚙️ Usage

### 📝 Worksheet Selection

Before performing any actions, select a worksheet.  
> 📌 **Important:** Worksheets **must** be descendants of the `sheet_data/` directory.

---

### ➕ Adding a Transaction

To add a transaction, the following fields are required:

- `Amount`
- `Currency`
- `Date`
- `Exchange Rate`
- `Reference ID`

> ⚠️ **Note:** The `Reference` field **must be spelled** as `Reference` (case insensitive) in the worksheet. After entering the Reference ID, make sure to press **space** to confirm the input.

---

### ❌ Deleting a Transaction

To delete a transaction, you only need:

- `Reference ID`

> The app will locate and remove the transaction based on the matching `Reference` field.

> ⚠️ **Note:** The `Reference` field **must be spelled** as `Reference` (case insensitive) in the worksheet. After entering the Reference ID, make sure to press **space** to confirm the input.

---

### 🧾 Receipt Generation

To generate a receipt for a transaction, provide:

- `Reference ID`

> ⚠️ **Note:** The `Reference` field **must be spelled** as `Reference` (case insensitive) in the worksheet. After entering the Reference ID, make sure to press **space** to confirm the input.

> Calcite will fetch the transaction by Reference ID and produce a receipt.


## 🛝 Play around
Select a file to work on or use the provided blank spreadsheet "TestBook.xlsx"
Go ahead, try to add and delete a few transactions, generate receipts!

---
## 💡 Tips and Troubleshooting
## 💡 TIP: Make sure your signature is in .PNG format ensuring quality and compatibility
## 🐳 Docker build fail?
The build may fail on some systems due to relative paths on the provided .env file
Create a .env file in the ```Calcite/docker``` directory
1. set the following paths BOT_PATH, ACTIONS_PATH, CORE_PATH, SHEET_PATH to their absolute paths on your machine.
## 🤔 Want to change signature or name
1. (I want to make my changes using the GUI) In ```config/config.json``` set ```["user"]["firstTime"] = True```
2. (I want to make my changes manually) In ```config/config.json``` set ```["user"]["name"] = <new_name>```, ```["user"]["signaturePath"] = <new_signature>```
> ⚠️ **Note:** Restart the application after making your changes

---
## ✉️ Want to suggest a feature or encountered a bug?
Do not hesistate to contact me if you have a specific feature in mind or have encountered, I am more than happy to help you personally, email: raso8856@mylaurier.ca






