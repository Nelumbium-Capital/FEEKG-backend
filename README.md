# FE-EKG: Financial Event Evolution Knowledge Graph

Implementation of the FEEKG paper: "Risk identification and management through knowledge Association: A financial event evolution knowledge graph approach"

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

## Development Status

- [x] **Stage 1**: Infrastructure & connection test ✅
- [x] **Stage 2**: Minimal schema with Risk Layer + Neo4j backend ✅
- [x] **Stage 3**: Sample Evergrande data (20 events, 10 entities, 10 risks, 154 enhanced evolution links) ✅
- [x] **Stage 4**: Event evolution methods (6 algorithms: temporal, entity, semantic, topic, causal, emotional) ✅
- [x] **Stage 5**: Risk queries (80+ Cypher templates, Python API, interactive demo) ✅
- [ ] **Stage 6**: Three-layer visualization
- [ ] **Stage 7**: Mini ABM (optional)

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
