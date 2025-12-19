# VectorDB Module for ApexWealth

This module implements semantic knowledge retrieval using Chroma VectorDB for financial advisory content.

## Overview

The VectorDB is used **only for semantic knowledge retrieval** - storing financial knowledge, strategies, market insights, and educational content. It does **NOT** store:
- Numeric portfolio data
- Transaction data
- Real-time asset values
- User balances
- User risk assessment results

These should be stored in a traditional database (Postgres/Mongo/Firestore).

## Architecture

### Components

1. **ChromaVectorDB** (`chroma_client.py`)
   - Manages Chroma database connections
   - Organizes knowledge by namespaces
   - Handles document storage and retrieval

2. **EmbeddingService** (`embedding_service.py`)
   - Converts text to embeddings
   - Supports OpenAI `text-embedding-3-large` (default)
   - Falls back to local models (sentence-transformers) if no API key

3. **KnowledgeStore** (`knowledge_store.py`)
   - Handles document chunking (300-800 tokens)
   - Manages knowledge storage and retrieval
   - Provides convenience methods for different knowledge types

### Namespaces

Knowledge is organized into namespaces:

- `/knowledge/general` - General financial knowledge and education
- `/knowledge/market_insights` - Market research and insights
- `/knowledge/strategies` - Investment strategies
- `/knowledge/risk_profiles` - Risk-profile-based guidance

## Workflow

```
User Query 
  → Parsing Agent (extracts intent)
  → Embedding (convert query to vector)
  → VectorDB Search (retrieve relevant knowledge)
  → Strategy Agent (generate recommendations)
  → Risk Agent (validate risk alignment)
  → Output Agent (format response)
```

## Usage

### Initial Setup

1. Install dependencies:
```bash
pip install chromadb sentence-transformers
```

**Note:** The system uses local embeddings (sentence-transformers) by default, which:
- Works offline (no API calls)
- No API key required
- Good quality for semantic search
- Aligns with FreeLLM usage

OpenAI embeddings are optional and only used if explicitly configured.

### Populate Knowledge Base

Run the population script to add sample knowledge:

```bash
python apex-wealth-agents/scripts/populate_knowledge.py
```

### Using in Code

```python
from vectordb.knowledge_store import get_knowledge_store

# Get knowledge store
knowledge_store = get_knowledge_store()

# Store a document
knowledge_store.store_document(
    content="Your financial knowledge content here...",
    title="Document Title",
    namespace="general"
)

# Retrieve knowledge
results = knowledge_store.retrieve_knowledge(
    query="What is SIP?",
    top_k=5
)

# Store market insight
knowledge_store.store_market_insight(
    content="Market analysis...",
    title="Market Update Q1 2024",
    date="2024-01-15"
)

# Store strategy
knowledge_store.store_strategy(
    content="Investment strategy details...",
    title="SIP Strategy",
    strategy_type="SIP",
    risk_level="moderate"
)
```

## Document Chunking

Documents are automatically chunked into 300-800 token segments:
- Chunks overlap by ~50 tokens for context preservation
- Chunks are split at paragraph boundaries when possible
- Each chunk includes metadata (title, source, chunk index)

## Embedding Models

### Local (Default)
- Model: `all-MiniLM-L6-v2` (sentence-transformers)
- No API key needed
- Works offline
- Good quality for semantic search
- Aligns with FreeLLM usage

### OpenAI (Optional)
- Model: `text-embedding-3-large`
- Requires: `OPENAI_API_KEY` environment variable
- Only used if explicitly configured

## Integration with Orchestrator

The orchestrator automatically uses VectorDB when:
1. User query requires knowledge retrieval (determined by Parsing Agent)
2. Query type is investment-related (investment_advice, portfolio_question, market_question)

For transaction analysis queries, the system uses the traditional CSV/DB approach.

## Best Practices

1. **Store Knowledge, Not Data**
   - ✅ Store: Strategies, market insights, educational content
   - ❌ Don't store: User portfolios, transaction data, real-time prices

2. **Chunk Appropriately**
   - Keep chunks between 300-800 tokens
   - Use meaningful boundaries (paragraphs, sections)
   - Maintain context with overlap

3. **Use Appropriate Namespaces**
   - `general`: General financial education
   - `market_insights`: Time-sensitive market information
   - `strategies`: Investment strategies and approaches
   - `risk_profiles`: Risk-based guidance

4. **Metadata Matters**
   - Include source, date, type in metadata
   - Helps with filtering and attribution
   - Improves retrieval quality

## Troubleshooting

### VectorDB not initializing
- Check that `chromadb` is installed: `pip install chromadb`
- Verify write permissions in the project directory
- Check for error messages in console

### Embedding errors
- If using OpenAI: Verify `OPENAI_API_KEY` is set
- If using local: Ensure `sentence-transformers` is installed
- Check network connection for API calls

### No results from search
- Ensure knowledge base is populated
- Try broader search terms
- Check namespace filtering

## Data Persistence

VectorDB data is stored in:
```
apex-wealth-agents/vectordb_data/
```

This directory is created automatically and persists across sessions.

