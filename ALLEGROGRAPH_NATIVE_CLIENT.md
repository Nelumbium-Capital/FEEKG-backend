# AllegroGraph Native Client - Working Configuration

**Date**: 2025-11-11
**Status**: ✅ Connection works with HTTPS port 443!

---

## Problem Solved! 🎉

The original issue was trying to use **port 10035** which is blocked. The solution is to use **HTTPS with explicit port 443**.

### Before (Didn't Work) ❌
```python
from franz.openrdf.sail.allegrographserver import AllegroGraphServer

server = AllegroGraphServer(
    host="qa-agraph.nelumbium.ai",
    port=10035,  # ← BLOCKED BY FIREWALL
    user="sadmin",
    password=password
)
# Result: Connection timeout
```

### After (Works!) ✅
```python
from franz.openrdf.connect import ag_connect

conn = ag_connect(
    'KG_200203',  # Repository name
    user="sadmin",
    host="https://qa-agraph.nelumbium.ai:443",  # ← Explicit port 443
    password=password
)
# Result: ✅ Connected! Triple count: 1707
```

---

## Key Changes Made

### 1. Added `pycurl` Dependency

**File**: [requirements.txt](requirements.txt#L4)
```diff
  agraph-python>=101.0.6  # AllegroGraph (RDF/SPARQL)
+ pycurl>=7.45.0          # Required by agraph-python for HTTPS
```

**Install**:
```bash
./venv/bin/pip install pycurl
```

### 2. Updated `config/rdf_backend.py`

**Before**:
```python
self.conn = ag_connect(
    self.ag_repo,
    host=self.ag_url.replace('https://', '').replace('http://', '').rstrip('/'),
    port=10035,  # ← Wrong
    user=self.ag_user,
    password=self.ag_pass
)
```

**After**:
```python
# Ensure URL has explicit port 443
if ':443' not in self.ag_url and self.ag_url.startswith('https://'):
    self.ag_url = self.ag_url.rstrip('/') + ':443'

self.conn = ag_connect(
    self.ag_repo,
    user=self.ag_user,
    host=self.ag_url,  # ← Full HTTPS URL with :443
    password=self.ag_pass
)
```

### 3. Updated `config/graph_backend.py`

Same changes applied to `AllegroGraphBackend` class.

### 4. Created New Script

**File**: [scripts/store_triples_native.py](scripts/store_triples_native.py)

Adapted from provided scripts with correct connection method.

---

## Test Results

### Connection Test ✅
```bash
$ python -c "
from franz.openrdf.connect import ag_connect
conn = ag_connect('KG_200203', user='sadmin',
                  host='https://qa-agraph.nelumbium.ai:443',
                  password='***')
print(f'✅ Connected! Triples: {conn.size()}')
"

✅ Connected! Triples: 1707
```

### Updated RDFBackend Test ✅
```bash
$ python -c "
from config.rdf_backend import RDFBackend
backend = RDFBackend()
backend.ag_repo = 'KG_200203'
backend.connect()
"

✅ Connected to AllegroGraph: KG_200203
✅ Triple count: 1707
```

### Native Script Test ✅ (Read-Only)
```bash
$ AG_REPO=KG_200203 python scripts/store_triples_native.py --mode query

✅ Connected to KG_200203
✅ Current triple count: 1707
```

---

## Current Permissions

### What Works ✅
- ✅ **Connect** to AllegroGraph via HTTPS port 443
- ✅ **List** repositories (28 repositories found)
- ✅ **Read** from existing repositories (e.g., `KG_200203`)
- ✅ **Query** with SPARQL
- ✅ **Get** triple counts and stats

### What Requires Permissions ⚠️
- ⚠️ **Create** new repositories (e.g., `feekg_dev`)
- ⚠️ **Write** to existing repositories
- ⚠️ **Delete** triples
- ⚠️ **Modify** repository settings

**Error messages seen**:
```
401 User 'sadmin' does not have sufficient permissions to perform this operation.
401 You do not have write permission on this repository.
```

---

## Available Repositories

Your AllegroGraph server has **28 repositories**:

1. BIS2008
2. BIS2008-nl-QlJcn
3. BIS99
4. Crisis_report
5. Crisis_report_vec_db
6. Earning_Call_Dataset
7. Event2018
8. Event_risk
9. Events&Risk
10. Events2018
... and 18 more

---

## Solutions

### Option 1: Get Write Permissions (Recommended)

**Ask your AllegroGraph admin to**:

1. **Create `feekg_dev` repository** with write access for user `sadmin`
2. Or **grant write access** to an existing repository

**Then you can**:
```bash
# Store triples
./venv/bin/python scripts/store_triples_native.py --mode sample

# Load from Neo4j
./venv/bin/python scripts/store_triples_native.py --mode neo4j

# Use RDF backend
python -c "
from config.rdf_backend import RDFBackend
backend = RDFBackend()
backend.connect()
# Now can create_event_triple(), create_entity_triple(), etc.
"
```

### Option 2: Use Existing Writable Repository

**Find a repository you can write to**:
```bash
# Test each repository
for repo in Crisis_report Event_risk Events2018; do
  echo "Testing $repo..."
  AG_REPO=$repo python scripts/store_triples_native.py --mode sample
done
```

**Update `.env`**:
```bash
AG_REPO=<writable_repository>
```

### Option 3: Use Apache Jena Fuseki (Alternative)

**No permission issues, full control**:
```bash
# Install and run Fuseki
./scripts/setup_fuseki.sh

# Upload data
python -c "
from config.fuseki_backend import FusekiBackend
fuseki = FusekiBackend()
fuseki.upload_turtle_file('results/feekg_graph.ttl')
"

# Query via web UI
open http://localhost:3030
```

### Option 4: Keep Using RDFLib (Simplest)

**Already works, no server needed**:
```bash
./venv/bin/python scripts/demo_rdf_conversion.py
```

---

## How to Use Now

### For Read-Only Operations ✅

**Query existing data**:
```python
from franz.openrdf.connect import ag_connect

conn = ag_connect(
    'KG_200203',  # Or any readable repository
    user='sadmin',
    host='https://qa-agraph.nelumbium.ai:443',
    password='your_password'
)

# Run SPARQL query
query = """
SELECT ?s ?p ?o
WHERE { ?s ?p ?o }
LIMIT 10
"""

result = conn.prepareTupleQuery(query=query).evaluate()
for binding in result:
    print(binding)

conn.close()
```

**Using RDFBackend**:
```python
from config.rdf_backend import RDFBackend
import os

os.environ['AG_REPO'] = 'KG_200203'

backend = RDFBackend()
backend.connect()

# Get stats
stats = backend.get_stats()
print(f"Total triples: {stats['total_triples']}")

# Query
results = backend.query_sparql("""
SELECT * WHERE { ?s ?p ?o } LIMIT 5
""")

backend.close()
```

### For Write Operations ⚠️

**Requires admin to grant permissions first**.

Once you have write access:

```bash
# Store sample triples
./venv/bin/python scripts/store_triples_native.py --mode sample

# Load from Neo4j
./venv/bin/python scripts/store_triples_native.py --mode neo4j

# Use RDF backend programmatically
python -c "
from config.rdf_backend import RDFBackend

backend = RDFBackend()
backend.connect()

# Create event
event = {
    'eventId': 'evt_test',
    'type': 'debt_default',
    'date': '2021-12-01',
    'actor': 'ent_evergrande'
}
backend.create_event_triple(event)

backend.close()
"
```

---

## Files Updated

### Core Backends ✅
- [config/rdf_backend.py](config/rdf_backend.py) - Updated `connect()` to use port 443
- [config/graph_backend.py](config/graph_backend.py) - Updated `AllegroGraphBackend.connect()`
- [requirements.txt](requirements.txt) - Added `pycurl` dependency

### New Scripts ✨
- [scripts/store_triples_native.py](scripts/store_triples_native.py) - Adapted storage script
- [scripts/test_allegrograph_simple.py](scripts/test_allegrograph_simple.py) - HTTPS connection test

### Documentation 📄
- [ALLEGROGRAPH_COMPARISON.md](ALLEGROGRAPH_COMPARISON.md) - Technical comparison
- [ALLEGROGRAPH_STATUS.md](ALLEGROGRAPH_STATUS.md) - Current status
- [ALLEGROGRAPH_NATIVE_CLIENT.md](ALLEGROGRAPH_NATIVE_CLIENT.md) - This file

---

## Provided Scripts Comparison

### Original Scripts (Provided)
```python
# store_triples_to_allegrograph.py
AG_HOST = "127.0.0.1"  # ← Localhost only
AG_PORT = 10035         # ← Blocked port

server = AllegroGraphServer(
    host=AG_HOST,
    port=AG_PORT,  # ← Doesn't work
    ...
)
```

**Problems**:
- ❌ Uses localhost (not remote server)
- ❌ Uses port 10035 (blocked)
- ❌ Wrong connection method
- ❌ Missing imports for your project

### Adapted Script (Fixed)
```python
# scripts/store_triples_native.py
AG_HOST = os.getenv('AG_URL', 'https://qa-agraph.nelumbium.ai/')
if ':443' not in AG_HOST:
    AG_HOST = AG_HOST.rstrip('/') + ':443'  # ← Add explicit port

conn = ag_connect(
    AG_REPOSITORY,
    user=AG_USER,
    host=AG_HOST,  # ← Full HTTPS URL
    password=AG_PASSWORD
)
```

**Improvements**:
- ✅ Uses environment variables
- ✅ Explicit HTTPS port 443
- ✅ Works with remote server
- ✅ Integrates with your Neo4j data
- ✅ Multiple modes (sample/neo4j/query)

---

## What You Learned

### The Critical Insight 💡

**From the user**:
```python
from franz.openrdf.connect import ag_connect

conn = ag_connect('KG_200203',
                  user="admin",
                  host="https://qa-agraph.nelumbium.ai:443",  # ← Explicit :443
                  password="Password#123!")
```

**Key points**:
1. Use **`ag_connect`** (not `AllegroGraphServer`)
2. Specify **full HTTPS URL** with **explicit `:443`**
3. Install both **`agraph-python`** and **`pycurl`**
4. Port 443 is **never blocked** by firewalls

---

## Next Steps

### Immediate Actions

**1. Request Permissions**

Contact your AllegroGraph admin and request:
- Create repository: `feekg_dev`
- Grant write access to user: `sadmin`

**2. Test with Existing Repo**

Try finding a writable repository:
```bash
# Test repositories one by one
for repo in Crisis_report Event_risk Events2018 Event2018; do
  echo "Testing $repo..."
  AG_REPO=$repo python -c "
from franz.openrdf.connect import ag_connect
import os
conn = ag_connect(os.environ['AG_REPO'], user='sadmin',
                  host='https://qa-agraph.nelumbium.ai:443',
                  password=os.getenv('AG_PASS'))
try:
    # Try to add a test triple
    s = conn.createURI('http://test/subject')
    p = conn.createURI('http://test/predicate')
    o = conn.createURI('http://test/object')
    conn.add(s, p, o)
    print(f'✅ {os.environ[\"AG_REPO\"]} is writable!')
    conn.remove(s, p, o)  # Clean up
except:
    print(f'❌ {os.environ[\"AG_REPO\"]} is read-only')
conn.close()
"
done
```

**3. Use Alternative (If Needed)**

While waiting for permissions:
```bash
# Use Fuseki (5 minutes setup)
./scripts/setup_fuseki.sh

# Or use RDFLib (works now)
./venv/bin/python scripts/demo_rdf_conversion.py
```

---

## Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| **HTTPS Connection** | ✅ Working | Port 443, no firewall issues |
| **ag_connect Method** | ✅ Working | Correct usage with explicit port |
| **pycurl Installed** | ✅ Done | Required dependency added |
| **Read Access** | ✅ Working | Can query existing repositories |
| **Write Access** | ⚠️ Needs Permissions | Request admin to grant access |
| **Native Scripts** | ✅ Adapted | [scripts/store_triples_native.py](scripts/store_triples_native.py) |
| **Backends Updated** | ✅ Done | Both RDF and Graph backends fixed |

---

## Bottom Line

✅ **The provided scripts CAN be used** - but needed adaptation for:
1. HTTPS port 443 instead of port 10035
2. Remote server instead of localhost
3. Your project structure and imports

✅ **Connection works perfectly** - just need write permissions

✅ **All backends updated** - ready to use once permissions granted

🎉 **Problem solved!** - Port 10035 blocking issue resolved with explicit HTTPS :443

---

**To get fully working**:
1. Get admin to create `feekg_dev` with write access
2. Or find existing writable repository
3. Or use Fuseki/RDFLib alternatives

**Everything is ready to go** - just waiting on permissions! 🚀
