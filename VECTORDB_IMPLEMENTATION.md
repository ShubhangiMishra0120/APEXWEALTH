# VectorDB Implementation for ApexWealth

## Summary

This document describes the VectorDB implementation for semantic knowledge retrieval in the ApexWealth financial advisory system.

## Implementation Status

✅ **Completed Components:**

1. **VectorDB Infrastructure**
   - Chroma VectorDB client with namespace organization
   - Embedding service (OpenAI + local fallback)
   - Knowledge store with automatic chunking (300-800 tokens)

2. **Agent System**
   - Parsing Agent: Extracts query intent and requirements
   - Strategy Agent: Generates investment recommendations
   - Risk Agent: Validates risk alignment
   - Output Agent: Formats user-friendly responses

3. **Orchestrator Integration**
   - Workflow: Query → Parsing → Embedding → VectorDB → Strategy → Risk → Output
   - Automatic fallback to original workflow if VectorDB unavailable
   - Seamless integration with existing transaction analysis

4. **Knowledge Management**
   - Document chunking (300-800 tokens)
   - Namespace organization (general, market_insights, strategies, risk_profiles)
   - Sample knowledge population script

## Architecture

### Data Separation

**VectorDB Stores (Semantic Knowledge):**
- Market research summaries
- Investment strategy explanations
- Case-based portfolio decision examples
- Financial education content
- Risk-profile-based guidance notes

**Traditional DB Stores (Numeric Data):**
- User portfolios
- SIP/Investment plans
- Daily NAV/price data
- User risk assessment results
- Transaction logs and audit trails

### Workflow

```
User Query
    ↓
Parsing Agent (extracts intent, determines data needs)
    ↓
    ├─→ Requires Knowledge? → Embedding → VectorDB Search
    ├─→ Requires Transaction Data? → CSV/DB Query
    └─→ Requires Market Data? → Real-time API
    ↓
Strategy Agent (combines knowledge + data)
    ↓
Risk Agent (validates alignment)
    ↓
Output Agent (formats response)
    ↓
User Response
```

## File Structure

```
apex-wealth-agents/
├── vectordb/
│   ├── __init__.py
│   ├── chroma_client.py          # Chroma VectorDB client
│   ├── embedding_service.py      # Embedding generation
│   ├── knowledge_store.py        # Knowledge management
│   └── README.md                 # Detailed documentation
├── agents/
│   ├── __init__.py
│   ├── parsing_agent.py          # Query parsing
│   ├── strategy_agent.py         # Strategy generation
│   ├── risk_agent.py             # Risk assessment
│   └── output_agent.py           # Response formatting
├── orchestrator.py               # Main orchestrator (updated)
└── scripts/
    └── populate_knowledge.py     # Knowledge population utility
```

## Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `chromadb` - Vector database
- `sentence-transformers` - Local embeddings (default, no API key needed)

**Note:** The system uses local embeddings by default (sentence-transformers), which works offline and doesn't require any API keys. This aligns with using FreeLLM for the main LLM.

### 2. Populate Knowledge Base

```bash
python apex-wealth-agents/scripts/populate_knowledge.py
```

This adds sample knowledge:
- Market insights
- Investment strategies
- Risk profile guidance
- General financial education

### 3. Run the Application

The VectorDB workflow is automatically integrated. Just run the server:

```bash
python apex-wealth-agents/start_server.py
```

The system will:
- Use VectorDB for investment/strategy queries
- Use traditional DB/CSV for transaction analysis
- Automatically determine which approach to use

## Query Examples

### Investment Queries (Uses VectorDB)
- "What is a good SIP strategy?"
- "How should I invest based on my risk profile?"
- "Tell me about mutual funds"
- "What's the best asset allocation for my age?"

### Transaction Queries (Uses CSV/DB)
- "What's my spending this month?"
- "Show me category breakdown"
- "What are my top merchants?"

### Hybrid Queries (Uses Both)
- "Based on my spending patterns, what investment strategy should I follow?"
- "I spend ₹50,000/month, how should I invest the rest?"

## Configuration

### Embedding Model

Default: `all-MiniLM-L6-v2` (local, sentence-transformers) - **No API key required**

The system uses local embeddings by default, which:
- Works offline
- No API costs
- Good quality for semantic search
- Aligns with FreeLLM usage

To use OpenAI embeddings (optional), you would need to:
1. Set `OPENAI_API_KEY` environment variable
2. Modify `get_embedding_service()` to use OpenAI model

### Chunk Size

Default: 500 tokens (range: 300-800)

To change, modify `knowledge_store.py`:
```python
chunk_text(text, chunk_size=600, chunk_overlap=50)
```

### VectorDB Storage

**Local Storage (Default):**
- Location: `apex-wealth-agents/vectordb_data/`
- Used when ChromaDB Cloud credentials are not set

**ChromaDB Cloud (Optional):**
- Set environment variables: `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`
- Automatically used when all three are set
- See `CHROMADB_CLOUD_SETUP.md` for setup instructions

To change local storage location, modify `chroma_client.py`:
```python
ChromaVectorDB(persist_directory="/path/to/custom/location")
```

## Testing

### Test VectorDB Search

```python
from vectordb.knowledge_store import get_knowledge_store

knowledge_store = get_knowledge_store()
results = knowledge_store.retrieve_knowledge("SIP strategy", top_k=3)
print(results)
```

### Test Agent Workflow

```python
from orchestrator import chat

response = chat("What investment strategy should I follow?")
print(response)
```

## Troubleshooting

### VectorDB Not Working

1. Check installation: `pip list | grep chromadb`
2. Check permissions: Ensure write access to project directory
3. Check logs: Look for initialization errors

### Embedding Errors

1. **OpenAI errors**: Verify API key is set and valid
2. **Local embedding errors**: Install sentence-transformers: `pip install sentence-transformers`
3. **Network errors**: Check internet connection for API calls

### No Knowledge Retrieved

1. Ensure knowledge base is populated: Run `populate_knowledge.py`
2. Check query keywords: Use relevant financial terms
3. Verify namespace: Check if query matches stored knowledge type

## Future Enhancements

Potential improvements:
1. Real-time market data integration
2. User-specific knowledge personalization
3. Multi-language support
4. Advanced RAG techniques (reranking, query expansion)
5. Knowledge base versioning and updates
6. Integration with external financial APIs

## Compliance Notes

- VectorDB stores only general knowledge, not user-specific data
- User portfolios and transactions remain in secure databases
- All recommendations are generated, not stored
- Risk assessments are computed on-demand

## Support

For issues or questions:
1. Check `vectordb/README.md` for detailed documentation
2. Review error messages in console
3. Verify all dependencies are installed
4. Check environment variables are set correctly

