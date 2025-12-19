# ChromaDB Cloud Setup Guide

## Overview

ApexWealth now supports both **local ChromaDB** (default) and **ChromaDB Cloud**. When ChromaDB Cloud credentials are provided, the system automatically uses the cloud instance instead of local storage.

## Benefits of ChromaDB Cloud

- **Persistent storage**: Data stored in the cloud, accessible from anywhere
- **Scalability**: Handle larger knowledge bases
- **Backup**: Automatic backups and data redundancy
- **Multi-device access**: Access the same knowledge base from different machines

## Setup Instructions

### Option 1: Set Environment Variables (Recommended for Production)

**Windows PowerShell (Current Session):**
```powershell
$env:CHROMA_API_KEY="ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy"
$env:CHROMA_TENANT="ca9ef9e7-c73f-48e4-ad67-e58f1f185635"
$env:CHROMA_DATABASE="ApexWealth"
```

**Windows PowerShell (Permanent - User Level):**
```powershell
[System.Environment]::SetEnvironmentVariable('CHROMA_API_KEY', 'ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy', 'User')
[System.Environment]::SetEnvironmentVariable('CHROMA_TENANT', 'ca9ef9e7-c73f-48e4-ad67-e58f1f185635', 'User')
[System.Environment]::SetEnvironmentVariable('CHROMA_DATABASE', 'ApexWealth', 'User')
```

**Windows Command Prompt:**
```cmd
setx CHROMA_API_KEY "ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy"
setx CHROMA_TENANT "ca9ef9e7-c73f-48e4-ad67-e58f1f185635"
setx CHROMA_DATABASE "ApexWealth"
```

**Linux/Mac:**
```bash
export CHROMA_API_KEY="ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy"
export CHROMA_TENANT="ca9ef9e7-c73f-48e4-ad67-e58f1f185635"
export CHROMA_DATABASE="ApexWealth"
```

### Option 2: Create .env File (For Development)

Create a `.env` file in the project root:

```env
CHROMA_API_KEY=ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy
CHROMA_TENANT=ca9ef9e7-c73f-48e4-ad67-e58f1f185635
CHROMA_DATABASE=ApexWealth
```

**Note:** Make sure the `.env` file is in UTF-8 encoding (not UTF-16) to avoid encoding errors.

## Verification

To verify ChromaDB Cloud is connected:

```python
from vectordb.chroma_client import get_vectordb

vdb = get_vectordb()
print(f"Using ChromaDB Cloud: {vdb.is_cloud}")
```

Or run the populate script - it will automatically use ChromaDB Cloud if credentials are set:

```bash
python apex-wealth-agents/scripts/populate_knowledge.py
```

## Switching Between Local and Cloud

- **To use ChromaDB Cloud**: Set all three environment variables (CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE)
- **To use Local ChromaDB**: Unset or don't set these environment variables

The system automatically detects which mode to use based on the presence of these environment variables.

## Current Configuration

Your ChromaDB Cloud credentials:
- **API Key**: `ck-C34VNB178WL775dSxT3B69NX9gTWD6JVsTd6UiC7ARVy`
- **Tenant**: `ca9ef9e7-c73f-48e4-ad67-e58f1f185635`
- **Database**: `ApexWealth`

## Troubleshooting

### Connection Errors

1. **Verify credentials are set:**
   ```powershell
   echo $env:CHROMA_API_KEY
   echo $env:CHROMA_TENANT
   echo $env:CHROMA_DATABASE
   ```

2. **Check network connectivity** to `api.trychroma.com`

3. **Verify credentials** are correct in your ChromaDB Cloud dashboard

### Encoding Errors with .env File

If you get encoding errors with `.env` file:
- Ensure the file is saved as UTF-8 (not UTF-16)
- Or use environment variables instead of `.env` file

### Fallback to Local

If ChromaDB Cloud connection fails, the system will raise an error. To use local storage instead, simply unset the environment variables.

## Security Notes

- **Never commit** `.env` files or API keys to version control
- The `.env` file is already in `.gitignore`
- Use environment variables for production deployments
- Rotate API keys regularly for security

