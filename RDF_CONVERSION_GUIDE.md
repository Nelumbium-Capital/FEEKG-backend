# Converting FE-EKG to RDF

You have **4 options** to use RDF with FE-EKG:

## Option 1: AllegroGraph RDF Backend (Recommended)

Use your existing AllegroGraph credentials to store data as RDF triples.

### Setup

Your `.env` already has AllegroGraph credentials:
```bash
AG_URL=https://qa-agraph.nelumbium.ai/
AG_USER=sadmin
AG_PASS=279H-Dt<>,YU
AG_REPO=feekg_dev
```

### Convert Your Data

```bash
# Interactive menu
./venv/bin/python scripts/convert_to_rdf.py

# Options:
# 1. Convert from Neo4j to RDF (migrate existing data)
# 2. Convert from JSON to RDF (fresh start)
# 3. Export to Turtle file (.ttl)
# 4. Test SPARQL queries
```

### Use RDF Backend in Code

```python
from config.rdf_backend import RDFBackend

# Connect
rdf = RDFBackend()
rdf.connect()

# Add event as RDF triple
event = {
    'eventId': 'evt_001',
    'type': 'debt_default',
    'date': '2021-12-01',
    'description': 'Evergrande defaulted on bonds'
}
rdf.create_event_triple(event)

# Query with SPARQL
query = """
PREFIX feekg: <http://feekg.org/ontology#>

SELECT ?event ?type ?date
WHERE {
    ?event a feekg:Event .
    ?event feekg:eventType ?type .
    ?event feekg:date ?date .
}
ORDER BY ?date
"""
results = rdf.query_sparql(query)

# Export to file
rdf.export_to_turtle('results/feekg_graph.ttl')

rdf.close()
```

### RDF Triple Format

Your data becomes:

```turtle
@prefix feekg: <http://feekg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Event
feekg:evt_001 rdf:type feekg:Event .
feekg:evt_001 feekg:eventType "debt_default" .
feekg:evt_001 feekg:date "2021-12-01"^^xsd:date .
feekg:evt_001 feekg:description "Evergrande defaulted on bonds" .

# Entity
feekg:ent_evergrande rdf:type feekg:Entity .
feekg:ent_evergrande feekg:name "China Evergrande Group" .
feekg:ent_evergrande feekg:entityType "company" .

# Evolution relationship (reified)
feekg:evt_001_to_evt_002 rdf:type feekg:EvolutionLink .
feekg:evt_001_to_evt_002 feekg:fromEvent feekg:evt_001 .
feekg:evt_001_to_evt_002 feekg:toEvent feekg:evt_002 .
feekg:evt_001_to_evt_002 feekg:score "0.85"^^xsd:float .
```

---

## Option 2: Neo4j + Neosemantics (n10s)

Keep using Neo4j but add RDF support with the `n10s` plugin.

### Install n10s Plugin

```bash
# 1. Download n10s plugin
# https://github.com/neo4j-labs/neosemantics/releases

# 2. Copy to Neo4j plugins folder
docker cp neosemantics-4.4.0.0.jar feekg-neo4j:/plugins/

# 3. Restart Neo4j
docker restart feekg-neo4j

# 4. Enable in Neo4j Browser
CALL n10s.graphconfig.init();
```

### Export Neo4j to RDF

```cypher
// Export entire graph to Turtle
CALL n10s.rdf.export.cypher(
  'MATCH (n) RETURN n',
  {format: 'Turtle'}
)
```

### Import RDF into Neo4j

```cypher
// Import from Turtle file
CALL n10s.rdf.import.fetch(
  'file:///path/to/feekg_graph.ttl',
  'Turtle'
)
```

**Pros**: Keep Neo4j, get RDF for free
**Cons**: Requires plugin installation, mapping config

---

## Option 3: RDFLib (Python Library)

Generate RDF triples using Python's `rdflib` library.

### Install

```bash
./venv/bin/pip install rdflib
```

### Example Code

```python
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

# Create graph
g = Graph()
FEEKG = Namespace("http://feekg.org/ontology#")
g.bind("feekg", FEEKG)

# Add event
event_uri = FEEKG['evt_001']
g.add((event_uri, RDF.type, FEEKG.Event))
g.add((event_uri, FEEKG.eventType, Literal("debt_default")))
g.add((event_uri, FEEKG.date, Literal("2021-12-01", datatype=XSD.date)))

# Save to file
g.serialize(destination='results/feekg_graph.ttl', format='turtle')

# Query with SPARQL
query = """
SELECT ?event ?type
WHERE {
    ?event a feekg:Event .
    ?event feekg:eventType ?type .
}
"""
results = g.query(query)
for row in results:
    print(f"{row.event} -> {row.type}")
```

**Pros**: Pure Python, no external database
**Cons**: In-memory only, no scalability

---

## Option 4: Dual Backend (Neo4j + AllegroGraph)

Run both Neo4j and AllegroGraph simultaneously.

### Architecture

```
FE-EKG
   ├── Neo4j (primary)        ← Fast queries, visualizations
   └── AllegroGraph (RDF)     ← SPARQL, semantic web integration
```

### Code Example

```python
from config.graph_backend import Neo4jBackend
from config.rdf_backend import RDFBackend

# Dual write
neo4j = Neo4jBackend()
rdf = RDFBackend()
rdf.connect()

def add_event(event):
    # Write to both backends
    neo4j.create_event(event)
    rdf.create_event_triple(event)

# Query from either backend
# Fast queries: Neo4j
results = neo4j.execute_query("MATCH (e:Event) RETURN e LIMIT 10")

# Semantic queries: AllegroGraph
results = rdf.query_sparql("SELECT ?event WHERE { ?event a feekg:Event }")
```

**Pros**: Best of both worlds
**Cons**: Data sync complexity

---

## Comparison Table

| Feature | AllegroGraph | Neo4j + n10s | RDFLib | Dual Backend |
|---------|--------------|--------------|--------|--------------|
| **RDF Native** | ✅ Yes | 🟡 Via plugin | ✅ Yes | ✅ Yes |
| **SPARQL** | ✅ Full support | ✅ Via n10s | ✅ Yes | ✅ Yes |
| **Scalability** | ✅ Enterprise | ✅ High | ❌ In-memory | ✅ High |
| **Setup Complexity** | 🟡 Medium | 🟡 Plugin install | ✅ Easy | 🔴 Complex |
| **Your Credentials** | ✅ Already have | ❌ Need setup | ✅ Built-in | 🟡 Both |
| **Cost** | 💰 Commercial | 💰 Enterprise | 🆓 Free | 💰💰 Both |

---

## Recommendation

**For your project, I recommend Option 1: AllegroGraph** because:

1. ✅ You already have credentials in `.env`
2. ✅ RDF-native (no conversion needed)
3. ✅ Full SPARQL support
4. ✅ I already built the backend (`config/rdf_backend.py`)
5. ✅ Easy migration with `scripts/convert_to_rdf.py`

**Quick Start**:

```bash
# 1. Convert your data
./venv/bin/python scripts/convert_to_rdf.py
# Choose option 2: Convert from JSON to RDF

# 2. Test SPARQL queries
./venv/bin/python scripts/convert_to_rdf.py
# Choose option 4: Test SPARQL queries

# 3. Export to Turtle
./venv/bin/python scripts/convert_to_rdf.py
# Choose option 3: Export to .ttl file
```

---

## Why RDF?

**RDF (Resource Description Framework)** is better than property graphs for:

### 1. Semantic Web Integration
```sparql
# RDF: Can federate with other knowledge graphs
SELECT ?event ?related
WHERE {
    ?event a feekg:Event .

    # Query external SPARQL endpoint
    SERVICE <http://dbpedia.org/sparql> {
        ?related dbo:company ?event .
    }
}
```

### 2. Schema Flexibility
```turtle
# RDF: Can add properties without schema migration
feekg:evt_001 feekg:newProperty "value" .  # Just add it!
```

### 3. Standards Compliance
- W3C standards (RDF, SPARQL, OWL)
- Interoperability with other systems
- Reuse existing ontologies (Dublin Core, FOAF, etc.)

### 4. Reasoning
```sparql
# OWL reasoning: Infer new facts
feekg:LiquidityRisk rdfs:subClassOf feekg:FinancialRisk .
# Reasoner automatically knows all liquidity risks are financial risks
```

---

## Files Created

```
feekg/
├── config/
│   └── rdf_backend.py           # AllegroGraph RDF backend
│
├── scripts/
│   └── convert_to_rdf.py        # Conversion tool
│
└── RDF_CONVERSION_GUIDE.md      # This file
```

---

## Next Steps

1. **Try the conversion**:
   ```bash
   ./venv/bin/python scripts/convert_to_rdf.py
   ```

2. **Learn SPARQL**:
   - Similar to SQL but for triples
   - W3C tutorial: https://www.w3.org/TR/sparql11-query/

3. **Integrate with API**:
   - Add SPARQL endpoint to `api/app.py`
   - Query RDF from web demo

4. **Explore semantic reasoning**:
   - Define ontology with OWL
   - Use reasoners to infer new knowledge

---

## Troubleshooting

**Problem**: AllegroGraph connection fails

```bash
# Check if AllegroGraph is accessible
curl https://qa-agraph.nelumbium.ai:10035

# Verify credentials in .env
cat .env | grep AG_
```

**Problem**: Port 10035 blocked

```bash
# AllegroGraph uses port 10035
# Check firewall/VPN settings
```

**Problem**: Want to use both Neo4j and RDF

```python
# Use dual backend approach
from config.graph_backend import Neo4jBackend
from config.rdf_backend import RDFBackend

# Both work simultaneously
```

---

**Status**: RDF backend ready to use! 🎉
