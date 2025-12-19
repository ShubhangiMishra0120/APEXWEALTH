from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os, importlib, httpx
import tempfile
import shutil
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from orchestrator import chat as chat_fn
try:
    from enhanced_orchestrator import process_historical_query  # optional, not required for /chat
except Exception:
    process_historical_query = None

app = FastAPI(title="Apex Advisor")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Serve minimal static UI (resolve absolute path)
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ChatReq(BaseModel):
    session_id: str
    message: str
    context: List[Dict[str, str]] = []
    user_id: Optional[str] = None

class CategorizeReq(BaseModel):
    user_id: str
    tx_ids: List[str] = []

@app.get("/")
def root():
    return RedirectResponse(url="/landing")

@app.get("/ui")
def ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/landing")
def landing():
    landing_path = os.path.join(STATIC_DIR, "landing.html")
    return FileResponse(landing_path)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat_api(req: ChatReq):
    try:
        response = chat_fn(req.message, req.context, user_id=req.user_id)
        if isinstance(response, dict):
            return response
        return {"answer": str(response), "status": "success", "type": "text"}
    except Exception as e:
        return {"answer": f"I apologize, but I encountered an error: {str(e)}", "status": "error", "type": "error"}

@app.get("/selftest")
def selftest():
    out = {}
    out["csv_exists"] = os.path.exists("data/transactions.csv")
    for m in ["run_expense_categorizer","run_budget_monitor","run_cashflow_predictor","llm.llm_client","llm.schemas","app.tools.categorize","app.tools.budget"]:
        try:
            importlib.import_module(m)
            out[f"import:{m}"] = True
        except Exception as e:
            out[f"import:{m}"] = f"ERR: {e}"
    prov = os.getenv("LLM_PROVIDER","openrouter")
    out["LLM_PROVIDER"] = prov
    if prov == "openrouter":
        out["OPENROUTER_KEY_set"] = bool(os.getenv("OPENROUTER_API_KEY"))
    if prov == "gemini":
        out["GEMINI_KEY_set"] = bool(os.getenv("GEMINI_API_KEY"))
    try:
        from run_budget_monitor import run as rb
        out["budget_smoke"] = rb()
    except Exception as e:
        out["budget_smoke"] = f"ERR: {e}"
    return out


# Flowise-compatible endpoints (minimal)
@app.post("/tools/categorize_txn")
def categorize_txn(req: CategorizeReq):
    from run_expense_categorizer import run as run_cat
    # For demo, ignore tx_ids and run on current CSV
    return run_cat(transactions_path="data/transactions.csv", use_llm=True)

@app.get("/reports/spend_mtd")
def spend_mtd(user_id: str = Query(...)):
    from app.tools.budget import run as budget_run
    return budget_run()

@app.get("/budgets")
def budgets(user_id: str = Query(...)):
    from app.tools.budget import DEFAULT_LIMITS
    return DEFAULT_LIMITS

@app.get("/series/daily_net_flow")
def daily_net_flow(user_id: str = Query(...), window: int = Query(365)):
    # Simple placeholder: return empty series for now (Flowise template stub)
    return []

@app.post("/models/forecast")
def forecast(series: Any):
    from run_cashflow_predictor import run as run_forecast
    return run_forecast()

@app.post("/tools/query_csv")
def http_query_csv(payload: Dict[str, Any]):
    from app.tools.csv_tools import query_csv
    sql = str(payload.get("sql") or "").strip()
    limit = int(payload.get("limit") or 1000)
    return query_csv(sql=sql, limit=limit)

@app.get("/tools/spend_aggregate")
def http_spend_aggregate(month: str | None = Query(None), group_by: str = Query("category")):
    from app.tools.csv_tools import spend_aggregate
    return spend_aggregate(month=month, group_by=group_by)

@app.get("/tools/top_merchants")
def http_top_merchants(month: str | None = Query(None), n: int = Query(10)):
    from app.tools.csv_tools import top_merchants
    return top_merchants(month=month, n=n)

@app.get("/tools/describe_csv")
def http_describe_csv():
    from app.tools.csv_tools import describe_csv
    return describe_csv()

@app.post("/historical/analyze")
def historical_analysis(req: ChatReq):
    """Dedicated endpoint for historical analysis with charts"""
    try:
        response = process_historical_query(req.message, req.context)
        return response
    except Exception as e:
        return {
            "answer": f"Error in historical analysis: {str(e)}",
            "status": "error",
            "type": "error"
        }

@app.get("/historical/years")
def get_available_years():
    """Get list of available years in the dataset"""
    try:
        from app.tools.enhanced_csv_tools import get_available_years
        years = get_available_years()
        return {"years": years, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/historical/year/{year}")
def get_year_data(year: int):
    """Get data for a specific year"""
    try:
        from app.tools.enhanced_csv_tools import extract_year_data
        data = extract_year_data(year)
        return data
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/historical/range/{start_year}/{end_year}")
def get_year_range_data(start_year: int, end_year: int):
    """Get data for a range of years"""
    try:
        from app.tools.enhanced_csv_tools import extract_year_range_data
        data = extract_year_range_data(start_year, end_year)
        return data
    except Exception as e:
        return {"error": str(e), "status": "error"}


# Personalization endpoints
@app.post("/personalization/upload")
async def upload_personal_data(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    overwrite: bool = Form(False)
):
    """
    Upload personal finance CSV data for personalization
    
    Args:
        file: CSV file with transaction data
        user_id: Unique user identifier
        overwrite: Whether to overwrite existing data
    """
    try:
        from app.tools.personalization import PersonalizationEngine
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            return {
                "success": False,
                "error": "File must be a CSV file"
            }
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Process CSV
            engine = PersonalizationEngine()
            result = engine.process_user_csv(tmp_path, user_id, overwrite=overwrite)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/personalization/train")
def train_personal_model(
    user_id: str = Form(...),
    retrain: bool = Form(False)
):
    """
    Train a personalized model for a user
    
    Args:
        user_id: Unique user identifier
        retrain: Whether to retrain if model already exists
    """
    try:
        from app.tools.personalization import PersonalizationEngine
        
        engine = PersonalizationEngine()
        result = engine.train_user_model(user_id, retrain=retrain)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/personalization/status/{user_id}")
def get_personalization_status(user_id: str):
    """
    Get personalization status for a user
    
    Args:
        user_id: Unique user identifier
    """
    try:
        from app.tools.personalization import PersonalizationEngine
        
        engine = PersonalizationEngine()
        
        # Get metadata
        metadata = engine.get_user_metadata(user_id)
        
        # Check if model exists
        model_path = engine.get_user_model_path(user_id)
        has_model = model_path is not None
        
        return {
            "user_id": user_id,
            "has_data": metadata is not None,
            "has_model": has_model,
            "metadata": metadata,
            "model_path": model_path if has_model else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/personalization/validate")
async def validate_csv(file: UploadFile = File(...)):
    """
    Validate CSV file structure before upload
    
    Args:
        file: CSV file to validate
    """
    try:
        from app.tools.personalization import PersonalizationEngine
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            engine = PersonalizationEngine()
            result = engine.validate_csv(tmp_path)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@app.get("/personalization/users")
def list_personalized_users():
    """List all users with personalized data"""
    try:
        from app.tools.personalization import PersonalizationEngine
        
        engine = PersonalizationEngine()
        users = engine.list_users()
        
        # Get status for each user
        user_statuses = []
        for user_id in users:
            metadata = engine.get_user_metadata(user_id)
            model_path = engine.get_user_model_path(user_id)
            user_statuses.append({
                "user_id": user_id,
                "has_model": model_path is not None,
                "metadata": metadata
            })
        
        return {
            "users": user_statuses,
            "count": len(users)
        }
    except Exception as e:
        return {
            "error": str(e),
            "users": []
        }


# User Profile Management Endpoints (MongoDB)
@app.post("/profile/create")
def create_user_profile(
    user_id: str = Form(...),
    profile_data: str = Form(...)  # JSON string
):
    """
    Create or update user profile in MongoDB
    
    Args:
        user_id: Unique user identifier
        profile_data: JSON string with profile data
    """
    try:
        from database.mongodb_service import get_mongodb_service
        
        mongodb = get_mongodb_service()
        if not mongodb.is_connected():
            return {
                "success": False,
                "error": "MongoDB not connected. Please check your MongoDB setup."
            }
        
        # Parse JSON profile data
        import json
        profile = json.loads(profile_data)
        
        result = mongodb.create_user_profile(user_id, profile)
        return result
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON in profile_data"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/profile/{user_id}")
def get_user_profile(user_id: str):
    """
    Get user profile from MongoDB
    
    Args:
        user_id: Unique user identifier
    """
    try:
        from database.mongodb_service import get_mongodb_service
        
        mongodb = get_mongodb_service()
        if not mongodb.is_connected():
            # Fallback to file-based profile
            import os
            import json
            profile_path = os.path.join("apex-wealth-agents", "state", "profile.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    return {"success": True, "profile": json.load(f), "source": "file"}
            return {"success": False, "error": "Profile not found"}
        
        profile = mongodb.get_user_profile(user_id)
        if profile:
            return {"success": True, "profile": profile, "source": "mongodb"}
        else:
            return {"success": False, "error": "Profile not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/profile/{user_id}")
def update_user_profile(
    user_id: str,
    updates: str = Form(...)  # JSON string
):
    """
    Update user profile fields
    
    Args:
        user_id: Unique user identifier
        updates: JSON string with fields to update
    """
    try:
        from database.mongodb_service import get_mongodb_service
        import json
        
        mongodb = get_mongodb_service()
        if not mongodb.is_connected():
            return {
                "success": False,
                "error": "MongoDB not connected"
            }
        
        update_data = json.loads(updates)
        result = mongodb.update_user_profile(user_id, update_data)
        return result
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON in updates"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/profile/{user_id}")
def delete_user_profile(user_id: str):
    """
    Delete user profile
    
    Args:
        user_id: Unique user identifier
    """
    try:
        from database.mongodb_service import get_mongodb_service
        
        mongodb = get_mongodb_service()
        if not mongodb.is_connected():
            return {
                "success": False,
                "error": "MongoDB not connected"
            }
        
        result = mongodb.delete_user_profile(user_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/profile/list")
def list_all_profiles():
    """List all user profiles"""
    try:
        from database.mongodb_service import get_mongodb_service
        
        mongodb = get_mongodb_service()
        if not mongodb.is_connected():
            return {
                "success": False,
                "error": "MongoDB not connected",
                "users": []
            }
        
        users = mongodb.list_all_users()
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "users": []}


@app.get("/database/status")
def database_status():
    """Check MongoDB connection status"""
    try:
        from database.mongodb_service import get_mongodb_service
        
        mongodb = get_mongodb_service()
        is_connected = mongodb.is_connected()
        
        return {
            "mongodb_connected": is_connected,
            "database_name": mongodb.database_name if is_connected else None,
            "status": "connected" if is_connected else "disconnected"
        }
    except Exception as e:
        return {
            "mongodb_connected": False,
            "status": "error",
            "error": str(e)
        }

