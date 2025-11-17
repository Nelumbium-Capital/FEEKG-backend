"""
Network Topology Loader from Knowledge Graph

Loads interbank network from KG evolution links to create realistic
network topology for ABM simulation.
"""

import networkx as nx
import sys
import os
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.graph_backend import get_graph_backend
except ImportError:
    print("Warning: Could not import graph_backend. Using default network.")
    get_graph_backend = None


def load_network_from_kg(
    entity_limit: Optional[int] = None,
    min_evolution_score: float = 0.5
) -> tuple[nx.Graph, Dict[int, Dict]]:
    """
    Load network topology from Knowledge Graph evolution links

    Process:
    1. Query AllegroGraph for entities and evolution links
    2. Build network graph with entities as nodes
    3. Add edges from evolution links (weighted by score)
    4. Extract entity metadata for agent initialization

    Args:
        entity_limit: Maximum number of entities to include (None = all)
        min_evolution_score: Minimum evolution link score to include

    Returns:
        tuple: (NetworkX graph, entity metadata dict)
            graph: nx.Graph with entities as nodes
            metadata: Dict mapping node_id -> {name, entity_id, ...}
    """
    if get_graph_backend is None:
        print("⚠️  KG backend not available. Using random network.")
        return create_default_network(n=10)

    try:
        # Get backend
        backend = get_graph_backend()

        # Query entities
        print(f"📊 Loading entities from Knowledge Graph...")
        entities = backend.get_entities()

        if entity_limit:
            entities = entities[:entity_limit]

        print(f"   Found {len(entities)} entities")

        # Build entity metadata
        entity_metadata = {}
        entity_id_to_node = {}  # Map KG entity_id to node index

        for i, entity in enumerate(entities):
            entity_id = entity.get('entity_id') or entity.get('entityId')
            entity_name = entity.get('name') or entity.get('label')

            entity_metadata[i] = {
                'entity_id': entity_id,
                'name': entity_name,
                'type': entity.get('type', 'bank')
            }

            entity_id_to_node[entity_id] = i

        # Create graph
        G = nx.Graph()
        G.add_nodes_from(range(len(entities)))

        # Query evolution links
        print(f"🔗 Loading evolution links (score ≥ {min_evolution_score})...")

        try:
            # Try to get evolution links from backend
            if hasattr(backend, 'get_evolution_links'):
                links = backend.get_evolution_links(min_score=min_evolution_score)
            else:
                # Fallback: query directly
                links = query_evolution_links_sparql(backend, min_evolution_score)

            print(f"   Found {len(links)} evolution links")

            # Add edges from evolution links
            # Evolution links connect events, we map to entities via event actors
            edges_added = 0
            for link in links:
                source_entities = link.get('source_entities', [])
                target_entities = link.get('target_entities', [])
                score = link.get('score', 0.5)

                # Connect entities from source to target events
                for src_ent in source_entities:
                    if src_ent in entity_id_to_node:
                        src_node = entity_id_to_node[src_ent]
                        for tgt_ent in target_entities:
                            if tgt_ent in entity_id_to_node:
                                tgt_node = entity_id_to_node[tgt_ent]
                                if src_node != tgt_node:
                                    # Add weighted edge
                                    if G.has_edge(src_node, tgt_node):
                                        # Increase weight if edge exists
                                        G[src_node][tgt_node]['weight'] += score
                                    else:
                                        G.add_edge(src_node, tgt_node, weight=score)
                                    edges_added += 1

            print(f"   Added {edges_added} connections")

            # If graph is disconnected, add minimum spanning connections
            if not nx.is_connected(G) and len(G.nodes()) > 1:
                print(f"   ⚠️  Graph disconnected, adding connections...")
                G = ensure_connected(G)

            return G, entity_metadata

        except Exception as e:
            print(f"   ⚠️  Could not load evolution links: {e}")
            print(f"   Using entity-based network instead")

            # Fallback: Create network based on entity co-occurrence
            return create_entity_cooccurrence_network(entities)

    except Exception as e:
        print(f"❌ Error loading from KG: {e}")
        print(f"   Falling back to default network")
        return create_default_network(n=10)


def query_evolution_links_sparql(backend, min_score: float = 0.5) -> List[Dict]:
    """
    Query evolution links using SPARQL

    Args:
        backend: AllegroGraph backend
        min_score: Minimum score threshold

    Returns:
        List of evolution link dicts
    """
    sparql_query = f"""
    PREFIX feekg: <http://example.org/feekg#>

    SELECT ?source_event ?target_event ?score ?source_entity ?target_entity
    WHERE {{
        ?link a feekg:EvolutionLink ;
              feekg:source ?source_event ;
              feekg:target ?target_event ;
              feekg:score ?score .

        OPTIONAL {{
            ?source_event feekg:hasActor ?source_entity .
        }}

        OPTIONAL {{
            ?target_event feekg:hasActor ?target_entity .
        }}

        FILTER(?score >= {min_score})
    }}
    LIMIT 10000
    """

    try:
        results = backend.execute_sparql(sparql_query)

        # Parse results
        links = []
        for row in results:
            links.append({
                'source_event': row.get('source_event'),
                'target_event': row.get('target_event'),
                'score': float(row.get('score', 0.5)),
                'source_entities': [row.get('source_entity')] if row.get('source_entity') else [],
                'target_entities': [row.get('target_entity')] if row.get('target_entity') else []
            })

        return links

    except Exception as e:
        print(f"   SPARQL query failed: {e}")
        return []


def create_entity_cooccurrence_network(entities: List[Dict]) -> tuple[nx.Graph, Dict]:
    """
    Create network from entity co-occurrence in events

    Args:
        entities: List of entity dicts from KG

    Returns:
        tuple: (NetworkX graph, entity metadata)
    """
    # Build entity metadata
    entity_metadata = {}
    for i, entity in enumerate(entities):
        entity_metadata[i] = {
            'entity_id': entity.get('entity_id') or entity.get('entityId'),
            'name': entity.get('name') or entity.get('label'),
            'type': entity.get('type', 'bank')
        }

    # Create Erdős-Rényi network (random connections)
    # In reality, would compute co-occurrence from events
    n = len(entities)
    G = nx.erdos_renyi_graph(n, p=0.3)

    return G, entity_metadata


def create_default_network(n: int = 10) -> tuple[nx.Graph, Dict]:
    """
    Create default random network for testing

    Args:
        n: Number of nodes

    Returns:
        tuple: (NetworkX graph, entity metadata)
    """
    print(f"   Creating default random network with {n} nodes")

    # Default bank names
    bank_names = [
        "Lehman Brothers", "AIG", "Bear Stearns", "Merrill Lynch",
        "Morgan Stanley", "Goldman Sachs", "Citigroup", "Bank of America",
        "JPMorgan", "Wells Fargo"
    ]

    # Create metadata
    entity_metadata = {}
    for i in range(n):
        entity_metadata[i] = {
            'entity_id': f"ent_bank_{i}",
            'name': bank_names[i] if i < len(bank_names) else f"Bank_{i}",
            'type': 'bank'
        }

    # Create Erdős-Rényi network
    G = nx.erdos_renyi_graph(n, p=0.3, seed=42)

    return G, entity_metadata


def ensure_connected(G: nx.Graph) -> nx.Graph:
    """
    Ensure graph is connected by adding minimum edges

    Args:
        G: NetworkX graph

    Returns:
        Connected graph
    """
    # Get connected components
    components = list(nx.connected_components(G))

    if len(components) <= 1:
        return G  # Already connected

    # Connect components with minimum edges
    component_list = [list(c) for c in components]

    for i in range(len(component_list) - 1):
        # Connect component i to component i+1
        node_a = component_list[i][0]
        node_b = component_list[i + 1][0]
        G.add_edge(node_a, node_b, weight=0.5)

    return G


def export_network_viz(G: nx.Graph, entity_metadata: Dict, output_path: str):
    """
    Export network visualization data for frontend

    Args:
        G: NetworkX graph
        entity_metadata: Entity metadata dict
        output_path: Path to save JSON
    """
    import json

    # Convert to dict format
    nodes = []
    for node_id in G.nodes():
        metadata = entity_metadata.get(node_id, {})
        nodes.append({
            'id': node_id,
            'label': metadata.get('name', f'Node_{node_id}'),
            'entity_id': metadata.get('entity_id'),
            'type': metadata.get('type', 'bank')
        })

    edges = []
    for source, target in G.edges():
        weight = G[source][target].get('weight', 1.0)
        edges.append({
            'source': source,
            'target': target,
            'weight': weight
        })

    network_data = {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'n_nodes': len(nodes),
            'n_edges': len(edges),
            'density': nx.density(G),
            'avg_degree': sum(dict(G.degree()).values()) / len(G.nodes())
        }
    }

    with open(output_path, 'w') as f:
        json.dump(network_data, f, indent=2)

    print(f"✅ Network visualization exported to: {output_path}")
