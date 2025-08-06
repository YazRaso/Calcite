# Calcite

> 🧮 Like Copilot, but for bookkeeping.  
> A local-first, voice-enabled desktop assistant that automates transactions and generates receipts.

**Calcite** is a production-grade desktop app that manages your financial records via natural language.  
It parses spoken or written commands like:  
`"Add a transaction for 5000 USD at rate 0.25 reference 4392 for today"`  
and updates your Excel file, generates a receipt image, and provides voice feedback — all processed locally.

---

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

### 1. Clone the repository

```bash
git clone https://github.com/YazRaso/calcite.git
cd .Calcite/bot/actions
pip install -r requirements_core.txt
chmod u+x ./start.sh
./start.sh
```




