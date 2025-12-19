## Apex Advisor

A Gemini-like personal finance advisor with three agents:
- Expense Categorization
- Budget Monitoring
- Cash Flow Prediction

### Setup

```
pip install -r requirements.txt
```

### Run the Web UI (FreeLLM by default)

1. Set env vars (Windows PowerShell):
```
setx LLM_PROVIDER freellm
setx LLM_MODEL freellm-default
```
2. Start server:
```
venv\Scripts\python.exe -m uvicorn --app-dir apex-wealth-agents app.main:app --reload --port 8000
```
3. Open `http://localhost:8000/ui`.

### Run the Interactive CLI

```
venv\Scripts\python.exe apex-wealth-agents\run_cli.py
```
Type your question (e.g., "What’s my budget status?") and the orchestrator will plan tool calls.

4. **Working Video of Project on Drive Link**
https://drive.google.com/file/d/1SPrxz-ksO5VLhUr0_Bs6TDGdAAitf8IG/view?usp=drive_link
