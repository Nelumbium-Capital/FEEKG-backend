// ============================================================
// FE-EKG Neo4j Schema: Financial Event Evolution Knowledge Graph
// Three-Layer Architecture: Entity → Event → Risk
// ============================================================

// ========== NODE CONSTRAINTS & INDEXES ==========

// LAYER 1: ENTITY
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.entityId IS UNIQUE;
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);

// LAYER 2: EVENT
CREATE CONSTRAINT event_id IF NOT EXISTS FOR (ev:Event) REQUIRE ev.eventId IS UNIQUE;
CREATE INDEX event_date IF NOT EXISTS FOR (ev:Event) ON (ev.date);
CREATE INDEX event_type IF NOT EXISTS FOR (ev:Event) ON (ev.type);

// LAYER 3: RISK
CREATE CONSTRAINT risk_id IF NOT EXISTS FOR (r:Risk) REQUIRE r.riskId IS UNIQUE;
CREATE INDEX risk_score IF NOT EXISTS FOR (r:Risk) ON (r.score);
CREATE INDEX risk_status IF NOT EXISTS FOR (r:Risk) ON (r.status);

// RISK TYPE
CREATE CONSTRAINT risk_type_name IF NOT EXISTS FOR (rt:RiskType) REQUIRE rt.name IS UNIQUE;

// RISK SNAPSHOT
CREATE INDEX snapshot_time IF NOT EXISTS FOR (rs:RiskSnapshot) ON (rs.time);

// ========== NODE LABELS ==========

// Entity subtypes (optional, for better querying)
// :Entity:Company
// :Entity:Bank
// :Entity:Fund
// :Entity:RatingAgency
// :Entity:Regulator
// :Entity:Person

// ========== RELATIONSHIP TYPES ==========

// Entity Layer Relationships
// (Entity)-[:RELATED_TO]->(Entity)
// (Entity)-[:OWNS]->(Entity)
// (Entity)-[:CONTROLS]->(Entity)
// (Entity)-[:SUPPLIES]->(Entity)

// Event Layer Relationships
// (Event)-[:HAS_ACTOR]->(Entity)
// (Event)-[:HAS_TARGET]->(Entity)
// (Event)-[:EVOLVES_TO {confidence: float, type: string}]->(Event)

// Risk Layer Relationships
// (Event)-[:INCREASES_RISK_OF]->(Risk)
// (Risk)-[:MATERIALIZES_AS]->(Event)
// (Risk)-[:TARGETS_ENTITY]->(Entity)
// (Risk)-[:HAS_RISK_TYPE]->(RiskType)
// (Risk)-[:TRANSITIONS_TO {probability: float}]->(Risk)
// (RiskSnapshot)-[:SNAP_OF]->(Risk)

// ========== INITIAL RISK TYPES ==========
// Create the 12 risk types from the paper

MERGE (rt1:RiskType {name: 'LiquidityRisk', label: 'Liquidity Risk'});
MERGE (rt2:RiskType {name: 'CreditRisk', label: 'Credit Risk'});
MERGE (rt3:RiskType {name: 'OperationalRisk', label: 'Operational Risk'});
MERGE (rt4:RiskType {name: 'MarketRisk', label: 'Market Risk'});
MERGE (rt5:RiskType {name: 'SystemicRisk', label: 'Systemic Risk'});
MERGE (rt6:RiskType {name: 'ContagionRisk', label: 'Contagion Risk'});
MERGE (rt7:RiskType {name: 'SolvencyRisk', label: 'Solvency Risk'});
MERGE (rt8:RiskType {name: 'ReputationalRisk', label: 'Reputational Risk'});
MERGE (rt9:RiskType {name: 'RegulatoryRisk', label: 'Regulatory Risk'});
MERGE (rt10:RiskType {name: 'StrategicRisk', label: 'Strategic Risk'});
MERGE (rt11:RiskType {name: 'ComplianceRisk', label: 'Compliance Risk'});
MERGE (rt12:RiskType {name: 'GeopoliticalRisk', label: 'Geopolitical Risk'});

// ========== PROPERTY SCHEMAS ==========

// Entity properties:
// - entityId (unique)
// - name
// - type (Company, Bank, Fund, etc.)
// - createdAt
// - updatedAt

// Event properties:
// - eventId (unique)
// - type (debt_default, credit_downgrade, etc.)
// - date
// - description
// - source
// - sourceUrl
// - confidence
// - createdAt

// Risk properties:
// - riskId (unique)
// - score (0.0-1.0)
// - severity (low, medium, high, critical)
// - probability (0.0-1.0)
// - status (open, mitigated, materialized, closed)
// - detectedDate
// - createdAt
// - updatedAt

// RiskSnapshot properties:
// - snapshotId
// - time (timestamp)
// - score (0.0-1.0)
// - severity

// ========== EXAMPLE DATA MODEL ==========

// Example 1: Event → Entity
// (evt1:Event {type:'debt_default'})-[:HAS_ACTOR]->(evergrande:Entity:Company)
// (evt1)-[:HAS_TARGET]->(minsheng:Entity:Bank)

// Example 2: Event Evolution
// (evt1:Event)-[:EVOLVES_TO {confidence:0.8, type:'temporal'}]->(evt2:Event)

// Example 3: Event → Risk → Entity
// (evt1:Event)-[:INCREASES_RISK_OF]->(risk1:Risk)
// (risk1)-[:HAS_RISK_TYPE]->(CreditRisk:RiskType)
// (risk1)-[:TARGETS_ENTITY]->(evergrande:Entity)

// Example 4: Risk Snapshot
// (snap1:RiskSnapshot {time:'2021-09-20T12:00:00', score:0.7})-[:SNAP_OF]->(risk1:Risk)

// ========== USEFUL QUERIES FOR VALIDATION ==========

// Count nodes by type
// MATCH (n) RETURN labels(n) as Type, count(n) as Count ORDER BY Count DESC;

// List all risk types
// MATCH (rt:RiskType) RETURN rt.name, rt.label;

// Find event evolution chains
// MATCH path=(e1:Event)-[:EVOLVES_TO*1..5]->(e2:Event)
// RETURN path LIMIT 10;

// Find risks by entity
// MATCH (e:Entity {name:'Evergrande'})<-[:TARGETS_ENTITY]-(r:Risk)
// RETURN r.riskId, r.score, r.status;
