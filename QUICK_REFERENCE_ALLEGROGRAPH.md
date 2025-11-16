# AllegroGraph Quick Reference

## ✅ WORKING Connection Method

```python
from franz.openrdf.connect import ag_connect

conn = ag_connect(
    'KG_200203',  # Repository name
    user='sadmin',
    host='https://qa-agraph.nelumbium.ai:443',  # ← Explicit :443 is key!
    password='your_password'
)

print(f"✅ Connected! Triples: {conn.size()}")
conn.close()
```

## Key Requirements

1. **Install dependencies**:
   ```bash
   pip install agraph-python pycurl
   ```

2. **Use explicit port 443** in host URL

3. **Use `ag_connect`** (not `AllegroGraphServer`)

## What Works Now ✅

- ✅ Connect via HTTPS port 443
- ✅ Read from repositories
- ✅ SPARQL queries
- ✅ Get triple counts

## What Needs Permissions ⚠️

- ⚠️ Create repositories
- ⚠️ Write triples
- ⚠️ Delete data

## Quick Tests

### Test Connection
```bash
./venv/bin/python -c "
from franz.openrdf.connect import ag_connect
import os
from dotenv import load_dotenv
load_dotenv()

conn = ag_connect('KG_200203', user='sadmin',
                  host='https://qa-agraph.nelumbium.ai:443',
                  password=os.getenv('AG_PASS'))
print(f'✅ Connected! Triples: {conn.size()}')
conn.close()
"
```

### Test RDF Backend
```bash
AG_REPO=KG_200203 ./venv/bin/python -c "
from config.rdf_backend import RDFBackend
backend = RDFBackend()
backend.connect()
stats = backend.get_stats()
print(f\"Total triples: {stats['total_triples']}\")
backend.close()
"
```

### Test Native Script
```bash
AG_REPO=KG_200203 ./venv/bin/python scripts/store_triples_native.py --mode query
```

## Files Updated

- ✅ [config/rdf_backend.py](config/rdf_backend.py)
- ✅ [config/graph_backend.py](config/graph_backend.py)
- ✅ [requirements.txt](requirements.txt)
- ✅ [scripts/store_triples_native.py](scripts/store_triples_native.py)

## Documentation

- [ALLEGROGRAPH_NATIVE_CLIENT.md](ALLEGROGRAPH_NATIVE_CLIENT.md) - Complete guide
- [ALLEGROGRAPH_COMPARISON.md](ALLEGROGRAPH_COMPARISON.md) - Technical comparison
- [ALLEGROGRAPH_STATUS.md](ALLEGROGRAPH_STATUS.md) - Current status

## Next Step

**Get write permissions** from AllegroGraph admin for repository `feekg_dev` or use existing writable repository.
