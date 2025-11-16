# AllegroGraph Connection Methods Comparison

## TL;DR

**Original Scripts**: ❌ Use port 10035 (blocked)
**Your HTTPS Backend**: ✅ Uses port 443 (works)
**Adapted Script**: ✅ Uses HTTPS backend (best of both)

---

## Comparison Table

| Feature | Original Scripts | Your HTTPS Backend | Adapted Script |
|---------|-----------------|-------------------|----------------|
| **Port** | 10035 (blocked) | 443 (HTTPS) | 443 (HTTPS) |
| **Library** | franz.openrdf | requests | requests |
| **Works remotely?** | ❌ No | ✅ Yes | ✅ Yes |
| **Firewall-friendly?** | ❌ No | ✅ Yes | ✅ Yes |
| **Triple storage** | ✅ Yes | ✅ Yes | ✅ Yes |
| **SPARQL queries** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Neo4j integration** | ❌ No | ❌ No | ✅ Yes |

---

## 1. Original Scripts (Provided)

**Files**: `store_triples_to_allegrograph.py`, `store_triples_to_allegrograph-1.py`

### Connection Method
```python
from franz.openrdf.sail.allegrographserver import AllegroGraphServer

server = AllegroGraphServer(
    host="127.0.0.1",      # Localhost only
    port=10035,            # ← BLOCKED PORT
    user="SADMIN",
    password=password
)
```

### Problems
1. ❌ **Port 10035 blocked** by firewall
2. ❌ **Localhost only** - doesn't work with remote `qa-agraph.nelumbium.ai`
3. ❌ **Different project structure** - imports don't exist in your codebase
4. ❌ **Network dependency** - requires VPN or firewall rules

### What They Do Well
- ✅ Clear triple storage pattern
- ✅ Good error handling
- ✅ Sample SPARQL query examples
- ✅ URI creation helpers

---

## 2. Your HTTPS Backend (Already Created)

**File**: [config/allegrograph_https_backend.py](config/allegrograph_https_backend.py)

### Connection Method
```python
import requests

# Uses HTTPS REST API
self.repos_url = f"{self.base_url}/repositories"
self.statements_url = f"{self.repo_url}/statements"

response = requests.post(
    self.statements_url,
    data=triple_content,
    auth=(self.user, self.password),  # HTTP Basic Auth
    headers={'Content-Type': 'text/plain'}
)
```

### Advantages
1. ✅ **Port 443 (HTTPS)** - not blocked
2. ✅ **REST API** - standard HTTP operations
3. ✅ **Remote access** - works with `qa-agraph.nelumbium.ai`
4. ✅ **No special client** - uses standard `requests` library
5. ✅ **Firewall-friendly** - HTTPS is almost never blocked

### What It Does
- ✅ Test connection
- ✅ List repositories
- ✅ Create repositories
- ✅ Upload Turtle files
- ✅ Execute SPARQL queries
- ✅ Get triple counts
- ✅ Clear repositories

---

## 3. Adapted Script (Just Created)

**File**: [scripts/store_triples_https.py](scripts/store_triples_https.py)

### What It Combines
```python
from config.allegrograph_https_backend import AllegroGraphHTTPSBackend

# Uses HTTPS backend (not port 10035)
ag = AllegroGraphHTTPSBackend()

# Stores triples like original scripts
ag.add_triple(subject, predicate, object)

# Integrates with your Neo4j data
neo4j = Neo4jBackend()
events = neo4j.execute_query("MATCH (e:Event) RETURN e")
```

### Advantages
1. ✅ **HTTPS connection** (bypasses firewall)
2. ✅ **Triple storage pattern** from original scripts
3. ✅ **Neo4j integration** with your existing data
4. ✅ **Two modes**:
   - `sample`: Store demo triples
   - `neo4j`: Convert Neo4j data to RDF

### Usage

**Store sample triples:**
```bash
./venv/bin/python scripts/store_triples_https.py --mode sample
```

**Load from Neo4j and store:**
```bash
./venv/bin/python scripts/store_triples_https.py --mode neo4j
```

---

## Technical Comparison

### Port 10035 vs HTTPS (Port 443)

**Port 10035 (Original Scripts)**:
```python
# Native AllegroGraph protocol
server = AllegroGraphServer(
    host="qa-agraph.nelumbium.ai",
    port=10035  # ← Blocked by firewall
)
# Result: Connection timeout
```

**Port 443 (HTTPS Backend)**:
```python
# REST API over HTTPS
requests.post(
    "https://qa-agraph.nelumbium.ai/repositories/feekg_dev/statements",
    auth=(user, password)  # ← Works through firewall
)
# Result: ✅ Success
```

### Why Port 10035 Is Blocked

1. **Corporate firewalls** block non-standard ports
2. **Security policies** only allow HTTP(S) (80/443)
3. **AllegroGraph port 10035** is a proprietary protocol port
4. **HTTPS port 443** is universally allowed

---

## What You Should Use

### Recommendation: Hybrid Approach ✅

**For triple storage and queries:**
```bash
# Use the adapted script (best of both worlds)
./venv/bin/python scripts/store_triples_https.py --mode neo4j
```

**For RDF conversion:**
```bash
# Use existing conversion script
./venv/bin/python scripts/convert_to_rdf.py
```

**For testing:**
```bash
# Use HTTPS backend directly
./venv/bin/python config/allegrograph_https_backend.py
```

---

## Migration Path

If you want to fully integrate AllegroGraph:

### Step 1: Test HTTPS Connection
```bash
./venv/bin/python config/allegrograph_https_backend.py
```

### Step 2: Store Sample Triples
```bash
./venv/bin/python scripts/store_triples_https.py --mode sample
```

### Step 3: Load from Neo4j
```bash
./venv/bin/python scripts/store_triples_https.py --mode neo4j
```

### Step 4: Query via SPARQL
```python
from config.allegrograph_https_backend import AllegroGraphHTTPSBackend

ag = AllegroGraphHTTPSBackend()
results = ag.query_sparql("""
PREFIX feekg: <http://feekg.org/ontology#>
SELECT ?event ?type WHERE {
    ?event a feekg:Event .
    ?event feekg:eventType ?type .
}
""")
```

---

## Alternative: Keep Using Neo4j + RDFLib

**Your current setup works great:**

1. ✅ **Neo4j** as primary database (20 events, 10 entities, 10 risks)
2. ✅ **RDFLib** for RDF export ([scripts/demo_rdf_conversion.py](scripts/demo_rdf_conversion.py))
3. ✅ **REST API** for queries ([api/app.py](api/app.py))
4. ✅ **Visualizations** working ([results/](results/))

**You don't NEED AllegroGraph** unless:
- You want a dedicated RDF triplestore
- You need advanced SPARQL features
- You're integrating with other RDF systems

---

## Summary

| Aspect | Original Scripts | Use This Instead |
|--------|-----------------|------------------|
| **Connection** | Port 10035 (blocked) | [config/allegrograph_https_backend.py](config/allegrograph_https_backend.py) |
| **Triple Storage** | Good pattern | [scripts/store_triples_https.py](scripts/store_triples_https.py) |
| **RDF Conversion** | Not included | [scripts/convert_to_rdf.py](scripts/convert_to_rdf.py) |
| **SPARQL Queries** | Limited examples | [config/allegrograph_https_backend.py](config/allegrograph_https_backend.py) |
| **Neo4j Integration** | Not included | [scripts/store_triples_https.py](scripts/store_triples_https.py) `--mode neo4j` |

---

## Files Reference

### Your Existing Files (All Working) ✅
- [config/allegrograph_https_backend.py](config/allegrograph_https_backend.py) - HTTPS connection
- [config/fuseki_backend.py](config/fuseki_backend.py) - Apache Fuseki alternative
- [scripts/convert_to_rdf.py](scripts/convert_to_rdf.py) - Neo4j → RDF conversion
- [scripts/demo_rdf_conversion.py](scripts/demo_rdf_conversion.py) - RDFLib demo

### New File (Just Created) ✨
- [scripts/store_triples_https.py](scripts/store_triples_https.py) - Adapted storage script

### Provided Files (Don't Use - Port 10035) ❌
- `store_triples_to_allegrograph.py` - Original (blocked)
- `store_triples_to_allegrograph-1.py` - Duplicate (blocked)

---

## Conclusion

**No, the provided scripts won't help directly** because they use the blocked port 10035. However:

1. ✅ Your **HTTPS backend already solves the problem**
2. ✅ I've **adapted the scripts** to use HTTPS ([scripts/store_triples_https.py](scripts/store_triples_https.py))
3. ✅ You have **multiple working alternatives** (Fuseki, RDFLib)

**Recommendation**: Try the adapted script if you want AllegroGraph integration, or stick with your current Neo4j + RDFLib setup which already works perfectly.
