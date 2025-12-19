# Quick MongoDB Atlas Setup

## Your Credentials (from MongoDB Atlas)

- **Username**: `anshita3781beai23_db_user`
- **Password**: `EKr6WyPoEuH4Az1Q`
- **IP Address**: `49.43.90.160` (already whitelisted ✅)

## Quick Setup (3 Steps)

### Step 1: Get Your Cluster URL

1. In MongoDB Atlas, click **"Choose a connection method"** in the modal
2. Select **"Connect your application"**
3. Copy the connection string shown (it will look like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/...
   ```
4. Note the cluster part: `cluster0.xxxxx` (this is your cluster URL)

### Step 2: Set Environment Variable

**Windows PowerShell (Current Session):**
```powershell
$env:MONGODB_URI = "mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority"
```
*(Replace `YOUR_CLUSTER` with your actual cluster URL from Step 1)*

**Windows PowerShell (Permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable('MONGODB_URI', 'mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority', 'User')
```

**Windows Command Prompt:**
```cmd
setx MONGODB_URI "mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority"
```

### Step 3: Test Connection

Start the application:
```powershell
python apex-wealth-agents\start_server.py
```

You should see: `✅ Connected to MongoDB: apexwealth`

Or check status:
```powershell
curl http://localhost:8000/database/status
```

## Example Connection String

Based on your setup, your connection string should look like this:
```
mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@cluster0.xxxxx.mongodb.net/apexwealth?retryWrites=true&w=majority
```

**Important**: Replace `cluster0.xxxxx` with your actual cluster URL from MongoDB Atlas!

## Troubleshooting

### "Connection failed"
- Make sure you replaced `YOUR_CLUSTER` with your actual cluster URL
- Verify your IP (49.43.90.160) is whitelisted in Network Access
- Check that the password has no extra spaces

### "Authentication failed"
- Double-check username: `anshita3781beai23_db_user`
- Double-check password: `EKr6WyPoEuH4Az1Q`
- Make sure the database user was created in Atlas

### "Timeout"
- Check your internet connection
- Verify firewall isn't blocking MongoDB
- Try the connection string in MongoDB Compass to test

## Next Steps

Once connected:
1. ✅ MongoDB is ready
2. Start using the API endpoints for user profiles
3. Upload CSV data for personalization
4. All user data will be stored in MongoDB!

