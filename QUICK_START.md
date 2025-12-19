# Quick Start Guide - ApexWealth

## 🚀 Running the Project

### Step 1: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

### Step 2: Start the Server

**Option A: Using the startup script (Recommended)**
```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth"
python apex-wealth-agents\start_server.py
```

**Option B: Using uvicorn directly**
```powershell
cd "C:\Users\Anshita bathla\OneDrive\Documents\Desktop\ApexWealth"
python -m uvicorn --app-dir apex-wealth-agents app.main:app --reload --port 8000
```

### Step 3: Access the Application

Once the server starts, you'll see:
```
🚀 Starting Apex Wealth server...
📍 Landing page: http://localhost:8000
💬 Chat interface: http://localhost:8000/ui
📊 API docs: http://localhost:8000/docs
🔧 Health check: http://localhost:8000/health
```

**Open in your browser:**
- **Chat Interface**: http://localhost:8000/ui
- **Landing Page**: http://localhost:8000/landing
- **API Documentation**: http://localhost:8000/docs

### Step 4: Using Personalization Features

1. **Click the "Personalize" button** in the top-right corner of the chat interface
2. **Upload your CSV file** with financial data (must have `date` and `amount` columns)
3. **Train your personalized model** by clicking "Train Model"
4. **Start chatting** - your financial analysis will now be personalized!

### 📋 CSV Format Requirements

Your CSV file should have at least these columns:
- **date** (or Date, DATE, ts, timestamp) - Transaction date
- **amount** (or Amount, AMOUNT, monthly_expense_total, expense) - Transaction amount
- **category** (optional) - Transaction category

Example CSV:
```csv
date,amount,category
2024-01-15,1500.00,Groceries
2024-01-16,2500.00,Rent
2024-01-17,500.00,Utilities
```

### 🛑 Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.

---

## 🔧 Troubleshooting

### Port Already in Use
If port 8000 is busy, use a different port:
```powershell
python -m uvicorn --app-dir apex-wealth-agents app.main:app --reload --port 8001
```

### Dependencies Not Installed
```powershell
pip install -r requirements.txt
```

### Import Errors
Make sure you're in the project root directory and the virtual environment is activated.

---

## 📚 Additional Resources

- Full documentation: See `HOW_TO_RUN.md`
- API endpoints: Visit http://localhost:8000/docs
- Project structure: See `README.md`

