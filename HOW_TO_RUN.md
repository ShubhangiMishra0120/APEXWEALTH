# How to Run Apex Wealth Project

## Project Overview

**Apex Wealth** is a personal finance advisor application with three main agents:
- **Expense Categorization**: Automatically categorizes transactions
- **Budget Monitoring**: Tracks spending against budget goals
- **Cash Flow Prediction**: Forecasts future cash flow

The project includes:
- A **Web UI** (FastAPI-based) with chat interface
- An **Interactive CLI** for command-line usage
- Transaction data analysis and visualization capabilities

---

## Prerequisites

1. **Python 3.10+** installed
2. **Virtual environment** (already created in `venv/`)
3. **Dependencies** installed (see Setup below)

---

## Setup Instructions

### 1. Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

If not already installed:
```powershell
pip install -r requirements.txt
```

### 3. Environment Variables (Optional)

The project uses **FreeLLM** by default (no API keys required). However, if you want to use other LLM providers:

**For FreeLLM (Default - No setup needed):**
- Already configured, no environment variables required

**For OpenRouter:**
```powershell
setx LLM_PROVIDER openrouter
setx OPENROUTER_API_KEY your_api_key_here
```

**For Gemini:**
```powershell
setx LLM_PROVIDER gemini
setx GEMINI_API_KEY your_api_key_here
```

---

## Running the Project

### Option 1: Web UI (Recommended)

Start the FastAPI server:

```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth"


```

Or using uvicorn directly:
```powershell
.\venv\Scripts\python.exe -m uvicorn --app-dir apex-wealth-agents app.main:app --reload --port 8000
```

**Access the application:**
- 🏠 **Landing Page**: http://localhost:8000/landing
- 💬 **Chat Interface**: http://localhost:8000/ui
- 📊 **API Documentation**: http://localhost:8000/docs
- 🔧 **Health Check**: http://localhost:8000/health

**To stop the server:** Press `Ctrl+C` in the terminal

---

### Option 2: Interactive CLI

Run the command-line interface:

```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth"
.\venv\Scripts\python.exe apex-wealth-agents\run_cli.py
```

**Usage:**
- Type your questions (e.g., "What's my budget status?", "Show me spending by category")
- Type `exit` or `quit` to close
- Press `Ctrl+C` to interrupt

---

## Project Structure

```
ApexWealth/
├── apex-wealth-agents/          # Main application directory
│   ├── app/                     # FastAPI application
│   │   ├── main.py             # Main FastAPI app with routes
│   │   ├── static/             # Web UI files (HTML)
│   │   └── tools/              # Analysis tools
│   │       ├── csv_tools.py    # CSV query tools
│   │       ├── enhanced_csv_tools.py
│   │       └── visualization.py
│   ├── data/
│   │   └── transactions.csv    # Transaction data (3002 rows)
│   ├── llm/                    # LLM client and utilities
│   ├── orchestrator.py         # Main chat orchestrator
│   ├── start_server.py         # Server startup script
│   └── run_cli.py              # CLI interface
├── requirements.txt            # Python dependencies
└── venv/                      # Virtual environment
```

---

## Available Features

### Chat Interface Capabilities

You can ask questions like:
- "What's my total spending this month?"
- "Show me spending by category"
- "Analyze my expenses for 2023"
- "What are my top merchants?"
- "Create a chart of monthly spending"
- "Compare spending between months"

### API Endpoints

- `POST /chat` - Chat with the advisor
- `GET /tools/spend_aggregate` - Get spending aggregates
- `GET /tools/top_merchants` - Get top merchants
- `GET /historical/years` - Get available years
- `GET /health` - Health check
- And more... (see `/docs` for full API)

---

## Troubleshooting

### Server won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)

### Import errors
- Ensure you're in the correct directory
- Activate the virtual environment
- Reinstall dependencies if needed

### Data not loading
- Check that `apex-wealth-agents/data/transactions.csv` exists
- Verify the file has data (should have 3002+ rows)

### LLM errors
- FreeLLM is used by default (no API key needed)
- If using other providers, ensure API keys are set correctly
- Check network connection

---

## Quick Start (One Command)

**For Web UI:**
```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth" ; .\venv\Scripts\python.exe apex-wealth-agents\start_server.py
```

**For CLI:**
```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth" ; .\venv\Scripts\python.exe apex-wealth-agents\run_cli.py
```

---

## Next Steps

1. Start the server and open http://localhost:8000/ui
2. Try asking questions about your transaction data
3. Explore the API documentation at http://localhost:8000/docs
4. Check out the visualization features for spending analysis

