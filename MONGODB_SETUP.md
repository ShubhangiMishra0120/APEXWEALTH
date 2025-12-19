# MongoDB Setup Guide for ApexWealth

## Overview

ApexWealth now supports MongoDB for storing user profiles and personalization data. The system automatically falls back to file-based storage if MongoDB is not available.

## Installation

### 1. Install MongoDB

**Windows:**
1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. MongoDB will be installed as a Windows service by default

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Install Python Dependencies

```powershell
pip install pymongo motor
```

Or install all requirements:
```powershell
pip install -r requirements.txt
```

## Configuration

### Option 1: Local MongoDB (Default)

If MongoDB is running locally on the default port (27017), no configuration is needed. The system will automatically connect to:
```
mongodb://localhost:27017/
```

### Option 2: MongoDB Atlas (Cloud)

1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a cluster and get your connection string
3. Set environment variable:

**Windows PowerShell:**
```powershell
$env:MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
```

**Windows Command Prompt:**
```cmd
setx MONGODB_URI "mongodb+srv://username:password@cluster.mongodb.net/"
```

**Linux/Mac:**
```bash
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

### Option 3: Custom MongoDB Connection

Set the `MONGODB_URI` environment variable to your MongoDB connection string:
```
MONGODB_URI=mongodb://user:password@host:port/
```

## Database Structure

MongoDB will create the following collections in the `apexwealth` database:

### Collections

1. **user_profiles**
   - Stores user profile information
   - Fields: `user_id`, `name`, `currency`, `goals`, `risk_preference`, `pay_cycle`, `budget_priorities`, `advice_tone`, `created_at`, `updated_at`

2. **user_personalization**
   - Stores CSV upload metadata
   - Fields: `user_id`, `metadata` (transaction stats, date ranges, categories), `upload_date`, `updated_at`

3. **user_models**
   - Stores model training information
   - Fields: `user_id`, `model_info` (accuracy, training samples, feature info), `trained_at`, `updated_at`

## API Endpoints

### User Profile Management

- `POST /profile/create` - Create or update user profile
- `GET /profile/{user_id}` - Get user profile
- `PUT /profile/{user_id}` - Update user profile
- `DELETE /profile/{user_id}` - Delete user profile
- `GET /profile/list` - List all user profiles

### Database Status

- `GET /database/status` - Check MongoDB connection status

## Usage Examples

### Create User Profile

```python
import requests

profile_data = {
    "name": "John Doe",
    "currency": "INR",
    "goals": ["emergency fund", "retirement"],
    "risk_preference": "moderate",
    "pay_cycle": "monthly",
    "budget_priorities": ["Rent", "Groceries"],
    "advice_tone": "warm, practical"
}

response = requests.post(
    "http://localhost:8000/profile/create",
    data={
        "user_id": "user123",
        "profile_data": json.dumps(profile_data)
    }
)
```

### Get User Profile

```python
response = requests.get("http://localhost:8000/profile/user123")
profile = response.json()
```

### Check Database Status

```python
response = requests.get("http://localhost:8000/database/status")
status = response.json()
# Returns: {"mongodb_connected": true, "database_name": "apexwealth", "status": "connected"}
```

## Fallback Behavior

If MongoDB is not available or not connected:
- The system automatically falls back to file-based storage
- User profiles are stored in `apex-wealth-agents/state/profile.json`
- Personalization data is stored in `apex-wealth-agents/state/user_data/`
- All functionality continues to work without MongoDB

## Verification

1. Start your MongoDB server
2. Start the ApexWealth application
3. Check the console for: `✅ Connected to MongoDB: apexwealth`
4. Visit http://localhost:8000/database/status to verify connection

## Troubleshooting

### MongoDB Not Connecting

1. **Check if MongoDB is running:**
   ```powershell
   # Windows
   Get-Service MongoDB
   
   # Linux/Mac
   sudo systemctl status mongodb
   ```

2. **Check connection string:**
   - Verify `MONGODB_URI` environment variable is set correctly
   - For Atlas, ensure your IP is whitelisted

3. **Check firewall:**
   - Ensure port 27017 is open (for local MongoDB)

4. **Check logs:**
   - Look for MongoDB connection errors in the console
   - The system will show: `⚠️  MongoDB connection failed: ...`

### Import Errors

If you see `ImportError: No module named 'pymongo'`:
```powershell
pip install pymongo motor
```

## Migration from File-Based Storage

The system automatically migrates data:
- When MongoDB is available, new data is stored in MongoDB
- Existing file-based data continues to work
- You can manually migrate by:
  1. Reading from file-based storage
  2. Creating profiles via API endpoints
  3. Uploading CSV data again (will save to MongoDB)

## Production Recommendations

1. **Use MongoDB Atlas** for production deployments
2. **Enable authentication** in MongoDB
3. **Use connection pooling** (already implemented)
4. **Set up backups** for MongoDB
5. **Monitor connection health** using `/database/status` endpoint
6. **Use environment variables** for connection strings (never hardcode)

## Next Steps

1. Install MongoDB
2. Install dependencies: `pip install -r requirements.txt`
3. Set `MONGODB_URI` if using remote MongoDB
4. Start the application
5. Verify connection at http://localhost:8000/database/status

