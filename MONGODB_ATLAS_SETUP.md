# MongoDB Atlas Setup for ApexWealth

## Quick Setup Using Your Credentials

Based on your MongoDB Atlas setup, here's how to configure the connection:

### Your Credentials:
- **Username**: `anshita3781beai23_db_user`
- **Password**: `EKr6WyPoEuH4Az1Q`
- **Cluster**: `ApexWealth` (you'll need to get the cluster URL from Atlas)
- **Database**: `apexwealth` (will be created automatically)

## Step 1: Get Your Connection String

1. In MongoDB Atlas, click **"Choose a connection method"** in the modal
2. Select **"Connect your application"**
3. Choose **"Python"** and version **"3.6 or later"**
4. Copy the connection string (it will look like):
   ```
   mongodb+srv://anshita3781beai23_db_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your password: `EKr6WyPoEuH4Az1Q`
6. Add the database name at the end: `/apexwealth`

**Final connection string should be:**
```
mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@cluster0.xxxxx.mongodb.net/apexwealth?retryWrites=true&w=majority
```
*(Replace `cluster0.xxxxx` with your actual cluster URL)*

## Step 2: Set Environment Variable

### Windows PowerShell:
```powershell
$env:MONGODB_URI = "mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority"
```

### Windows Command Prompt (Permanent):
```cmd
setx MONGODB_URI "mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority"
```

### Linux/Mac:
```bash
export MONGODB_URI="mongodb+srv://anshita3781beai23_db_user:EKr6WyPoEuH4Az1Q@YOUR_CLUSTER.mongodb.net/apexwealth?retryWrites=true&w=majority"
```

## Step 3: Verify Network Access

Make sure your IP address (49.43.90.160) is whitelisted in MongoDB Atlas:
1. Go to **Network Access** in MongoDB Atlas
2. Verify your IP is in the list
3. If not, click **"Add IP Address"** and add `49.43.90.160`

## Step 4: Test Connection

Start your application and check the connection:

```powershell
python apex-wealth-agents\start_server.py
```

Look for: `✅ Connected to MongoDB: apexwealth`

Or check via API:
```powershell
curl http://localhost:8000/database/status
```

## Alternative: Use Setup Script

I've created a setup script for you. Run:

```powershell
python setup_mongodb.py
```

This will guide you through the setup process.

## Important Notes

1. **Password Security**: Never commit your password to version control
2. **IP Whitelisting**: Your IP (49.43.90.160) is already added, but if you change networks, you'll need to add the new IP
3. **Database Name**: The database `apexwealth` will be created automatically on first connection
4. **Collections**: Will be created automatically when you first use the API

## Troubleshooting

### Connection Failed
- Check that your IP is whitelisted in Network Access
- Verify the connection string is correct
- Make sure you replaced `<password>` with your actual password
- Check that the cluster URL is correct (from Atlas connection modal)

### Authentication Failed
- Double-check username and password
- Make sure there are no extra spaces in the connection string
- Verify the database user was created successfully in Atlas

### Timeout Errors
- Check your internet connection
- Verify firewall isn't blocking MongoDB connections
- Try pinging your cluster URL

## Next Steps

Once connected:
1. Start the application
2. Create a user profile via API: `POST /profile/create`
3. Upload CSV data for personalization
4. Train personalized models

The system will automatically use MongoDB for all user data storage!

