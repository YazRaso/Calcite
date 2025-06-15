# Calcite

**An AI Agent that does your accounting for you — from managing spreadsheets to generating receipts.**

---

## 🚀 What is Calcite?

Calcite is a local desktop AI assistant that automates bookkeeping tasks like adding/deleting transactions and generating receipts. It uses Rasa for natural language understanding, a Qt GUI frontend, and Docker for deployment.

All transactions are stored and managed via Excel files, and receipts are auto-generated as images.

---

## 🧠 Features

- Add or delete transactions using natural language
- AI auto-extracts:
  - `amount`
  - `rate`
  - `currency`
  - `reference ID`
- Generate image-based receipts
- All actions are accessible via a simple GUI
- Local-only, no cloud dependencies
- Fully Dockerized for easy setup

---

## 💬 Example Phrases

You can type:

- `Add 150 USD at rate 3.5 with ref ID 2042`
- `Delete transaction with ref 2042`
---

## 🖼️ Output

Receipts are saved as **images** in the `receipts/` directory.  
Excel files must be placed **inside the `sheet_data/` directory or its subfolders** for the app to access them.

---

## 🧰 Tech Stack

- [Rasa](https://rasa.com) – NLP + intent recognition  
- [PyQt](https://riverbankcomputing.com/software/pyqt/) – GUI  
- [Docker](https://www.docker.com) – Containerization  
- `openpyxl` – Excel editing  
- `Pillow` – Receipt image generation

---

## ⚡ Quick Start (Docker)

```bash
# Clone the repo
git clone https://github.com/YazRaso/Calcite.git
cd Calcite

# Build and run everything
docker compose up --build
