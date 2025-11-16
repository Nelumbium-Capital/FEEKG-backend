"""
Optimized Knowledge Graph Visualizations with CSV Traceability
Clean, professional D3.js visualizations leveraging full data provenance
"""

import sys
import os
import json
from typing import Optional, Dict, List
from collections import defaultdict, Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.graph_backend import get_connection


class OptimizedVisualizer:
    """Generate optimized, professional visualizations with data quality"""

    def __init__(self):
        """Initialize with AllegroGraph connection"""
        self.backend = get_connection()

    def close(self):
        """Close database connection"""
        self.backend.close()

    def fetch_clean_graph_data(self, max_events: int = 150) -> Dict:
        """
        Fetch clean, validated graph data with CSV provenance

        Args:
            max_events: Maximum events to include

        Returns:
            Dictionary with clean nodes and links
        """
        print(f"Fetching clean data (max {max_events} events with provenance)...")

        # Fetch entities with clean labels
        entity_query = """
        PREFIX feekg: <http://feekg.org/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?entity ?label ?type
        WHERE {
          ?entity a feekg:Entity .
          ?entity rdfs:label ?label .
          ?entity feekg:entityType ?type .
        }
        ORDER BY ?label
        """
        entities = self.backend.execute_query(entity_query)

        # Clean and deduplicate entities
        entity_nodes = {}
        for e in entities:
            label = e.get('label', '').strip(' "')
            if not label or label == 'None':
                continue

            entity_type = e.get('type', 'unknown').strip(' "').lower()

            if label not in entity_nodes:
                entity_nodes[label] = {
                    'id': label,
                    'label': label,
                    'type': entity_type,
                    'group': 'entity',
                    'uri': e['entity']
                }

        print(f"  ✓ Loaded {len(entity_nodes)} clean entities")

        # Fetch events with CSV metadata
        event_query = f"""
        PREFIX feekg: <http://feekg.org/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?event ?label ?type ?date ?desc
               ?csvRow ?csvFile ?confidence ?method
        WHERE {{
          ?event a feekg:Event .
          OPTIONAL {{ ?event rdfs:label ?label }}
          OPTIONAL {{ ?event feekg:eventType ?type }}
          OPTIONAL {{ ?event feekg:date ?date }}
          OPTIONAL {{ ?event feekg:description ?desc }}
          OPTIONAL {{ ?event feekg:csvRowNumber ?csvRow }}
          OPTIONAL {{ ?event feekg:csvFilename ?csvFile }}
          OPTIONAL {{ ?event feekg:classificationConfidence ?confidence }}
          OPTIONAL {{ ?event feekg:classificationMethod ?method }}
        }}
        ORDER BY ?date
        LIMIT {max_events}
        """
        events = self.backend.execute_query(event_query)

        event_nodes = {}
        event_uri_to_id = {}

        for i, e in enumerate(events):
            event_id = f"evt_{i}"
            label = (e.get('label') or f"Event {i}").strip(' "')[:50]
            event_type = (e.get('type') or 'unknown').strip(' "')
            date = (e.get('date') or 'unknown').strip(' "')
            desc = (e.get('desc') or '').strip(' "')[:200]

            # CSV metadata
            csv_row = e.get('csvRow', '').strip(' "')
            csv_file = e.get('csvFile', '').strip(' "')
            confidence = e.get('confidence', '').strip(' "')
            method = e.get('method', '').strip(' "')

            event_nodes[event_id] = {
                'id': event_id,
                'label': label,
                'type': event_type,
                'date': date,
                'description': desc,
                'group': 'event',
                'uri': e['event'],
                # Provenance metadata
                'csvRow': csv_row,
                'csvFile': csv_file,
                'confidence': confidence,
                'method': method
            }
            event_uri_to_id[e['event']] = event_id

        print(f"  ✓ Loaded {len(event_nodes)} events with provenance")

        # Fetch relationships
        links = []

        # Event → Entity (involves)
        involves_query = """
        PREFIX feekg: <http://feekg.org/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?event ?entity ?entityLabel
        WHERE {
          ?event feekg:involves ?entity .
          ?entity rdfs:label ?entityLabel .
        }
        LIMIT 500
        """

        try:
            involves = self.backend.execute_query(involves_query)
            for rel in involves:
                event_uri = rel['event']
                entity_label = rel['entityLabel'].strip(' "')

                if event_uri in event_uri_to_id and entity_label in entity_nodes:
                    links.append({
                        'source': event_uri_to_id[event_uri],
                        'target': entity_label,
                        'type': 'involves',
                        'strength': 0.8
                    })
            print(f"  ✓ Loaded {len(involves)} relationships")
        except Exception as e:
            print(f"  ⚠ Relationship loading: {str(e)[:100]}")

        # Calculate statistics
        entity_type_counts = Counter(n['type'] for n in entity_nodes.values())
        event_type_counts = Counter(n['type'] for n in event_nodes.values())

        all_nodes = list(entity_nodes.values()) + list(event_nodes.values())

        return {
            'nodes': all_nodes,
            'links': links,
            'stats': {
                'entities': len(entity_nodes),
                'events': len(event_nodes),
                'relationships': len(links),
                'entityTypes': dict(entity_type_counts),
                'eventTypes': dict(event_type_counts)
            }
        }

    def create_optimized_visualization(self,
                                       max_events: int = 100,
                                       save_path: Optional[str] = None) -> str:
        """
        Create optimized D3.js visualization with CSV provenance

        Args:
            max_events: Maximum events to visualize
            save_path: Path to save HTML file

        Returns:
            Path to generated file
        """
        if save_path is None:
            save_path = "results/optimized_knowledge_graph.html"

        # Fetch clean data
        data = self.fetch_clean_graph_data(max_events)

        # Generate HTML
        html_content = self._generate_optimized_html(data)

        # Save
        with open(save_path, 'w') as f:
            f.write(html_content)

        print(f"\n✅ Optimized visualization created!")
        print(f"📊 Stats: {data['stats']['entities']} entities, {data['stats']['events']} events, {data['stats']['relationships']} links")
        print(f"📂 Open: file://{os.path.abspath(save_path)}")

        return save_path

    def _generate_optimized_html(self, data: Dict) -> str:
        """Generate optimized HTML with modern UI"""

        graph_json = json.dumps(data, indent=2)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Event Knowledge Graph - Optimized</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            overflow: hidden;
        }}

        #graph {{
            width: 100vw;
            height: 100vh;
        }}

        .controls {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            min-width: 320px;
            max-height: 90vh;
            overflow-y: auto;
        }}

        .controls h1 {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .controls .subtitle {{
            font-size: 13px;
            color: #666;
            margin-bottom: 20px;
        }}

        .stats {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
        }}

        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
            font-size: 13px;
            color: #333;
        }}

        .stat-row:last-child {{
            border-bottom: none;
        }}

        .stat-value {{
            font-weight: 600;
            color: #667eea;
        }}

        .control-section {{
            margin-bottom: 20px;
        }}

        .control-section h3 {{
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 12px;
        }}

        .controls button {{
            width: 100%;
            padding: 12px;
            margin: 6px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .controls button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}

        .controls button:active {{
            transform: translateY(0);
        }}

        .controls button.secondary {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}

        .search-box {{
            width: 100%;
            padding: 10px 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 13px;
            transition: border-color 0.2s;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .legend {{
            margin-top: 20px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 13px;
            color: #333;
        }}

        .legend-color {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            margin-right: 12px;
            border: 2px solid rgba(0, 0, 0, 0.1);
        }}

        .tooltip {{
            position: fixed;
            background: rgba(255, 255, 255, 0.98);
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 16px;
            font-size: 13px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 2000;
            max-width: 400px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            color: #333;
        }}

        .tooltip.show {{
            opacity: 1;
        }}

        .tooltip strong {{
            color: #667eea;
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
        }}

        .tooltip .meta {{
            color: #666;
            font-size: 11px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #e9ecef;
        }}

        .tooltip .provenance {{
            background: #f8f9fa;
            padding: 8px;
            border-radius: 6px;
            margin-top: 8px;
            font-size: 11px;
        }}

        .node {{
            cursor: pointer;
            transition: all 0.2s;
        }}

        .node:hover {{
            stroke-width: 4px !important;
        }}

        .node.highlighted {{
            stroke: #ffd700 !important;
            stroke-width: 5px !important;
        }}

        .link {{
            stroke-opacity: 0.4;
            transition: stroke-opacity 0.2s;
        }}

        .link.highlight {{
            stroke-opacity: 0.9;
            stroke-width: 3px;
            stroke: #667eea;
        }}

        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 32px 48px;
            border-radius: 16px;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
            z-index: 3000;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="controls">
        <h1>📊 FE-EKG Knowledge Graph</h1>
        <div class="subtitle">Financial Event Evolution with CSV Provenance</div>

        <div class="stats">
            <div class="stat-row">
                <span>Entities</span>
                <span class="stat-value" id="entityCount">0</span>
            </div>
            <div class="stat-row">
                <span>Events</span>
                <span class="stat-value" id="eventCount">0</span>
            </div>
            <div class="stat-row">
                <span>Relationships</span>
                <span class="stat-value" id="linkCount">0</span>
            </div>
        </div>

        <div class="control-section">
            <h3>🔍 Search</h3>
            <input type="text" class="search-box" id="search" placeholder="Search entities or events...">
        </div>

        <div class="control-section">
            <h3>🎮 Controls</h3>
            <button onclick="resetView()">Reset View</button>
            <button onclick="togglePhysics()" class="secondary">Toggle Physics</button>
            <button onclick="centerOnEntity()" class="secondary">Center on Entity</button>
        </div>

        <div class="legend">
            <h3 style="font-size: 14px; color: #333; margin-bottom: 12px;">Legend</h3>
            <div class="legend-item">
                <div class="legend-color" style="background: #3b82f6;"></div>
                <span>Banks & Financial Institutions</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #8b5cf6;"></div>
                <span>Regulators & Government</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ec4899;"></div>
                <span>Investment Banks</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f59e0b;"></div>
                <span>Events</span>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>
    <svg id="graph"></svg>

    <script>
        // Graph data with CSV provenance
        const graphData = {graph_json};

        // Setup
        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g');

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});

        svg.call(zoom);

        // Color mapping
        const colorMap = {{
            'bank': '#3b82f6',
            'regulator': '#8b5cf6',
            'investment_bank': '#ec4899',
            'company': '#10b981',
            'ratingagency': '#f59e0b',
            'insurance': '#06b6d4',
            'person': '#f97316',
            'exchange': '#6366f1',
            'unknown': '#94a3b8',
            'event': '#f59e0b'
        }};

        function getNodeColor(d) {{
            if (d.group === 'entity') {{
                return colorMap[d.type] || colorMap['unknown'];
            }}
            return colorMap['event'];
        }}

        function getNodeSize(d) {{
            return d.group === 'entity' ? 14 : 9;
        }}

        // Force simulation
        let physicsEnabled = true;
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(120).strength(d => d.strength || 0.6))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => getNodeSize(d) + 10));

        // Draw links
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.links)
            .join('line')
            .attr('class', 'link')
            .attr('stroke', '#64748b')
            .attr('stroke-width', 1.5);

        // Draw link labels
        const linkLabels = g.append('g')
            .selectAll('text')
            .data(graphData.links)
            .join('text')
            .attr('class', 'link-label')
            .attr('font-size', 9)
            .attr('fill', '#94a3b8')
            .attr('text-anchor', 'middle')
            .attr('dy', -3)
            .style('pointer-events', 'none')
            .style('text-shadow', '0 0 3px rgba(0,0,0,0.8)')
            .text(d => d.type || 'related');

        // Draw nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .join('circle')
            .attr('class', 'node')
            .attr('r', getNodeSize)
            .attr('fill', getNodeColor)
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip)
            .on('click', nodeClicked);

        // Labels for entities only
        const labels = g.append('g')
            .selectAll('text')
            .data(graphData.nodes.filter(d => d.group === 'entity'))
            .join('text')
            .text(d => d.label)
            .attr('font-size', 11)
            .attr('font-weight', 600)
            .attr('fill', '#fff')
            .attr('text-anchor', 'middle')
            .attr('dy', -18)
            .style('pointer-events', 'none')
            .style('text-shadow', '0 1px 3px rgba(0,0,0,0.5)');

        // Update positions on tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            linkLabels
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});

        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}

        // Tooltip
        const tooltip = d3.select('#tooltip');

        function showTooltip(event, d) {{
            let html = `<strong>${{d.label}}</strong>`;
            html += `<div class="meta">Type: ${{d.type}}</div>`;

            if (d.date && d.date !== 'unknown') {{
                html += `<div class="meta">Date: ${{d.date}}</div>`;
            }}

            if (d.description) {{
                html += `<div style="margin-top: 8px; font-size: 12px; line-height: 1.5;">${{d.description}}</div>`;
            }}

            // CSV Provenance
            if (d.csvRow && d.csvRow !== 'None') {{
                html += `<div class="provenance">`;
                html += `<strong style="font-size: 11px;">📄 Data Source</strong><br>`;
                html += `Row: ${{d.csvRow}}<br>`;
                if (d.confidence) html += `Confidence: ${{(parseFloat(d.confidence) * 100).toFixed(1)}}%<br>`;
                if (d.method) html += `Method: ${{d.method}}`;
                html += `</div>`;
            }}

            tooltip
                .html(html)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 15) + 'px')
                .classed('show', true);

            // Highlight connected links
            link.classed('highlight', l => l.source === d || l.target === d);
            node.classed('highlighted', n => n === d);
        }}

        function hideTooltip() {{
            tooltip.classed('show', false);
            link.classed('highlight', false);
            node.classed('highlighted', false);
        }}

        function nodeClicked(event, d) {{
            console.log('Node clicked:', d);
            // Could add more interaction here
        }}

        // Controls
        function resetView() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            if (physicsEnabled) {{
                simulation.alpha(1).restart();
            }} else {{
                simulation.stop();
            }}
        }}

        function centerOnEntity() {{
            const lehman = graphData.nodes.find(n => n.label.includes('Lehman'));
            if (lehman) {{
                svg.transition().duration(750).call(
                    zoom.transform,
                    d3.zoomIdentity
                        .translate(width/2, height/2)
                        .scale(1.5)
                        .translate(-lehman.x, -lehman.y)
                );
            }}
        }}

        // Search functionality
        document.getElementById('search').addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();

            node.attr('opacity', d => {{
                if (!searchTerm) return 1;
                return d.label.toLowerCase().includes(searchTerm) ? 1 : 0.2;
            }});

            labels.attr('opacity', d => {{
                if (!searchTerm) return 1;
                return d.label.toLowerCase().includes(searchTerm) ? 1 : 0.2;
            }});
        }});

        // Update stats
        document.getElementById('entityCount').textContent = graphData.stats.entities;
        document.getElementById('eventCount').textContent = graphData.stats.events;
        document.getElementById('linkCount').textContent = graphData.stats.relationships;

        // Initial zoom to fit
        setTimeout(() => {{
            const bounds = g.node().getBBox();
            const fullWidth = bounds.width;
            const fullHeight = bounds.height;
            const midX = bounds.x + fullWidth / 2;
            const midY = bounds.y + fullHeight / 2;

            const scale = 0.9 / Math.max(fullWidth / width, fullHeight / height);
            const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

            svg.call(zoom.transform, d3.zoomIdentity
                .translate(translate[0], translate[1])
                .scale(scale));
        }}, 1000);
    </script>
</body>
</html>"""


if __name__ == "__main__":
    viz = OptimizedVisualizer()

    print("=" * 70)
    print("Creating Optimized Knowledge Graph Visualization")
    print("=" * 70)
    print()

    viz.create_optimized_visualization(
        max_events=100,
        save_path="results/optimized_knowledge_graph.html"
    )

    viz.close()

    print()
    print("=" * 70)
    print("✅ Done! Open in browser:")
    print("   results/optimized_knowledge_graph.html")
    print("=" * 70)
