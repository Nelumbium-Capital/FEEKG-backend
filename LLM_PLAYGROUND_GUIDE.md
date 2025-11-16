# AllegroGraph LLM Playground Guide for FE-EKG

## What is the LLM Playground?

AllegroGraph's **LLM Playground** allows you to query your knowledge graph using **natural language** instead of writing SPARQL queries.

### Example:
**Instead of writing SPARQL:**
```sparql
PREFIX feekg: <http://feekg.org/ontology#>
SELECT ?event ?date ?label
WHERE {
    ?event a feekg:Event .
    ?event feekg:severity "critical" .
    ?event feekg:date ?date .
    ?event rdfs:label ?label .
}
ORDER BY ?date
```

**You can ask in plain English:**
```
"What critical events happened in 2008?"
```

And the LLM **automatically generates and executes** the SPARQL for you!

---

## How It Works

```
┌─────────────────────────────────────────────┐
│  1. You ask in natural language             │
│     "Show me all bankruptcies in 2008"      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  2. LLM + Vector DB converts to SPARQL      │
│     SELECT ?event WHERE { ... }             │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  3. AllegroGraph executes SPARQL            │
│     Returns: [Event1, Event2, ...]          │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  4. Results displayed + SPARQL shown        │
│     (You can save good examples)            │
└─────────────────────────────────────────────┘
```

**Key Features:**
- Uses **OpenAI API** (you need an API key)
- Creates **Vector Database (VDB)** to learn your query patterns
- Uses **SHACL shapes** to understand your data structure
- **Improves over time** as you save good query examples

---

## Comparison: LLM Playground vs Traditional Approach

### Traditional SPARQL (Current Method)
✅ **Pros:**
- Full control over queries
- No API costs (free)
- Works offline
- Deterministic results
- Fast for repeated queries

❌ **Cons:**
- Requires learning SPARQL syntax
- Manual query writing
- Error-prone for complex queries
- Time-consuming for exploration

### LLM Playground (New Method)
✅ **Pros:**
- **No SPARQL knowledge needed**
- Natural language queries
- **Fast exploration** of data
- Learn SPARQL by seeing generated queries
- Interactive refinement
- Great for **ad-hoc analysis**

❌ **Cons:**
- **Requires OpenAI API key** (costs money)
- May generate incorrect queries initially
- Needs training with examples
- Slower than direct SPARQL (API latency)
- Requires internet connection

---

## When to Use Which?

| Use Case | Recommended Approach |
|----------|---------------------|
| **Exploration** (new dataset, trying ideas) | 🤖 **LLM Playground** |
| **Learning** (understanding your data) | 🤖 **LLM Playground** |
| **Production queries** (automated, repeated) | 📝 **Traditional SPARQL** |
| **Complex analysis** (joins, aggregations) | 📝 **Traditional SPARQL** |
| **Cost-sensitive** (no budget for API calls) | 📝 **Traditional SPARQL** |
| **Teaching others** (show SPARQL examples) | 🤖 **LLM Playground** → save as SPARQL |
| **Quick questions** ("What events in 2008?") | 🤖 **LLM Playground** |
| **Batch processing** (thousands of queries) | 📝 **Traditional SPARQL** |

---

## Setup: Enable LLM Playground for FEEKG

### Option 1: Use Existing `llm-playground-1`
Your repository `llm-playground-1` is already created! You can use it for testing.

### Option 2: Enable LLM Features in FEEKG Repository

**Step 1: Open FEEKG in AllegroGraph WebView**
1. Go to: https://qa-agraph.nelumbium.ai/catalogs/mycatalog/repositories/FEEKG
2. Click "Query" in left sidebar

**Step 2: Create Natural Language to SPARQL VDB**
1. In query editor, select **"Natural Language (NL) to SPARQL"** from the "New Query" dropdown
2. Click **"CREATE NLQ VDB & SHACL SHAPES"**
3. Choose embedder: **OpenAI**
4. Enter your **OpenAI API key**: `sk-...`

**Step 3: Test Natural Language Query**
1. In the prompt area, type: `"What events happened in September 2008?"`
2. Click **"Run NL Query"**
3. Review the generated SPARQL
4. Click **"Execute"** to see results

**Step 4: Save Good Examples**
- When a query works well, click **"Save to NLQ VDB"**
- This teaches the system your query patterns
- Future similar queries will be more accurate

---

## Example Queries for FEEKG

### Starting Simple:

**Natural Language:**
```
"How many events are in the database?"
```

**Natural Language:**
```
"Show me all entities"
```

**Natural Language:**
```
"What are the different event types?"
```

### Getting More Specific:

**Natural Language:**
```
"What critical events happened to Lehman Brothers?"
```

**Natural Language:**
```
"Show me all bankruptcies between 2007 and 2009"
```

**Natural Language:**
```
"Which entities had the most high-severity events?"
```

### Advanced Questions:

**Natural Language:**
```
"What risks were triggered by credit downgrades?"
```

**Natural Language:**
```
"Show me the timeline of events for Bank of America in 2008"
```

**Natural Language:**
```
"Which risk type is most common in the database?"
```

---

## Cost Considerations

### OpenAI API Pricing (approximate):
- **GPT-4**: ~$0.03 per query (for NL→SPARQL conversion)
- **Embeddings**: ~$0.0001 per query (for vector search)
- **Estimated cost**: $0.03 - $0.05 per natural language query

### Budget-Friendly Approach:
1. **Use LLM Playground for exploration** (10-20 queries)
2. **Save the generated SPARQL** queries you like
3. **Switch to traditional SPARQL** for repeated analysis
4. **Total cost**: ~$1-2 for initial exploration

---

## Hybrid Workflow (Recommended)

### Best of Both Worlds:

**Phase 1: Exploration (1-2 hours)**
- Use **LLM Playground** to explore data
- Ask 20-30 natural language questions
- Save all good SPARQL queries generated
- **Cost**: ~$1-2

**Phase 2: Refinement**
- Copy generated SPARQL to Python scripts
- Modify and optimize queries
- Add to `efficient_analyzer.py`

**Phase 3: Production**
- Use **traditional SPARQL** (free, fast)
- Run via Python scripts or web UI
- **Cost**: $0

### Example Workflow:

```bash
# Day 1: Exploration with LLM (in web UI)
Ask: "What critical events happened in September 2008?"
      → Get SPARQL, save it

Ask: "Which entities were involved in bankruptcies?"
      → Get SPARQL, save it

Ask: "Show me the risk distribution by type"
      → Get SPARQL, save it

# Day 2+: Use saved SPARQL in Python
./venv/bin/python scripts/efficient_analyzer.py <command>
```

---

## Setup Script for Testing

I'll create a script to test if LLM integration would work with your data:

```python
# Test if your OpenAI key works with AllegroGraph
from openai import OpenAI
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'sk-...'  # Your key here

client = OpenAI()

# Test embedding generation (needed for VDB)
response = client.embeddings.create(
    input="test query about financial events",
    model="text-embedding-ada-002"
)

print("✓ OpenAI API key works!")
print(f"✓ Embedding dimension: {len(response.data[0].embedding)}")
```

---

## Practical Setup Steps

### 1. Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. **Save it securely** (you won't see it again)

### 2. Add Budget Limit (Recommended)
1. In OpenAI dashboard, go to "Billing"
2. Set usage limit: $10/month
3. This prevents accidental high costs

### 3. Test in AllegroGraph
1. Open: https://qa-agraph.nelumbium.ai/catalogs/mycatalog/repositories/FEEKG
2. Create NLQ VDB (as described above)
3. Try a simple query: "Show me all entities"

### 4. Build Your Query Library
- Save 10-20 good query examples
- These become templates for future queries
- System learns your data model

---

## Decision Matrix

**Choose LLM Playground if:**
- ✅ You have OpenAI API key
- ✅ Budget for ~$1-2 for exploration
- ✅ Want to learn SPARQL by example
- ✅ Need quick answers without writing code
- ✅ Frequently ask new types of questions

**Stick with Traditional SPARQL if:**
- ✅ No OpenAI API key or budget
- ✅ Queries are repetitive
- ✅ Need offline access
- ✅ Already comfortable with SPARQL
- ✅ Building automated pipelines

---

## My Recommendation for Your FE-EKG Project

### 🎯 **Best Approach: Hybrid**

**Week 1: LLM Playground Exploration**
- Invest $2-5 in OpenAI credits
- Use LLM Playground to explore your 86,583 triples
- Ask 30-50 natural language questions
- Save all good SPARQL queries
- **Output**: Library of 20-30 SPARQL templates

**Week 2+: Traditional SPARQL**
- Use saved queries in `efficient_analyzer.py`
- Customize and optimize them
- Run unlimited free queries
- Build dashboards and visualizations

### 💰 **Total Investment**
- **Time**: 2-3 hours of exploration
- **Money**: $2-5 for OpenAI API
- **Value**: Permanent library of SPARQL queries + deep understanding of your data

---

## Quick Start Commands

### Check Your Current Repository
```bash
./venv/bin/python -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv('AG_URL').rstrip('/')
auth = (os.getenv('AG_USER'), os.getenv('AG_PASS'))

# List all repositories
response = requests.get(
    f'{base_url}/repositories',
    auth=auth
)

print('Available repositories:')
for line in response.text.split('\n'):
    if line.startswith('id:'):
        print(f'  - {line.split(\":\", 1)[1].strip()}')
"
```

### Test LLM Playground Repository
```bash
# Check if llm-playground-1 exists and its size
curl -u sadmin:$AG_PASS \
  https://qa-agraph.nelumbium.ai/repositories/llm-playground-1/size
```

---

## Next Steps

1. **Decide**: Do you have/want to use OpenAI API?
   - **Yes** → Set up LLM Playground in FEEKG
   - **No** → Continue with efficient_analyzer.py

2. **If Yes**:
   - Get OpenAI API key
   - Set $10 budget limit
   - Create NLQ VDB in FEEKG
   - Spend 2-3 hours exploring with natural language
   - Save good queries

3. **Either Way**:
   - Your current Python scripts work great!
   - You have full SPARQL access
   - No cost to continue current approach

---

## Conclusion

The LLM Playground is **excellent for exploration and learning**, but your **current Python approach is perfectly fine** for production use!

**My suggestion:**
- **If you have $2-5 to spare**: Try LLM Playground for 1-2 hours of exploration
- **If budget is tight**: Stick with your current `efficient_analyzer.py` scripts

Both approaches work with your 86,583 triples in FEEKG! 🎉

---

Last Updated: 2025-11-15
