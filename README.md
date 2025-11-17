# FE-EKG: Financial Event Evolution Knowledge Graph

Implementation of the FEEKG paper: "Risk identification and management through knowledge Association: A financial event evolution knowledge graph approach"

**Tech Stack:** AllegroGraph (RDF) + Flask API + Python 3.10+ | **Data:** 4,000 real Capital IQ events (2007-2009 Lehman crisis)

## 📚 Documentation

- **[Developer Guide](CLAUDE.md)** - Complete technical guide for contributors
- **[Security Policy](SECURITY.md)** - Security guidelines and reporting
- **[Internal Docs](docs/internal/)** - Stage summaries, migration notes, and archived documentation

## 📊 Database: AllegroGraph (Production)

**Current Setup:**
- **Database:** AllegroGraph 8.4.0 (cloud-hosted)
- **Data:** 4,000 real financial events from Capital IQ (2007-2009 Lehman Brothers crisis)
- **Repository:** `mycatalog/FEEKG` @ qa-agraph.nelumbium.ai
- **Entities:** 22 major financial institutions (Morgan Stanley, Lehman Brothers, etc.)
- **Query Language:** SPARQL

> ⚠️ **Note:** Neo4j has been retired in favor of AllegroGraph. See [docs/internal/migration-notes/ALLEGROGRAPH_MIGRATION.md](docs/internal/migration-notes/ALLEGROGRAPH_MIGRATION.md) for details.

## 🚀 How to View Everything

### Option 1: Interactive HTML Visualizations

```bash
# Open interactive visualizations in browser
open results/optimized_knowledge_graph.html  # Main interactive graph
open results/timeline_view.html              # Timeline with 4,000 events
open results/dashboard.html                  # Statistics dashboard
```

**Available visualizations** (in `results/` folder):
- `optimized_knowledge_graph.html` (127KB) - Interactive network graph with zoom/pan/filter
- `timeline_view.html` (174KB) - Hierarchical timeline of 4,000 Lehman crisis events
- `dashboard.html` - Entity/Event/Risk statistics dashboard
- `interactive_kg_lehman_200.html` - Medium-scale graph (200 events)
- `clean_knowledge_graph.html` - Simplified graph view
- And 2 more...

See [docs/internal/archived/FRONTEND_STATUS.md](docs/internal/archived/FRONTEND_STATUS.md) for complete visualization documentation.

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

### Option 3: AllegroGraph SPARQL Queries

```bash
# Check repository status
./venv/bin/python scripts/utils/check_feekg_mycatalog.py
```

See [docs/internal/migration-notes/ALLEGROGRAPH_MIGRATION.md](docs/internal/migration-notes/ALLEGROGRAPH_MIGRATION.md) for SPARQL query examples.

### Option 4: Run Query Demos (Terminal)

```bash
# Interactive demonstrations
./venv/bin/python scripts/demos/demo_feekg_capabilities.py

# This shows:
# - AllegroGraph connection test
# - Database statistics (4,000 events, 22 entities)
# - SPARQL query examples
# - Data quality metrics
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

Create a `.env` file with your AllegroGraph credentials:

```bash
AG_URL=https://qa-agraph.nelumbium.ai/
AG_USER=your_username
AG_PASS=your_password
AG_CATALOG=mycatalog
AG_REPO=FEEKG
```

**⚠️ NEVER commit the .env file to Git!** See [SECURITY.md](SECURITY.md) for details.

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

## Development Status

- [x] **AllegroGraph Migration**: Migrated from Neo4j to AllegroGraph (cloud-hosted RDF triplestore) ✅
- [x] **Capital IQ Data**: Loaded 4,000 real financial events from 2007-2009 Lehman Brothers crisis ✅
- [x] **CSV Traceability**: Full data lineage with row numbers and Capital IQ IDs ✅
- [x] **Event Evolution**: 6 evolution algorithms (temporal, entity, semantic, topic, causal, emotional) ✅
- [x] **SPARQL Queries**: Query system with Python API ✅
- [x] **Interactive Visualizations**: 7 HTML visualizations with vis.js (network graphs, timeline, dashboard) ✅
- [x] **REST API**: 20+ endpoints for data access and visualization generation ✅
- [ ] **Evolution Links Computation**: Apply 6 methods to 4,000 events (future)

## Usage Guide

### Connecting to AllegroGraph

```bash
# Test connection
./venv/bin/python scripts/utils/check_feekg_mycatalog.py

# Expected output:
# ✅ Connected to AllegroGraph
# 📊 Total triples: 59,090
# 📅 Events: 4,000
# 👥 Entities: 22
```

### Running Demos

```bash
# Interactive capabilities demo
./venv/bin/python scripts/demos/demo_feekg_capabilities.py

# View visualizations
open results/optimized_knowledge_graph.html
open results/timeline_view.html
open results/dashboard.html
```

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

### Using SPARQL Queries

```python
import requests
from requests.auth import HTTPBasicAuth

url = 'https://qa-agraph.nelumbium.ai/catalogs/mycatalog/repositories/FEEKG'
auth = HTTPBasicAuth('sadmin', '279H-Dt<>,YU')

# Query entities
query = '''
PREFIX feekg: <http://feekg.org/ontology#>
SELECT ?entity ?label ?type
WHERE {
    ?entity a feekg:Entity .
    ?entity feekg:label ?label .
    ?entity feekg:entityType ?type .
}
LIMIT 10
'''

response = requests.post(url, data={'query': query},
                        headers={'Accept': 'application/sparql-results+json'},
                        auth=auth)
results = response.json()['results']['bindings']

for r in results:
    print(f"{r['label']['value']} ({r['type']['value']})")
```

See [ALLEGROGRAPH_MIGRATION.md](ALLEGROGRAPH_MIGRATION.md) for more SPARQL examples.

## 📋 Quick Reference

### All Important Commands

```bash
# =============================================================================
# INTERACTIVE VISUALIZATIONS
# =============================================================================

# Open interactive HTML visualizations in browser
open results/optimized_knowledge_graph.html  # Main interactive graph
open results/timeline_view.html              # Timeline with 4,000 events
open results/dashboard.html                  # Statistics dashboard

# =============================================================================
# REST API
# =============================================================================

# Start API server → http://localhost:5000
./venv/bin/python api/app.py

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/info
curl http://localhost:5000/api/entities

# Open interactive demo page (in browser)
# Navigate to: file:///Users/hansonxiong/Desktop/DDP/feekg/api/demo.html

# =============================================================================
# ALLEGROGRAPH QUERIES
# =============================================================================

# Check AllegroGraph repository status
./venv/bin/python scripts/utils/check_feekg_mycatalog.py

# Run interactive capabilities demo
./venv/bin/python scripts/demos/demo_feekg_capabilities.py

# =============================================================================
# DATA MANAGEMENT
# =============================================================================

# Load Capital IQ data to AllegroGraph
./venv/bin/python ingestion/load_capital_iq_to_allegrograph.py

# Recompute evolution links (SPARQL-based)
./venv/bin/python evolution/run_evolution_ag.py
```

### Important Files & Locations

| What | Where | Description |
|------|-------|-------------|
| **Interactive Visualizations** | `results/*.html` | 7 interactive HTML visualizations |
| **API Demo** | `api/demo.html` | Interactive web interface |
| **API Docs** | `api/README.md` | Complete API documentation |
| **Project Guide** | `CLAUDE.md` | Comprehensive project guide |
| **AllegroGraph Migration** | `ALLEGROGRAPH_MIGRATION.md` | Migration guide and SPARQL examples |
| **Frontend Status** | `FRONTEND_STATUS.md` | Visualization documentation |
| **Capital IQ Data** | `data/capital_iq_raw/` | Raw transaction data (2007-2009) |
| **Processed Data** | `data/capital_iq_processed/` | Classified Lehman events |
| **Data Quality Report** | `DATA_QUALITY_REPORT.md` | Classification metrics |

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
