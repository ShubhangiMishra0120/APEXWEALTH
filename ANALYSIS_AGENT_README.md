# Analysis Agent Documentation

## Overview

The Analysis Agent provides ML-based financial health analysis with visualizations. It integrates seamlessly with the existing ApexWealth agent workflow.

## Features

1. **ML-Based Financial Health Prediction**
   - Uses trained model (`financial_model.pkl`) if available
   - Falls back to rule-based analysis if model not found
   - Predicts: "Good", "At Risk", or "Bad"

2. **Financial Metrics Calculation**
   - Income vs Expenses
   - Surplus calculation
   - Savings goal gap analysis
   - Category-wise expense breakdown

3. **Visualizations**
   - Bar chart: Financial overview (Income, Expenses, Savings Goal, Surplus)
   - Comparison bar chart: Current vs Suggested strategy (if strategy data provided)
   - Pie chart: Expense breakdown by category

## Integration

The Analysis Agent is automatically integrated into the orchestrator workflow:

```
User Query → Parsing Agent → Transaction Data → Analysis Agent → Output
```

### When It's Used

The Analysis Agent is triggered when:
- Query requires transaction data (`requires_transaction_data = True`)
- Analysis Agent is initialized (model may or may not exist)

### Data Flow

1. **Transaction Summary** extracted from CSV/DB
2. **User Profile** loaded from `state/profile.json` (for income/savings goals)
3. **Financial Data** extracted and structured
4. **Analysis** performed (ML or rule-based)
5. **Visualizations** generated
6. **Results** added to response

## Model Requirements

### ML Model Format

The model should be a scikit-learn-compatible model saved with `joblib`:
- Input features: `[income, total_expenses, savings_goal, surplus]`
- Output: One of `["Good", "At Risk", "Bad"]`

### Model Location

Default path: `apex-wealth-agents/state/models/financial_model.pkl`

To use a different path:
```python
from agents.analysis_agent import AnalysisAgent

agent = AnalysisAgent(model_path="/path/to/your/model.pkl")
```

### Fallback Behavior

If model is not found or fails to load:
- System uses rule-based prediction
- No errors thrown
- Analysis continues normally

## Usage Example

```python
from agents.analysis_agent import AnalysisAgent

# Initialize agent
agent = AnalysisAgent()

# Prepare financial data
financial_data = {
    "income": 50000,
    "savings_goal": 10000,
    "expenses": {
        "Rent": 15000,
        "Groceries": 8000,
        "Transport": 5000,
        "Utilities": 3000
    }
}

# Perform analysis
analysis = agent.analyze(financial_data)

# Access results
print(f"Financial Health: {analysis['financial_health']}")
print(f"Surplus: ₹{analysis['surplus']:,.0f}")
print(f"Insights: {analysis['insights']}")

# Visualizations are matplotlib figures
# analysis['bar_chart'] - bar chart figure
# analysis['pie_chart'] - pie chart figure
```

## Data Extraction from Transactions

The agent can extract financial data from transaction summaries:

```python
transaction_summary = {
    "monthly_spend": 30000,
    "category_breakdown": {
        "Groceries": 8000,
        "Transport": 5000,
        "Rent": 15000
    }
}

profile = {
    "monthly_income": 50000,
    "savings_goal": 10000
}

financial_data = agent.extract_financial_data_from_transactions(
    transaction_summary, profile
)
```

## Response Format

The analysis is added to the orchestrator response:

```json
{
    "answer": "...",
    "status": "success",
    "type": "strategy_with_analysis",
    "financial_analysis": {
        "income": 50000,
        "total_expenses": 31000,
        "surplus": 19000,
        "savings_goal": 10000,
        "extra_surplus": 9000,
        "financial_health": "Good",
        "insights": ["✅ Financial health is good..."],
        "bar_chart": <matplotlib.figure.Figure>,
        "pie_chart": <matplotlib.figure.Figure>
    }
}
```

## Visualizations

### Bar Chart
- Shows Income, Expenses, Savings Goal, and Surplus
- Supports comparison mode (Current vs Suggested)
- Dark background theme
- Amount labels on bars

### Pie Chart
- Expense breakdown by category
- Percentage labels
- Filters out zero values
- Dark background theme

## Configuration

### Model Path
Set custom model path in orchestrator initialization or use default.

### Visualization Style
Uses `dark_background` matplotlib style. To change:
```python
plt.style.use('your_style')
```

## Troubleshooting

### Model Not Found
- Check model path: `state/models/financial_model.pkl`
- System will use rule-based analysis automatically
- No action needed

### Import Errors
- Ensure `joblib` and `matplotlib` are installed
- Check matplotlib backend (uses 'Agg' for non-interactive)

### Visualization Issues
- Ensure matplotlib is properly installed
- Check that figures are being saved/returned correctly

## Integration with Existing System

The Analysis Agent:
- ✅ Works with existing transaction data tools
- ✅ Integrates with user profile system
- ✅ Compatible with VectorDB workflow
- ✅ Optional (gracefully handles missing model)
- ✅ Adds visualizations to response
- ✅ Follows existing agent patterns

## Future Enhancements

Potential improvements:
- Support for multiple model types
- Real-time model updates
- Custom visualization themes
- Export visualizations to files
- Historical trend analysis

