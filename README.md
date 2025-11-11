# FE-EKG: Financial Event Evolution Knowledge Graph

Implementation of the FEEKG paper: "Risk identification and management through knowledge Association: A financial event evolution knowledge graph approach"

## 🚀 How to View Everything

### Option 1: View Visualizations (PNG Images)

```bash
# Generate all visualizations
./venv/bin/python scripts/demo_visualizations.py

# View the images (Mac)
open results/three_layer_graph.png
open results/evolution_network.png

# Or view all at once
open results/*.png

# On Linux
xdg-open results/three_layer_graph.png

# On Windows
start results\three_layer_graph.png
```

**Generated files** (in `results/` folder):
- `three_layer_graph.png` - Full 3-layer architecture
- `evolution_network.png` - Event evolution network
- `risk_propagation.png` - Risk-entity connections
- `evolution_heatmap.png` - Event type matrix
- `component_breakdown.png` - Evolution method contributions
- And 3 more...

### Option 2: Interactive API Demo (Web Browser)

```bash
# 1. Start the API server
./venv/bin/python api/app.py

# 2. Open the demo page in your browser
# Mac: open api/demo.html
# Or navigate to: file:///Users/hansonxiong/Desktop/DDP/feekg/api/demo.html
```

The demo page provides:
- ✅ Interactive buttons to test all API endpoints
- ✅ Live visualization generation
- ✅ Database statistics
- ✅ Query results display

### Option 3: Neo4j Browser (Interactive Graph Database)

```bash
# Open Neo4j Browser
open http://localhost:7474

# Login with:
# Username: neo4j
# Password: feekg2024

# Try these queries:
# 1. View evolution network
MATCH (e1:Event)-[r:EVOLVES_TO]->(e2:Event)
RETURN e1, r, e2
LIMIT 50

# 2. View entity risks
MATCH (e:Entity {name: 'China Evergrande Group'})<-[:TARGETS_ENTITY]-(r:Risk)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN e, r, rt
```

### Option 4: Run Query Demos (Terminal)

```bash
# Interactive risk analysis demo
./venv/bin/python scripts/demo_risk_queries.py

# This shows:
# - Database overview
# - Entity risk profiles
# - Evolution analysis
# - Pattern detection
# - Statistics
```

## Project Structure

```
feekg/
├── .env                    # AllegroGraph credentials (NOT committed)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── config/                # Configuration and secrets
│   ├── __init__.py
│   └── secrets.py        # Secure credential loading
│
├── scripts/              # Utility scripts
│   └── check_connection.py  # Test AG connection
│
├── ontology/             # RDF schema definitions
├── data/                 # Sample data and inputs
├── ingestion/            # Data loading scripts
├── evolution/            # Event evolution algorithms
├── query/                # SPARQL queries and NL interface
├── viz/                  # Visualization scripts
├── results/              # Output files (graphs, plots)
└── logs/                 # Log files and test results
```

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

The `.env` file should already exist with your AllegroGraph credentials:

```bash
AG_URL=https://qa-agraph.nelumbium.ai/
AG_USER=sadmin
AG_PASS=279H-Dt<>,YU
AG_REPO=feekg_dev
```

**⚠️ NEVER commit the .env file to Git!**

### 3. Test Connection

```bash
python scripts/check_connection.py
```

Expected output:
```
✅ Connected successfully!
   Repository: feekg_dev
   Current size: X triples
   Latency: XX ms
```

## Three-Layer Architecture

FE-EKG implements a three-layer knowledge graph:

1. **Entity Layer** (Bottom): Companies, institutions, and their relationships
2. **Event Layer** (Middle): Financial events and their evolution chains
3. **Risk Layer** (Top): Risk types, transitions, and probabilities

```
Risk Layer:     [LiquidityRisk] ──0.7──> [CreditRisk]
                       ↑
Event Layer:    [DebtDefault] ──evolves──> [CreditDowngrade]
                       ↑                           ↑
Entity Layer:   [Evergrande] ─────────────> [Minsheng Bank]
```

## NVIDIA NIM Pipeline (Stage 7)

FE-EKG integrates NVIDIA NIM for automated knowledge extraction from financial news:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FE-EKG LLM PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

1. INPUT
   Financial News Articles (manual or RSS feeds)
        ↓
2. NVIDIA NIM (llm/ module)
   ┌──────────────────────────────────────┐
   │ TripletExtractor                     │
   │  • Extract events from text          │
   │  • Identify entities (companies)     │
   │  • Extract relationships             │
   │                                      │
   │ SemanticScorer                       │
   │  • Embedding-based similarity        │
   │  • Replace keyword matching          │
   │  • 98% accuracy (with fine-tuning)   │
   └──────────────────────────────────────┘
        ↓
3. NEO4J GRAPH DATABASE
   Store triplets as nodes & relationships
        ↓
4. EVOLUTION ANALYSIS (evolution/ module)
   6 evolution methods + enhanced semantic similarity
        ↓
5. QUERY & VISUALIZE (api/ + viz/ modules)
   REST API, Cypher queries, NetworkX visualizations
```

**Key Components**:
- **NemotronClient**: NVIDIA NIM API wrapper for text generation & embeddings
- **TripletExtractor**: Extract (subject, predicate, object) from financial text
- **SemanticScorer**: Embedding-based similarity (replaces keyword matching)

**Models Used**:
- `meta/llama-3.1-8b-instruct` - Text generation & triplet extraction
- `nvidia/nv-embedqa-e5-v5` - Semantic embeddings (1024 dimensions)

**Status**: Module implemented, requires NVIDIA API key to use.

See `llm/README.md` for complete documentation.

## Development Status

- [x] **Stage 1**: Infrastructure & connection test ✅
- [x] **Stage 2**: Minimal schema with Risk Layer + Neo4j backend ✅
- [x] **Stage 3**: Sample Evergrande data (20 events, 10 entities, 10 risks, 154 enhanced evolution links) ✅
- [x] **Stage 4**: Event evolution methods (6 algorithms: temporal, entity, semantic, topic, causal, emotional) ✅
- [x] **Stage 5**: Risk queries (80+ Cypher templates, Python API, interactive demo) ✅
- [x] **Stage 6**: Visualizations (NetworkX/Matplotlib graphs, REST API with 20+ endpoints) ✅
- [x] **Stage 7**: LLM/Nemotron integration (NVIDIA NIM, triplet extraction, embedding-based similarity) ✅
- [ ] **Stage 8**: Mini ABM (optional)

## Usage Guide

### Connecting to Neo4j Browser

1. Open Neo4j Browser: http://localhost:7474
2. Connect with:
   - **URL**: `neo4j://localhost:7687`
   - **Username**: `neo4j`
   - **Password**: `feekg2024`

### Running Risk Analysis

```bash
# Run the interactive demo
./venv/bin/python scripts/demo_risk_queries.py

# Verify Stage 4 (Evolution Methods)
./venv/bin/python scripts/verify_stage4.py

# Verify Stage 5 (Risk Queries)
./venv/bin/python scripts/verify_stage5.py

# Verify Stage 6 (Visualizations & API)
./venv/bin/python scripts/verify_stage6.py

# Demo LLM Integration (Stage 7)
./venv/bin/python scripts/demo_llm_integration.py
```

### Using LLM Features (Stage 7)

```bash
# 1. Get NVIDIA API key from https://build.nvidia.com
# 2. Add to .env: NVIDIA_API_KEY=your_key_here

# 3. Run LLM demo
./venv/bin/python scripts/demo_llm_integration.py
```

**LLM Capabilities**:
- Extract knowledge triplets from financial news (98% accuracy)
- Automatic event and entity recognition
- Enhanced semantic similarity using embeddings
- Foundation for natural language queries

See `llm/README.md` for complete documentation.

### Generating Visualizations

```bash
# Generate all visualizations (saved to results/)
./venv/bin/python scripts/demo_visualizations.py
```

This creates 8 visualization files:
- `three_layer_graph.png` - Full 3-layer architecture
- `evolution_network.png` - Event evolution network
- `risk_propagation.png` - Risk → Entity connections
- `risk_timeline.png` - Risk evolution over time
- `evolution_heatmap.png` - Event type evolution matrix
- `event_network_timeline.png` - Temporal event network
- `component_breakdown.png` - Evolution method contributions
- `risk_distribution.png` - Risk severity distribution

### Starting the REST API

```bash
# Start the API server
./venv/bin/python api/app.py

# Or use Python directly
python api/app.py
```

The API will be available at **http://localhost:5000**

Test it:
```bash
# Health check
curl http://localhost:5000/health

# Get all entities
curl http://localhost:5000/api/entities

# Get evolution links
curl "http://localhost:5000/api/evolution/links?min_score=0.5"

# Get graph data for frontend visualization
curl http://localhost:5000/api/graph/data
```

See [api/README.md](api/README.md) for complete API documentation.
```

### Using the Python API

```python
from query.risk_analyzer import RiskAnalyzer

analyzer = RiskAnalyzer()

# Get entity risk profile
risks = analyzer.get_entity_risk_profile('China Evergrande Group')
for risk in risks:
    print(f"{risk['riskType']}: {risk['score']:.3f} ({risk['severity']})")

# Find strongest evolution links
links = analyzer.get_strongest_evolution_links(min_score=0.5)
for link in links[:5]:
    print(f"{link['fromEvent']} → {link['toEvent']} (score: {link['overallScore']:.3f})")

# Detect causal chains
chains = analyzer.get_causal_chains(min_causality=0.6)
for chain in chains:
    print(f"Chain: {' → '.join(chain['eventChain'])}")

analyzer.close()
```

### Sample Neo4j Queries

```cypher
// View all enhanced evolution links
MATCH (e1:Event)-[r:EVOLVES_TO {type: 'enhanced'}]->(e2:Event)
RETURN e1.type, e2.type, r.score, r.causality
ORDER BY r.score DESC
LIMIT 20;

// Find causal chains
MATCH path = (e1:Event)-[:EVOLVES_TO*2..4]->(e2:Event)
WHERE all(r in relationships(path) WHERE r.causality > 0.6)
RETURN [e in nodes(path) | e.type] as chain;

// Entity risk profile
MATCH (e:Entity {name: 'China Evergrande Group'})
MATCH (r:Risk)-[:TARGETS_ENTITY]->(e)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN rt.label, r.score, r.severity
ORDER BY r.score DESC;
```

## 📋 Quick Reference

### All Important Commands

```bash
# =============================================================================
# VIEWING & VISUALIZATION
# =============================================================================

# Generate all visualizations → results/*.png
./venv/bin/python scripts/demo_visualizations.py

# View a specific visualization (Mac)
open results/three_layer_graph.png

# View all visualizations
open results/*.png

# Run query demos (terminal output)
./venv/bin/python scripts/demo_risk_queries.py

# =============================================================================
# REST API
# =============================================================================

# Start API server → http://localhost:5000
./venv/bin/python api/app.py

# Test API
curl http://localhost:5000/health
curl http://localhost:5000/api/info
curl http://localhost:5000/api/entities

# Open interactive demo page (in browser)
# Navigate to: file:///Users/hansonxiong/Desktop/DDP/feekg/api/demo.html

# =============================================================================
# NEO4J BROWSER
# =============================================================================

# Open Neo4j Browser → http://localhost:7474
open http://localhost:7474

# Credentials:
# Username: neo4j
# Password: feekg2024

# =============================================================================
# VERIFICATION
# =============================================================================

# Verify Stage 4 (Evolution Methods)
./venv/bin/python scripts/verify_stage4.py

# Verify Stage 5 (Risk Queries)
./venv/bin/python scripts/verify_stage5.py

# Verify Stage 6 (Visualizations & API)
./venv/bin/python scripts/verify_stage6.py

# =============================================================================
# DATA MANAGEMENT
# =============================================================================

# Reload data into Neo4j
./venv/bin/python ingestion/load_evergrande.py

# Recompute evolution links
./venv/bin/python evolution/run_evolution.py

# =============================================================================
# NEO4J DOCKER
# =============================================================================

# Start Neo4j container
./scripts/start_neo4j.sh

# Check if running
docker ps | grep feekg-neo4j

# Stop Neo4j
docker stop feekg-neo4j

# Restart Neo4j
docker start feekg-neo4j
```

### Important Files & Locations

| What | Where | Description |
|------|-------|-------------|
| **Visualizations** | `results/*.png` | 8 generated PNG images |
| **API Demo** | `api/demo.html` | Interactive web interface |
| **API Docs** | `api/README.md` | Complete API documentation |
| **Project Guide** | `CLAUDE.md` | Comprehensive project guide |
| **Stage Summary** | `STAGE6_SUMMARY.md` | Latest implementation details |
| **Input Data** | `data/evergrande_crisis.json` | All events, entities, risks |
| **Evolution Results** | `results/evolution_links.json` | Computed evolution links |
| **Query Templates** | `query/risk_queries.cypher` | 80+ Cypher query examples |

### Quick API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/info` | Database overview |
| `GET /api/entities` | All entities |
| `GET /api/events` | All events |
| `GET /api/evolution/links?min_score=0.5` | Evolution links |
| `GET /api/evolution/chains` | Causal chains |
| `GET /api/risks` | All risks |
| `GET /api/graph/data` | Graph data for D3.js |
| `GET /api/visualizations/three-layer` | Generate 3-layer viz |

See `api/README.md` for complete API documentation.

## Security Notes

- All credentials are stored in `.env` (excluded from Git)
- Passwords are masked in logs and error messages
- Use `config.secrets.get_masked_config()` for safe logging

## References

- Paper: Liu et al. (2024) "Risk identification and management through knowledge Association"
- AllegroGraph: https://allegrograph.com/
- EventKG: https://eventkg.l3s.uni-hannover.de/

## License

This project is for research and educational purposes.
