# Calcite

> 🧮 Like Copilot, but for bookkeeping.  
> A local-first, voice-enabled desktop assistant that automates transactions and generates receipts.

**Calcite** is a production-grade desktop app that manages your financial records via natural language.  
It parses spoken or written commands like:  
`"Add a transaction for 5000 USD at rate 0.25 reference 4392 for today"`  
and updates your Excel file, generates a receipt image, and provides voice feedback — all processed locally.

---

## 🧱 Requirements
- Python 3.9
- Docker
- ✅ Supported: x86_64 architecture (e.g., most Windows/Linux PCs and Intel-based Macs)
- ⚠️ Not Supported: ARM-based systems (e.g., Apple Silicon/M1/M2)

## 🔧 Features

- 🧠 Intent parsing with Rasa and Duckling
- 🗣️ Voice command support using OpenAI Whisper
- 🧾 Excel transaction management via `openpyxl`
- 🖼️ Receipt image generation with `Pillow`
- 🖥️ Desktop GUI built using PyQt5
- 🐳 Dockerized deployment
- ✅ CI integration with GitHub Actions

---

## 🚀 Quick Start
```bash
git clone https://github.com/YazRaso/calcite.git
cd Calcite/bot/actions
pip install -r requirements_core.txt
chmod u+x ./start.sh
./start.sh
```

## 😄 Welcome to Calcite
Upload your name and signature (displayed on receipts)

## 🛝 Play around
Select a file to work on or use the provided blank spreadsheet "TestBook.xlsx"
Go ahead, try to add and delete a few transactions, generate receipts!




