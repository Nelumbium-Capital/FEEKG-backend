/*
 * FE-EKG Risk Analysis Queries
 *
 * Cypher templates for querying the three-layer knowledge graph
 * Based on the FEEKG paper's risk identification methods
 */

-- =============================================================================
-- 1. BASIC OVERVIEW QUERIES
-- =============================================================================

-- 1.1 Database Overview
-- Shows all node types and their counts
MATCH (n)
RETURN labels(n) as NodeType, count(n) as Count
ORDER BY Count DESC;

-- 1.2 Relationship Overview
-- Shows all relationship types and their counts
MATCH ()-[r]->()
RETURN type(r) as RelationType, count(r) as Count
ORDER BY Count DESC;

-- 1.3 Risk Type Distribution
-- Shows which risk types are most common
MATCH (r:Risk)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN rt.label as RiskType, count(r) as RiskCount
ORDER BY RiskCount DESC;


-- =============================================================================
-- 2. ENTITY RISK QUERIES
-- =============================================================================

-- 2.1 Entity Risk Profile
-- Get all risks targeting a specific entity (e.g., Evergrande)
MATCH (e:Entity {name: 'China Evergrande Group'})
MATCH (r:Risk)-[:TARGETS_ENTITY]->(e)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN e.name as Entity,
       rt.label as RiskType,
       r.score as RiskScore,
       r.severity as Severity,
       r.status as Status
ORDER BY r.score DESC;

-- 2.2 High-Risk Entities
-- Find entities with multiple high-severity risks
MATCH (e:Entity)<-[:TARGETS_ENTITY]-(r:Risk)
WHERE r.severity IN ['high', 'critical']
WITH e, count(r) as RiskCount, avg(r.score) as AvgRiskScore
WHERE RiskCount >= 2
RETURN e.name as Entity,
       e.type as EntityType,
       RiskCount,
       round(AvgRiskScore * 100) / 100 as AvgScore
ORDER BY AvgRiskScore DESC, RiskCount DESC;

-- 2.3 Entity Risk Timeline
-- Track how risks evolved for an entity over time
MATCH (e:Entity {name: 'China Evergrande Group'})<-[:TARGETS_ENTITY]-(r:Risk)
MATCH (r)-[:HAS_SNAPSHOT]->(rs:RiskSnapshot)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN rt.label as RiskType,
       rs.date as SnapshotDate,
       rs.score as Score
ORDER BY rs.date, rt.label;


-- =============================================================================
-- 3. EVENT EVOLUTION QUERIES
-- =============================================================================

-- 3.1 Event Evolution Chains
-- Find sequences of events that evolved into each other
MATCH path = (e1:Event)-[:EVOLVES_TO*1..3]->(e2:Event)
WHERE e1.eventId = 'evt_001'  -- Starting event
RETURN [e in nodes(path) | e.type] as EventChain,
       [e in nodes(path) | e.date] as DateChain,
       length(path) as ChainLength
ORDER BY ChainLength DESC
LIMIT 10;

-- 3.2 Strongest Evolution Links
-- Find the most significant event evolution relationships
MATCH (e1:Event)-[r:EVOLVES_TO {type: 'enhanced'}]->(e2:Event)
WHERE r.score > 0.5
RETURN e1.type as FromEvent,
       e1.date as FromDate,
       e2.type as ToEvent,
       e2.date as ToDate,
       round(r.score * 1000) / 1000 as OverallScore,
       round(r.causality * 1000) / 1000 as CausalityScore,
       round(r.emotional * 1000) / 1000 as EmotionalScore
ORDER BY r.score DESC
LIMIT 20;

-- 3.3 Causal Event Chains
-- Find event chains with strong causal relationships
MATCH path = (e1:Event)-[:EVOLVES_TO*2..5]->(e2:Event)
WHERE all(r in relationships(path) WHERE r.causality > 0.6)
WITH path,
     [e in nodes(path) | e.type] as chain,
     [r in relationships(path) | r.causality] as causal_scores
RETURN chain as EventChain,
       length(path) as ChainLength,
       round(reduce(sum = 0.0, score in causal_scores | sum + score) / size(causal_scores) * 1000) / 1000 as AvgCausality
ORDER BY ChainLength DESC, AvgCausality DESC
LIMIT 10;

-- 3.4 Event Impact Analysis
-- Find events that triggered the most subsequent events
MATCH (e:Event)-[r:EVOLVES_TO]->(next:Event)
WITH e, count(next) as DirectImpact, avg(r.score) as AvgLinkStrength
WHERE DirectImpact > 0
RETURN e.eventId as EventId,
       e.type as EventType,
       e.date as Date,
       DirectImpact,
       round(AvgLinkStrength * 1000) / 1000 as AvgEvolutionScore
ORDER BY DirectImpact DESC, AvgLinkStrength DESC;


-- =============================================================================
-- 4. RISK PROPAGATION QUERIES
-- =============================================================================

-- 4.1 Risk-Event-Risk Paths
-- Trace how risks connect through events
MATCH path = (r1:Risk)-[:TRIGGERED_BY]->(:Event)-[:TRIGGERS]->(r2:Risk)
MATCH (r1)-[:HAS_RISK_TYPE]->(rt1:RiskType)
MATCH (r2)-[:HAS_RISK_TYPE]->(rt2:RiskType)
RETURN rt1.label as FromRisk,
       rt2.label as ToRisk,
       count(path) as PathCount
ORDER BY PathCount DESC;

-- 4.2 Systemic Risk Detection
-- Identify entities at risk of contagion
MATCH (e:Entity)<-[:TARGETS_ENTITY]-(r:Risk)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType {name: 'ContagionRisk'})
MATCH (e)-[:RELATED_TO]-(connected:Entity)
RETURN e.name as SourceEntity,
       collect(DISTINCT connected.name) as ConnectedEntities,
       r.score as ContagionScore,
       r.severity as Severity
ORDER BY r.score DESC;

-- 4.3 Multi-Risk Entities
-- Find entities facing multiple types of risks simultaneously
MATCH (e:Entity)<-[:TARGETS_ENTITY]-(r:Risk)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
WITH e, collect(DISTINCT rt.label) as RiskTypes, avg(r.score) as AvgScore
WHERE size(RiskTypes) >= 3
RETURN e.name as Entity,
       RiskTypes,
       size(RiskTypes) as RiskTypeCount,
       round(AvgScore * 100) / 100 as AvgRiskScore
ORDER BY RiskTypeCount DESC, AvgScore DESC;


-- =============================================================================
-- 5. TEMPORAL ANALYSIS QUERIES
-- =============================================================================

-- 5.1 Event Timeline
-- Chronological view of all events
MATCH (e:Event)
OPTIONAL MATCH (e)-[:HAS_ACTOR]->(actor:Entity)
OPTIONAL MATCH (e)-[:HAS_TARGET]->(target:Entity)
RETURN e.date as Date,
       e.type as EventType,
       actor.name as Actor,
       target.name as Target,
       e.description as Description
ORDER BY e.date;

-- 5.2 Risk Evolution Over Time
-- Track how risk scores changed over time
MATCH (r:Risk)-[:HAS_SNAPSHOT]->(rs:RiskSnapshot)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
MATCH (r)-[:TARGETS_ENTITY]->(e:Entity)
RETURN rs.date as Date,
       e.name as Entity,
       rt.label as RiskType,
       rs.score as Score
ORDER BY rs.date, e.name, rt.label;

-- 5.3 Crisis Escalation Points
-- Identify dates with multiple significant events
MATCH (e:Event)
WITH e.date as Date, collect(e.type) as Events, count(e) as EventCount
WHERE EventCount >= 2
RETURN Date, Events, EventCount
ORDER BY Date;


-- =============================================================================
-- 6. NETWORK ANALYSIS QUERIES
-- =============================================================================

-- 6.1 Entity Relationship Network
-- Map how entities are connected
MATCH (e1:Entity)-[r:RELATED_TO]-(e2:Entity)
RETURN e1.name as Entity1,
       e2.name as Entity2,
       r.relationshipType as RelationType
ORDER BY e1.name, e2.name;

-- 6.2 Event Actor Network
-- Who are the key actors in events?
MATCH (e:Event)-[:HAS_ACTOR]->(actor:Entity)
WITH actor, count(e) as ActionCount, collect(DISTINCT e.type) as EventTypes
RETURN actor.name as Actor,
       actor.type as ActorType,
       ActionCount,
       EventTypes
ORDER BY ActionCount DESC;

-- 6.3 Event Target Network
-- Which entities are most frequently targets?
MATCH (e:Event)-[:HAS_TARGET]->(target:Entity)
WITH target, count(e) as TargetCount, collect(DISTINCT e.type) as EventTypes
RETURN target.name as Target,
       target.type as TargetType,
       TargetCount,
       EventTypes
ORDER BY TargetCount DESC;


-- =============================================================================
-- 7. ADVANCED PATTERN QUERIES
-- =============================================================================

-- 7.1 Debt Default Cascade Pattern
-- Detect debt default → credit downgrade → stock crash patterns
MATCH path = (e1:Event {type: 'debt_default'})-[:EVOLVES_TO*1..3]->(e2:Event)
WHERE any(e in nodes(path) WHERE e.type IN ['credit_downgrade', 'stock_crash'])
RETURN [e in nodes(path) | {type: e.type, date: e.date}] as CascadePattern,
       length(path) as Steps
ORDER BY length(path) DESC;

-- 7.2 Regulatory Intervention Impact
-- Analyze events following regulatory actions
MATCH (reg:Event {type: 'regulatory_intervention'})
MATCH path = (reg)-[:EVOLVES_TO*1..2]->(subsequent:Event)
RETURN reg.date as InterventionDate,
       collect(DISTINCT subsequent.type) as SubsequentEvents,
       count(DISTINCT subsequent) as EventCount
ORDER BY reg.date;

-- 7.3 Contagion Risk Paths
-- Identify potential contagion paths between entities
MATCH path = (e1:Entity)<-[:TARGETS_ENTITY]-(r:Risk)-[:HAS_RISK_TYPE]->
             (rt:RiskType {name: 'ContagionRisk'})
MATCH (e1)-[:RELATED_TO*1..2]-(e2:Entity)
WHERE e1 <> e2
RETURN e1.name as SourceEntity,
       e2.name as PotentialTarget,
       length(path) as Distance,
       r.score as ContagionScore
ORDER BY r.score DESC, length(path);


-- =============================================================================
-- 8. STATISTICAL QUERIES
-- =============================================================================

-- 8.1 Evolution Score Statistics
-- Overall statistics on evolution link quality
MATCH ()-[r:EVOLVES_TO {type: 'enhanced'}]->()
RETURN count(r) as TotalLinks,
       round(avg(r.score) * 1000) / 1000 as AvgOverallScore,
       round(avg(r.temporal) * 1000) / 1000 as AvgTemporal,
       round(avg(r.entity_overlap) * 1000) / 1000 as AvgEntityOverlap,
       round(avg(r.semantic) * 1000) / 1000 as AvgSemantic,
       round(avg(r.topic) * 1000) / 1000 as AvgTopic,
       round(avg(r.causality) * 1000) / 1000 as AvgCausality,
       round(avg(r.emotional) * 1000) / 1000 as AvgEmotional;

-- 8.2 Risk Score Distribution
-- Histogram of risk scores by severity
MATCH (r:Risk)
WITH r.severity as Severity,
     CASE
       WHEN r.score < 0.3 THEN 'Low (0-0.3)'
       WHEN r.score < 0.6 THEN 'Medium (0.3-0.6)'
       WHEN r.score < 0.8 THEN 'High (0.6-0.8)'
       ELSE 'Critical (0.8-1.0)'
     END as ScoreBand,
     count(*) as Count
RETURN Severity, ScoreBand, Count
ORDER BY Severity, ScoreBand;

-- 8.3 Event Type Frequency
-- Most common event types
MATCH (e:Event)
RETURN e.type as EventType,
       count(*) as Frequency
ORDER BY Frequency DESC;


-- =============================================================================
-- 9. PARAMETERIZED QUERIES (Use with Python/API)
-- =============================================================================

-- 9.1 Entity Risk Query (parameterized)
-- Usage: Pass $entityName parameter
MATCH (e:Entity {name: $entityName})
MATCH (r:Risk)-[:TARGETS_ENTITY]->(e)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
RETURN rt.label as RiskType,
       r.score as Score,
       r.severity as Severity,
       r.status as Status
ORDER BY r.score DESC;

-- 9.2 Date Range Event Query (parameterized)
-- Usage: Pass $startDate and $endDate parameters
MATCH (e:Event)
WHERE date(e.date) >= date($startDate)
  AND date(e.date) <= date($endDate)
RETURN e.eventId as EventId,
       e.type as EventType,
       e.date as Date,
       e.description as Description
ORDER BY e.date;

-- 9.3 Risk Score Threshold Query (parameterized)
-- Usage: Pass $minScore parameter
MATCH (r:Risk)-[:TARGETS_ENTITY]->(e:Entity)
MATCH (r)-[:HAS_RISK_TYPE]->(rt:RiskType)
WHERE r.score >= $minScore
RETURN e.name as Entity,
       rt.label as RiskType,
       r.score as Score,
       r.severity as Severity
ORDER BY r.score DESC;


-- =============================================================================
-- 10. VISUALIZATION QUERIES
-- =============================================================================

-- 10.1 Three-Layer Graph Sample
-- Sample nodes from all three layers for visualization
MATCH (e:Entity)
WITH collect(e)[..5] as entities
MATCH (ev:Event)
WITH entities, collect(ev)[..10] as events
MATCH (r:Risk)
WITH entities, events, collect(r)[..10] as risks
UNWIND entities + events + risks as node
RETURN node
LIMIT 25;

-- 10.2 Evolution Network Visualization
-- Get evolution network for graph visualization
MATCH path = (e1:Event)-[r:EVOLVES_TO {type: 'enhanced'}]->(e2:Event)
WHERE r.score > 0.4
RETURN e1, r, e2
LIMIT 50;

-- 10.3 Risk Propagation Network
-- Visualize how risks spread through entities
MATCH (e1:Entity)<-[:TARGETS_ENTITY]-(r:Risk)-[:TRIGGERED_BY]->
      (:Event)-[:TRIGGERS]->(r2:Risk)-[:TARGETS_ENTITY]->(e2:Entity)
RETURN e1, r, r2, e2
LIMIT 30;
