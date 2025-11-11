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
- [x] **Stage 3**: Sample Evergrande data (20 events, 10 entities, 10 risks, 190 evolution links) ✅
- [ ] **Stage 4**: Event evolution methods (6 algorithms)
- [ ] **Stage 5**: Risk queries (Cypher/SPARQL)
- [ ] **Stage 6**: Three-layer visualization
- [ ] **Stage 7**: Mini ABM (optional)

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
