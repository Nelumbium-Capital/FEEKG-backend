"""
FE-EKG REST API Application

Flask REST API for serving knowledge graph data and visualizations
"""

import sys
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query.risk_analyzer import RiskAnalyzer
from viz.graph_viz import ThreeLayerVisualizer
from viz.plot_utils import (plot_risk_timeline, plot_evolution_heatmap,
                            plot_event_network, plot_component_breakdown,
                            plot_risk_distribution)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend access

    # ==========================================================================
    # HEALTH & INFO ENDPOINTS
    # ==========================================================================

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'FE-EKG API',
            'version': '1.0.0'
        })

    @app.route('/api/info', methods=['GET'])
    def info():
        """Get database information"""
        try:
            analyzer = RiskAnalyzer()
            overview = analyzer.get_database_overview()
            analyzer.close()

            return jsonify({
                'status': 'success',
                'data': overview
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # ENTITY ENDPOINTS
    # ==========================================================================

    @app.route('/api/entities', methods=['GET'])
    def get_entities():
        """Get all entities"""
        try:
            analyzer = RiskAnalyzer()
            query = """
            MATCH (e:Entity)
            RETURN e.entityId as id, e.name as name, e.type as type, e.description as description
            ORDER BY e.name
            """
            entities = analyzer.backend.execute_query(query)
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(entities),
                'data': entities
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/entities/<entity_id>', methods=['GET'])
    def get_entity(entity_id):
        """Get specific entity details"""
        try:
            analyzer = RiskAnalyzer()
            query = """
            MATCH (e:Entity {entityId: $entityId})
            RETURN e.entityId as id, e.name as name, e.type as type, e.description as description
            """
            entity = analyzer.backend.execute_query(query, {'entityId': entity_id})
            analyzer.close()

            if not entity:
                return jsonify({
                    'status': 'error',
                    'message': 'Entity not found'
                }), 404

            return jsonify({
                'status': 'success',
                'data': entity[0]
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/entities/<entity_id>/risks', methods=['GET'])
    def get_entity_risks(entity_id):
        """Get risks for a specific entity"""
        try:
            analyzer = RiskAnalyzer()
            query = """
            MATCH (e:Entity {entityId: $entityId})
            MATCH (r:Risk)-[:TARGETS_ENTITY]->(e)
            MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
            RETURN r.riskId as id, rt.label as type, r.score as score,
                   r.severity as severity, r.status as status
            ORDER BY r.score DESC
            """
            risks = analyzer.backend.execute_query(query, {'entityId': entity_id})
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(risks),
                'data': risks
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # EVENT ENDPOINTS
    # ==========================================================================

    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Get all events with optional filtering"""
        try:
            # Query parameters
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            event_type = request.args.get('type')

            analyzer = RiskAnalyzer()

            # Build query
            conditions = []
            params = {}

            if start_date:
                conditions.append("date(e.date) >= date($startDate)")
                params['startDate'] = start_date

            if end_date:
                conditions.append("date(e.date) <= date($endDate)")
                params['endDate'] = end_date

            if event_type:
                conditions.append("e.type = $eventType")
                params['eventType'] = event_type

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
            MATCH (e:Event)
            {where_clause}
            OPTIONAL MATCH (e)-[:HAS_ACTOR]->(actor:Entity)
            OPTIONAL MATCH (e)-[:HAS_TARGET]->(target:Entity)
            RETURN e.eventId as id, e.type as type, toString(e.date) as date,
                   e.description as description, e.confidence as confidence,
                   actor.name as actor, target.name as target
            ORDER BY e.date
            """

            events = analyzer.backend.execute_query(query, params)
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(events),
                'data': events
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/events/<event_id>', methods=['GET'])
    def get_event(event_id):
        """Get specific event details"""
        try:
            analyzer = RiskAnalyzer()
            query = """
            MATCH (e:Event {eventId: $eventId})
            OPTIONAL MATCH (e)-[:HAS_ACTOR]->(actor:Entity)
            OPTIONAL MATCH (e)-[:HAS_TARGET]->(target:Entity)
            RETURN e.eventId as id, e.type as type, toString(e.date) as date,
                   e.description as description, e.confidence as confidence,
                   actor.name as actor, target.name as target
            """
            event = analyzer.backend.execute_query(query, {'eventId': event_id})
            analyzer.close()

            if not event:
                return jsonify({
                    'status': 'error',
                    'message': 'Event not found'
                }), 404

            return jsonify({
                'status': 'success',
                'data': event[0]
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # EVOLUTION ENDPOINTS
    # ==========================================================================

    @app.route('/api/evolution/links', methods=['GET'])
    def get_evolution_links():
        """Get evolution links with optional filtering"""
        try:
            min_score = float(request.args.get('min_score', 0.0))
            limit = int(request.args.get('limit', 100))

            analyzer = RiskAnalyzer()
            links = analyzer.get_strongest_evolution_links(min_score=min_score, limit=limit)
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(links),
                'data': links
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/evolution/chains', methods=['GET'])
    def get_causal_chains():
        """Get causal event chains"""
        try:
            min_causality = float(request.args.get('min_causality', 0.5))
            min_length = int(request.args.get('min_length', 2))
            max_length = int(request.args.get('max_length', 5))

            analyzer = RiskAnalyzer()
            chains = analyzer.get_causal_chains(
                min_causality=min_causality,
                min_length=min_length,
                max_length=max_length
            )
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(chains),
                'data': chains
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/evolution/stats', methods=['GET'])
    def get_evolution_stats():
        """Get evolution statistics"""
        try:
            analyzer = RiskAnalyzer()
            stats = analyzer.get_evolution_statistics()
            analyzer.close()

            return jsonify({
                'status': 'success',
                'data': stats
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # RISK ENDPOINTS
    # ==========================================================================

    @app.route('/api/risks', methods=['GET'])
    def get_risks():
        """Get all risks"""
        try:
            analyzer = RiskAnalyzer()
            query = """
            MATCH (r:Risk)-[:HAS_RISK_TYPE]->(rt:RiskType)
            MATCH (r)-[:TARGETS_ENTITY]->(e:Entity)
            RETURN r.riskId as id, rt.label as type, r.score as score,
                   r.severity as severity, r.status as status,
                   e.name as targetEntity
            ORDER BY r.score DESC
            """
            risks = analyzer.backend.execute_query(query)
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(risks),
                'data': risks
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/risks/systemic', methods=['GET'])
    def get_systemic_risks():
        """Get systemic/contagion risks"""
        try:
            analyzer = RiskAnalyzer()
            systemic = analyzer.detect_systemic_risk()
            analyzer.close()

            return jsonify({
                'status': 'success',
                'count': len(systemic),
                'data': systemic
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/risks/distribution', methods=['GET'])
    def get_risk_distribution():
        """Get risk distribution statistics"""
        try:
            analyzer = RiskAnalyzer()
            distribution = analyzer.get_risk_distribution()
            analyzer.close()

            return jsonify({
                'status': 'success',
                'data': distribution
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # VISUALIZATION ENDPOINTS
    # ==========================================================================

    @app.route('/api/visualizations/three-layer', methods=['GET'])
    def get_three_layer_viz():
        """Generate three-layer graph visualization"""
        try:
            limit_events = int(request.args.get('limit', 15))

            viz = ThreeLayerVisualizer()
            fig = viz.create_three_layer_graph(limit_events=limit_events)
            viz.close()

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/visualizations/evolution-network', methods=['GET'])
    def get_evolution_network():
        """Generate evolution network visualization"""
        try:
            min_score = float(request.args.get('min_score', 0.4))

            viz = ThreeLayerVisualizer()
            fig = viz.create_evolution_network(min_score=min_score)
            viz.close()

            if fig is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No evolution links found'
                }), 404

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/visualizations/risk-propagation', methods=['GET'])
    def get_risk_propagation():
        """Generate risk propagation visualization"""
        try:
            viz = ThreeLayerVisualizer()
            fig = viz.create_risk_propagation_view()
            viz.close()

            if fig is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No risk data found'
                }), 404

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/visualizations/risk-timeline', methods=['GET'])
    def get_risk_timeline():
        """Generate risk timeline plot"""
        try:
            entity_name = request.args.get('entity', 'China Evergrande Group')

            fig = plot_risk_timeline(entity_name=entity_name)

            if fig is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No timeline data found'
                }), 404

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/visualizations/evolution-heatmap', methods=['GET'])
    def get_evolution_heatmap():
        """Generate evolution heatmap"""
        try:
            fig = plot_evolution_heatmap()

            if fig is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No evolution data found'
                }), 404

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/visualizations/component-breakdown', methods=['GET'])
    def get_component_breakdown():
        """Generate component breakdown plot"""
        try:
            fig = plot_component_breakdown()

            if fig is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No statistics found'
                }), 404

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{img_base64}'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==========================================================================
    # GRAPH DATA ENDPOINTS (for D3.js/Cytoscape.js frontend)
    # ==========================================================================

    @app.route('/api/graph/data', methods=['GET'])
    def get_graph_data():
        """Get graph data in nodes/edges format for frontend visualization"""
        try:
            limit_events = int(request.args.get('limit', 20))

            viz = ThreeLayerVisualizer()
            data = viz.fetch_graph_data(limit_events=limit_events)
            viz.close()

            # Transform to nodes/edges format
            nodes = []
            edges = []

            # Add entity nodes
            for entity in data['nodes']['entities']:
                nodes.append({
                    'id': entity['id'],
                    'label': entity['name'],
                    'type': 'entity',
                    'group': 'entity',
                    'data': entity
                })

            # Add event nodes
            for event in data['nodes']['events']:
                nodes.append({
                    'id': event['id'],
                    'label': event['type'],
                    'type': 'event',
                    'group': 'event',
                    'data': event
                })

            # Add risk nodes
            for risk in data['nodes']['risks']:
                nodes.append({
                    'id': risk['id'],
                    'label': risk['type'],
                    'type': 'risk',
                    'group': 'risk',
                    'data': risk
                })

            # Add evolution edges
            for edge in data['edges']['evolution']:
                edges.append({
                    'source': edge['source'],
                    'target': edge['target'],
                    'type': 'evolves_to',
                    'weight': edge.get('score', 0.5),
                    'data': edge
                })

            # Add event-entity edges
            for edge in data['edges']['event_entity']:
                edges.append({
                    'source': edge['source'],
                    'target': edge['target'],
                    'type': edge['type'].lower(),
                    'data': edge
                })

            # Add risk-entity edges
            for edge in data['edges']['risk_entity']:
                edges.append({
                    'source': edge['source'],
                    'target': edge['target'],
                    'type': 'targets',
                    'data': edge
                })

            return jsonify({
                'status': 'success',
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'entities': len(data['nodes']['entities']),
                    'events': len(data['nodes']['events']),
                    'risks': len(data['nodes']['risks']),
                    'evolution_links': len(data['edges']['evolution'])
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 70)
    print("FE-EKG REST API Server")
    print("=" * 70)
    print("\nStarting server on http://localhost:5000")
    print("\nAPI Documentation:")
    print("  Health:       GET  /health")
    print("  Info:         GET  /api/info")
    print("  Entities:     GET  /api/entities")
    print("  Events:       GET  /api/events")
    print("  Evolution:    GET  /api/evolution/links")
    print("  Risks:        GET  /api/risks")
    print("  Graph Data:   GET  /api/graph/data")
    print("  Viz (3-layer):GET  /api/visualizations/three-layer")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
