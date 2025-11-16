# Interactive Knowledge Graph Visualizations

## What You Have Now ✅

### 1. **Interactive HTML Visualizations**
Three interactive knowledge graphs powered by **Pyvis** and **AllegroGraph**:

- **`results/interactive_entities_lehman.html`** (12 KB)
  - 21 entities from Lehman Brothers crisis
  - Color-coded by type: Banks (blue), Investment Banks (red), Regulators (purple)
  - Fully interactive: drag, zoom, click for details

- **`results/interactive_kg_lehman_50.html`** (39 KB)
  - 21 entities + 50 events
  - Event-entity relationships (when SPARQL queries work)

- **`results/interactive_kg_lehman_200.html`** (124 KB)
  - 21 entities + 200 events
  - Larger graph for deeper exploration

### 2. **Interactive Features**
Each visualization supports:
- ✅ **Drag nodes** - Click and drag to rearrange
- ✅ **Zoom** - Mouse wheel to zoom in/out
- ✅ **Pan** - Click and drag background to move view
- ✅ **Hover tooltips** - See details on hover
- ✅ **Physics simulation** - Nodes auto-arrange with forces
- ✅ **Toggle physics** - Turn off for manual layout
- ✅ **Fit to screen** - Auto-center and scale
- ✅ **Navigation buttons** - Built-in controls

### 3. **How to Use**
```bash
# Open in browser (Mac)
open results/interactive_entities_lehman.html

# Or double-click the HTML files in Finder
# Or open in browser: File > Open > select HTML file
```

---

## Current Data in AllegroGraph

| **Data Type** | **Count** | **Status** |
|---------------|-----------|------------|
| Total triples | 96 | ✅ Loaded |
| Entities | 21 unique | ✅ Loaded |
| Events | 2,507 | ✅ Loaded |
| Evolution links | 0 | ⚠️ Need to compute |

**Entities include:**
- Lehman Brothers (investment bank)
- JP Morgan, Treasury (banks)
- Morgan Stanley, Merrill Lynch (investment banks)
- SEC, Treasury (regulators)

---

## Issues to Fix 🔧

### 1. **SPARQL FILTER IN Syntax**
AllegroGraph doesn't support this syntax:
```sparql
FILTER(?event IN (<uri1>, <uri2>, ...))
```

**Solution:** Use `VALUES` clause instead:
```sparql
VALUES ?event { <uri1> <uri2> <uri3> }
```

### 2. **414 Request-URI Too Large**
With 200+ event URIs, the HTTP GET request URL exceeds server limits.

**Solution:** Use HTTP POST for queries, or batch the queries.

### 3. **Missing Evolution Links**
Need to compute event evolution relationships using the 6 methods from the paper:
1. Temporal Correlation (TCDI)
2. Entity Overlap (Jaccard)
3. Semantic Similarity
4. Topic Relevance
5. Event Type Causality
6. Emotional Consistency

---

## Zep/Graphiti Integration Ideas 💡

### What Zep/Graphiti Does Well

**1. Hybrid Retrieval (300ms P95 latency)**
- **Vector search** - Semantic similarity using embeddings
- **BM25 search** - Keyword/full-text search
- **Graph traversal** - BFS/DFS through relationships
- **No LLM calls** during retrieval (fast!)

**2. Bi-Temporal Model**
- `valid_at` / `invalid_at` timestamps on facts
- Track when events **occurred** vs when **ingested**
- Historical state queries

**3. Episode-Based Architecture**
- Data arrives as discrete "episodes" (text or JSON)
- Real-time incremental updates
- Temporal edge invalidation (old relationships marked superseded)

### How to Adapt for AllegroGraph

**AllegroGraph already supports:**
- ✅ **SPARQL** for graph queries
- ✅ **Full-text search** (via `lmdb:match` predicates)
- ✅ **RDF reification** for edge metadata (scores, timestamps)
- ✅ **Property paths** for graph traversal
- ✅ **Vector embeddings** (via franz extensions or external systems)

**Implementation Plan:**

#### Phase 1: Hybrid Retrieval
```python
class HybridRetriever:
    """Zep-style hybrid retrieval for AllegroGraph"""

    def search(self, query: str, top_k: int = 20):
        # 1. Vector similarity search
        vector_results = self.vector_search(query, k=top_k)

        # 2. BM25 full-text search
        text_results = self.fulltext_search(query, k=top_k)

        # 3. Graph traversal from seed nodes
        graph_results = self.graph_traverse(seed_nodes, depth=2)

        # 4. Reciprocal Rank Fusion (RRF)
        merged = self.rrf_merge(vector_results, text_results, graph_results)

        # 5. Optional: Cross-encoder reranking
        reranked = self.rerank(merged, query)

        return reranked[:top_k]
```

#### Phase 2: Temporal Extensions
Add bi-temporal tracking to RDF triples:
```turtle
# Event with temporal metadata
:event_123 a feekg:Event ;
    feekg:eventType "credit_downgrade" ;
    feekg:occurred_at "2008-09-15"^^xsd:date ;
    feekg:ingested_at "2024-11-15T10:00:00"^^xsd:dateTime ;
    feekg:valid_from "2008-09-15"^^xsd:date ;
    feekg:valid_until "2008-09-20"^^xsd:date .

# Evolution link with temporal validity
:event_123 feekg:evolvesTo :event_456 .

# Reified to add metadata
[ a rdf:Statement ;
  rdf:subject :event_123 ;
  rdf:predicate feekg:evolvesTo ;
  rdf:object :event_456 ;
  feekg:score 0.85 ;
  feekg:valid_at "2008-09-16"^^xsd:date ;
  feekg:invalid_at "2008-10-01"^^xsd:date ;
  feekg:superseded_by :event_789_evolution ] .
```

#### Phase 3: Episode-Based Ingestion
```python
class EpisodeIngestion:
    """Ingest data as discrete episodes with incremental updates"""

    def ingest_episode(self, episode_data: dict):
        # Extract entities and events
        entities, events = self.extract(episode_data)

        # Integrate into existing graph
        self.integrate_entities(entities)  # Merge or update
        self.integrate_events(events)      # Add new, link to existing

        # Compute evolution links incrementally
        new_links = self.compute_evolution(events)

        # Mark superseded links as invalid
        self.invalidate_old_links(new_links)

        # Store with provenance
        self.store_with_provenance(episode_data['source'], episode_data['timestamp'])
```

---

## Next Steps 🎯

### Immediate (Fix Visualizations)
1. ✅ Create interactive visualizations (DONE)
2. ⚠️ Fix SPARQL FILTER syntax to use VALUES
3. ⚠️ Add event-entity relationships to graphs
4. ⚠️ Compute and visualize evolution links

### Short-term (Enhance Retrieval)
1. Implement hybrid retrieval (vector + BM25 + graph)
2. Add full-text search indexing to AllegroGraph
3. Integrate vector embeddings (OpenAI, SentenceTransformers)
4. Build retrieval API endpoint

### Medium-term (Graphiti-style Features)
1. Add bi-temporal tracking to all facts
2. Implement episode-based ingestion
3. Add temporal edge invalidation
4. Build data provenance tracking
5. Create temporal query interface

### Long-term (Production System)
1. Real-time event ingestion pipeline
2. Automated evolution link computation
3. GraphRAG retrieval system
4. Interactive dashboard (React + D3.js)
5. RESTful API for all operations

---

## Comparison: Your System vs. Graphiti

| **Feature** | **Your FE-EKG** | **Graphiti/Zep** | **Status** |
|-------------|-----------------|------------------|------------|
| Knowledge Graph | AllegroGraph (RDF) | Neo4j | ✅ Different but equivalent |
| Temporal Events | Events with dates | Episodes with timestamps | ✅ Have |
| Evolution Links | 6-method scoring | Temporal edges | ✅ Have (more sophisticated!) |
| Multi-dimensional Scores | Temporal, causality, semantic, etc. | Score + metadata | ✅ Have (better!) |
| Vector Search | ❌ Not implemented | ✅ Embeddings | ⚠️ Need to add |
| Full-text Search | ❌ Not implemented | ✅ BM25 | ⚠️ Need to add |
| Graph Traversal | ✅ SPARQL property paths | ✅ BFS/DFS | ✅ Have |
| Hybrid Retrieval | ❌ Not implemented | ✅ Vector+BM25+Graph | ⚠️ Need to build |
| Bi-temporal Tracking | ❌ Only event dates | ✅ valid_at/invalid_at | ⚠️ Need to add |
| Temporal Invalidation | ❌ Old edges stay | ✅ Edges can be superseded | ⚠️ Need to add |
| Data Provenance | ❌ Not tracked | ✅ Source tracking | ⚠️ Need to add |
| Incremental Updates | ⚠️ Batch only | ✅ Real-time | ⚠️ Need to build |
| Interactive Viz | ✅ Pyvis HTML | ❌ Not mentioned | ✅ You have this! |

**Your advantages:**
- More sophisticated evolution scoring (6 methods vs. simple temporal)
- Interactive visualizations already working
- RDF flexibility for complex relationships

**Graphiti advantages:**
- Hybrid retrieval is production-ready and fast
- Bi-temporal model for historical queries
- Real-time incremental updates

---

## Code Snippets to Get Started

### 1. Simple Full-Text Search in AllegroGraph
```python
# Add full-text index
backend.conn.createFreeTextIndex("event_descriptions", predicates=["feekg:description"])

# Query
query = """
PREFIX feekg: <http://feekg.org/ontology#>
PREFIX fti: <http://franz.com/ns/allegrograph/2.2/textindex/>

SELECT ?event ?desc
WHERE {
  ?event feekg:description ?desc .
  ?desc fti:match "bankruptcy" .
}
"""
```

### 2. Vector Embeddings (External)
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed event descriptions
events = backend.execute_query("SELECT ?e ?desc WHERE { ?e feekg:description ?desc }")
for event in events:
    embedding = model.encode(event['desc'])
    # Store in separate vector DB (Chroma, Pinecone, etc.) or as RDF literal
```

### 3. Hybrid Search Prototype
```python
def hybrid_search(query: str, top_k: int = 10):
    # 1. Vector search (cosine similarity)
    query_vec = model.encode(query)
    vector_results = vector_db.similarity_search(query_vec, k=top_k)

    # 2. Full-text search
    sparql = f"""
    SELECT ?event ?score WHERE {{
      ?event feekg:description ?desc .
      ?desc fti:match "{query}" .
      BIND(fti:relevance(?desc) AS ?score)
    }}
    LIMIT {top_k}
    """
    text_results = backend.execute_query(sparql)

    # 3. Reciprocal Rank Fusion
    def rrf_score(rank, k=60):
        return 1 / (k + rank)

    scores = defaultdict(float)
    for i, r in enumerate(vector_results):
        scores[r['id']] += rrf_score(i)
    for i, r in enumerate(text_results):
        scores[r['event']] += rrf_score(i)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

---

## Resources

### Graphiti/Zep
- **Paper:** "Zep: A Temporal Knowledge Graph Architecture for Agent Memory" ([arXiv:2501.13956](https://arxiv.org/abs/2501.13956))
- **GitHub:** [getzep/graphiti](https://github.com/getzep/graphiti)
- **Docs:** [help.getzep.com/graphiti](https://help.getzep.com/graphiti/graphiti/overview)

### AllegroGraph
- **Full-text search:** [franz.com/agraph/support/documentation/current/text-index.html](https://franz.com/agraph/support/documentation/current/text-index.html)
- **RDF reification:** [w3.org/TR/rdf11-mt/#reification](https://www.w3.org/TR/rdf11-mt/#reification)
- **Property paths:** [w3.org/TR/sparql11-property-paths](https://www.w3.org/TR/sparql11-property-paths/)

### Hybrid Retrieval
- **Reciprocal Rank Fusion:** "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (Cormack et al., 2009)
- **Maximal Marginal Relevance:** "The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries" (Carbonell & Goldstein, 1998)

---

**Last Updated:** 2025-11-15
**Status:** Interactive visualizations working, retrieval enhancements planned
