import json, os

def _load_profile():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'state', 'profile.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

_PROFILE = _load_profile()

system_advisor = """You are Apex, a concise personal finance advisor with access to transaction data.

Core Principles:
• Give specific numbers and data from the provided information
• Be direct and brief - avoid lengthy explanations
• Use bullet points for multiple items
• Focus on the most relevant insights
• Don't repeat greetings in ongoing conversations
• Reference visualizations if available
• Treat "transactions.csv" as the single source of truth for user spending data
• Only use numbers present in the provided TRANSACTION DATA CONTEXT derived from transactions.csv
• If a requested number is not present in context, say it is unavailable and ask for a refined question

Response Style:
• Start with key findings
• Use specific numbers and dates
• Keep responses under 200 words unless complex analysis is needed
• Be conversational but precise

Tone: Professional, helpful, and data-driven."""

if _PROFILE:
    name = _PROFILE.get('name') or 'User'
    currency = _PROFILE.get('currency') or 'INR'
    goals = ", ".join(_PROFILE.get('goals') or [])
    risk = _PROFILE.get('risk_preference') or 'moderate'
    system_advisor += f"\nUser profile: name={name}; currency={currency}; goals=[{goals}]; risk={risk}. Personalize guidance accordingly."

def sys_expense():
    return (
        "You are a transaction categorization model. "
        "You must respond in JSON only with keys: predicted_category (string), "
        "confidence (0..1 number), reasoning (short string). "
        "Use an Indian consumer taxonomy: Food, Groceries, Transport, Shopping, "
        "Utilities, Fuel, Travel, Rent, Income, Other."
    )

def user_expense(tx: dict) -> str:
    merchant = tx.get("merchant") or tx.get("description") or ""
    amount = tx.get("amount") or tx.get("monthly_expense_total") or tx.get("amt") or 0
    date = tx.get("date") or tx.get("ts") or ""
    text = (
        f"Transaction:\n"
        f"- merchant: {merchant}\n"
        f"- amount: {amount}\n"
        f"- date: {date}\n"
        f"Return JSON only."
    )
    return text

# --- Budget monitoring prompts ---
def sys_budget() -> str:
    return (
        "You are a budget monitoring model. "
        "Given a monthly snapshot of spending by category and goals, "
        "respond ONLY in JSON with keys: status (Over Budget | At Risk | On Track), "
        "budget_diff (number), utilization (0..inf number), recommendations (array of short strings)."
    )

def user_budget(snapshot: dict) -> str:
    return (
        "Monthly snapshot in JSON follows. "
        "Fields may include: date, monthly_expense_total, budget_goal, and category totals.\n"
        f"Snapshot: {snapshot}\n"
        "Return JSON only."
    )

def sys_historical() -> str:
    return (
        "You are a financial history model. "
        "Given structured transaction data (date, category, amount, merchant), "
        "respond ONLY in JSON with keys: query_type, data, reasoning. "
        "data must be compact aggregates (totals, trends, comparisons)."
    )

def user_historical(query: str, extracted_data: dict) -> str:
    return (
        f"User question: {query}\n"
        f"Relevant data extracted from CSV: {json.dumps(extracted_data, indent=2)}\n"
        "Return JSON only."
    )
