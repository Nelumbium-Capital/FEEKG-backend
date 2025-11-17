# Agent-Based Model Component

**Component 2 of Financial Crisis AI System**

---

## Overview

This component implements an Agent-Based Model (ABM) for simulating financial crisis contagion using the Mesa framework. Agents (banks, regulators, markets) interact in a network, making decisions that lead to emergent systemic behavior.

---

## What It Does

### Simulates Financial Contagion
- **BankAgents** make strategic decisions (defensive, maintain, aggressive, seek liquidity)
- **RegulatorAgent** provides bailouts and adjusts interest rates
- **MarketAgent** tracks panic (VIX, TED spread, sentiment)
- **Network effects** propagate shocks through counterparty relationships

### Current Status: **Foundation Complete** ✅
- Rule-based decision logic (if/else)
- Network topology loaded from Knowledge Graph
- Metrics collection and export
- Test simulation working (10 banks, 100 steps)

### Next: **Week 3 - SLM Integration** ⏳
- Replace rules with AI reasoning
- Query KG for historical context
- Generate natural language explanations

---

## Files

```
abm/
├── __init__.py                # Package exports
├── agents.py                  # 3 agent classes (475 lines)
│   ├── BankAgent
│   ├── RegulatorAgent
│   └── MarketAgent
├── model.py                   # FinancialCrisisModel (315 lines)
├── network.py                 # KG topology loader (331 lines)
├── metrics.py                 # Data collection (285 lines)
├── test_simulation.py         # Test script (192 lines)
└── README.md                  # This file
```

---

## Quick Start

### Run Test Simulation

```bash
# From project root
./venv/bin/python abm/test_simulation.py
```

**Output:**
- Console: Step-by-step progress (failures, bailouts, market indicators)
- `results/abm_simulation_results.json` - Full data export
- `results/abm_network.json` - Network topology
- `results/abm_crisis_timeline.png` - 4-panel visualization

### Use in Code

```python
from abm import FinancialCrisisModel, load_network_from_kg

# Load network from Knowledge Graph
network, metadata = load_network_from_kg(entity_limit=20)

# Create model
model = FinancialCrisisModel(
    n_banks=20,
    network=network,
    initial_capital_range=(5.0, 20.0),
    crisis_trigger_step=50,  # Trigger shock at step 50
    random_seed=42
)

# Run simulation
for step in range(200):
    model.step()

    if (step + 1) % 20 == 0:
        summary = model.get_summary()
        print(f"Step {step + 1}: {summary['failed_banks']} banks failed")

# Export results
model.export_results('my_simulation.json')
```

---

## Agent Classes

### BankAgent

**Financial State:**
- `capital`: Tier 1 capital ($B)
- `liquidity`: Liquid assets ($B)
- `assets`: Total assets ($B)
- `liabilities`: Total liabilities ($B)
- `leverage_ratio`: liabilities / capital
- `liquidity_ratio`: liquidity / liabilities
- `risk_score`: Systemic risk (0-1)

**Decision Logic (Current - Rule-Based):**
```python
def decide_action(self, context):
    if context['liquidity_ratio'] < 0.15:
        return 'SEEK_LIQUIDITY'  # Critical - request Fed help
    elif context['risk_score'] > 0.7:
        return 'DEFENSIVE'       # High risk - reduce exposure
    elif context['risk_score'] > 0.4:
        return 'MAINTAIN'        # Moderate risk - status quo
    else:
        return 'AGGRESSIVE'      # Low risk - expand lending
```

**Decision Logic (Week 3 - SLM-Based):**
```python
def decide_action(self, context):
    # Query KG for historical analogies
    historical = self.rag_retriever.retrieve(
        f"Situations like: leverage={self.leverage_ratio:.1f}x, "
        f"VIX={context['market_vix']}, failed_banks={context['n_failed_banks']}"
    )

    # SLM reasoning
    decision = self.model.slm.generate(
        prompt=self.format_decision_prompt(context, historical),
        max_tokens=50
    )

    return decision  # AI-driven, knowledge-grounded
```

**Actions:**
- `DEFENSIVE`: Reduce exposure (-10% assets/liabilities), increase liquidity (+10%)
- `MAINTAIN`: Status quo (no changes)
- `AGGRESSIVE`: Expand lending (+5% assets/liabilities)
- `SEEK_LIQUIDITY`: Request emergency liquidity from Fed

**Failure Conditions:**
- Capital < $1B
- Liquidity ratio < 10%
- Leverage ratio > 40x

**Contagion Mechanics:**
- When bank fails, shocks propagate to counterparties
- Exposure loss: 30% of assets × shock strength
- Liquidity drain: 50% of capital loss
- Mark-to-market losses during crisis: 5% × crisis intensity

---

### RegulatorAgent

**Attributes:**
- `available_funds`: Bailout capacity ($B, default: $500B)
- `interest_rate`: Policy rate (%, range: 0-5%)
- `bailouts_provided`: Count of interventions
- `intervention_threshold`: Crisis trigger level (0-1)

**Actions:**
- **Provide Liquidity:** Give emergency loans to distressed banks
- **Adjust Interest Rates:** Cut rates during crisis (emergency: -0.5%), raise during calm (+0.25%)
- **Monitor Systemic Risk:** Calculate overall crisis intensity

**Logic:**
```python
def step(self):
    systemic_risk = self.calculate_systemic_risk()

    if systemic_risk > 0.8:
        self.interest_rate = max(0.0, self.interest_rate - 0.5)  # Emergency cut
    elif systemic_risk < 0.3:
        self.interest_rate = min(5.0, self.interest_rate + 0.25)  # Gradual tightening

def provide_liquidity(self, bank):
    liquidity_need = max(bank.liabilities * 0.15 - bank.liquidity, 0)

    if liquidity_need > self.available_funds:
        return False  # Insufficient funds

    bank.liquidity += liquidity_need
    self.available_funds -= liquidity_need
    self.bailouts_provided += 1

    print(f"🏦 Fed provided ${liquidity_need:.1f}B to {bank.name}")
    return True
```

---

### MarketAgent

**Attributes:**
- `vix`: Volatility index (10-80 range, calm=20, panic=60+)
- `ted_spread`: Credit stress (0.5-4.0%, normal=0.5%, crisis=3.0%)
- `sentiment`: Market confidence (-1 to +1, panic=-0.8, euphoria=+1)

**Dynamics:**
```python
def step(self):
    # Count failed banks
    failed_ratio = len(self.model.failed_banks) / self.model.n_banks

    # Update VIX (volatility increases with failures)
    target_vix = 20.0 + (failed_ratio * 60.0)  # 20-80 range
    self.vix = self.vix * 0.7 + target_vix * 0.3  # Smooth transition

    # Update TED spread (credit stress)
    target_ted = 0.5 + (failed_ratio * 3.5)  # 0.5-4.0% range
    self.ted_spread = self.ted_spread * 0.7 + target_ted * 0.3

    # Update sentiment
    self.sentiment = 1.0 - (failed_ratio * 2.0)  # More failures = panic
```

**Market Stress Level:**
```python
def get_stress_level(self):
    vix_stress = min(self.vix / 80.0, 1.0)
    ted_stress = min(self.ted_spread / 4.0, 1.0)
    return (vix_stress + ted_stress) / 2.0  # 0-1 range
```

---

## FinancialCrisisModel

**Orchestrates all agents and tracks system state.**

### Parameters
```python
model = FinancialCrisisModel(
    n_banks=10,                         # Number of bank agents
    network=None,                        # Network (default: Erdős-Rényi)
    initial_capital_range=(5.0, 20.0),  # Capital range ($B)
    crisis_trigger_step=None,            # Step to trigger shock (None = no shock)
    random_seed=42                       # Random seed for reproducibility
)
```

### Methods

**`step()`** - Execute one simulation step
```python
def step(self):
    # 1. Trigger crisis shock (if specified)
    if self.crisis_trigger_step == self.total_steps:
        self.trigger_crisis_shock()

    # 2. All agents act (random order)
    all_agents = self.bank_agents + [self.regulator_agent, self.market_agent]
    random.shuffle(all_agents)
    for agent in all_agents:
        agent.step()

    # 3. Update crisis intensity
    self.update_crisis_intensity()

    # 4. Collect data
    self.datacollector.collect(self)

    self.total_steps += 1
```

**`trigger_crisis_shock()`** - Simulate exogenous shock
```python
def trigger_crisis_shock(self):
    # Force highest-leverage bank to fail
    target_bank = max(self.bank_agents, key=lambda b: b.leverage_ratio)
    target_bank.capital = 0.5  # Below failure threshold
    target_bank.fail()

    # Market panic
    self.market_agent.vix = 60.0
    self.market_agent.ted_spread = 3.0
    self.market_agent.sentiment = -0.8

    self.crisis_intensity = 0.8
```

**`get_summary()`** - Get current state snapshot
```python
summary = model.get_summary()
# Returns:
{
    'step': 42,
    'n_banks': 10,
    'failed_banks': 3,
    'surviving_banks': 7,
    'crisis_intensity': 0.45,
    'market_vix': 35.2,
    'market_ted_spread': 1.8,
    'regulator_interest_rate': 1.5,
    'bailouts_provided': 2,
    'avg_capital': 12.3,
    'avg_liquidity_ratio': 0.18
}
```

**`export_results()`** - Save simulation data
```python
model.export_results('results/my_simulation.json')
```

---

## Network Topology

### Loading from Knowledge Graph

The ABM loads network topology from KG evolution links:

```python
from abm.network import load_network_from_kg

network, entity_metadata = load_network_from_kg(
    entity_limit=20,           # Max entities
    min_evolution_score=0.5    # Min link strength
)

# network: NetworkX graph
# entity_metadata: {node_id: {'name': '...', 'entity_id': '...', 'type': '...'}}
```

**Process:**
1. Query AllegroGraph for entities and evolution links
2. Build NetworkX graph (entities = nodes, evolution links = edges)
3. Extract metadata (names, IDs, types)
4. Ensure graph is connected (add edges if needed)

### Fallback: Default Network

If KG unavailable, creates Erdős-Rényi random network:
```python
network, metadata = create_default_network(n=10)
# G(10, p=0.3) - 10 nodes, 30% edge probability
```

---

## Metrics & Data Collection

### Model-Level Metrics
- `Failed_Banks`: Count of failed banks
- `Crisis_Intensity`: Overall crisis level (0-1)
- `Avg_Capital`: Average capital of surviving banks
- `Avg_Liquidity_Ratio`: Average liquidity ratio
- `Market_VIX`: Volatility index
- `Market_TED_Spread`: Credit stress
- `Regulator_Interest_Rate`: Policy rate
- `Bailouts_Provided`: Count of interventions

### Agent-Level Metrics
- `Capital`: Bank's capital at each step
- `Liquidity`: Bank's liquidity at each step
- `Risk_Score`: Bank's risk score (0-1)
- `Failed`: Bank failure status (True/False)

### Export Format

```json
{
  "metadata": {
    "n_banks": 10,
    "total_steps": 100,
    "crisis_trigger_step": 30,
    "final_failed_banks": 10
  },
  "model_data": {
    "0": {"Failed_Banks": 0, "Crisis_Intensity": 0.05, "Avg_Capital": 12.5, ...},
    "1": {"Failed_Banks": 2, "Crisis_Intensity": 0.23, "Avg_Capital": 11.2, ...},
    ...
  },
  "bank_failures": [
    {"name": "Lehman Brothers", "failure_step": 0, "capital_at_failure": 2.64, ...},
    ...
  ],
  "network_stats": {
    "nodes": 10,
    "edges": 17,
    "density": 0.378,
    "avg_clustering": 0.412
  }
}
```

---

## Advanced Usage

### Custom Network Topology

```python
import networkx as nx

# Create custom network (scale-free, for example)
G = nx.barabasi_albert_graph(n=20, m=3)

model = FinancialCrisisModel(
    n_banks=20,
    network=G,
    ...
)
```

### Access Individual Agents

```python
# Get specific bank
lehman = model.bank_agents[0]
print(f"{lehman.name}: ${lehman.capital:.1f}B capital")

# Manually trigger failure
lehman.capital = 0.5
lehman.fail()  # Propagates shocks to counterparties

# Check regulator state
print(f"Fed funds: ${model.regulator_agent.available_funds:.1f}B")
print(f"Interest rate: {model.regulator_agent.interest_rate:.2f}%")
```

### Run Multiple Scenarios

```python
results = []

for shock_step in [20, 30, 40, 50]:
    model = FinancialCrisisModel(
        n_banks=10,
        crisis_trigger_step=shock_step,
        random_seed=42
    )

    for _ in range(100):
        model.step()

    results.append({
        'shock_step': shock_step,
        'final_failures': len(model.failed_banks),
        'final_crisis_intensity': model.crisis_intensity
    })

# Analyze: Does early shock lead to more failures?
```

---

## Integration with Other Components

### With Knowledge Graph (Component 1)
```python
# Load network from KG evolution links
from abm.network import load_network_from_kg

network, metadata = load_network_from_kg(entity_limit=20)
model = FinancialCrisisModel(network=network)
```

### With SLM (Component 3) - Week 3
```python
# Future: Agents query KG and use SLM for decisions
class KGAwareBankAgent(BankAgent):
    def decide_action(self, context):
        # Query KG via RAG
        historical = self.rag_retriever.retrieve(query)

        # SLM reasoning
        decision = self.slm.generate(prompt)

        return decision
```

### With RAG (Component 4) - Week 4
```python
# Future: Cache queries for performance
from rag.cache import KGCacheManager

cache = KGCacheManager(rag_retriever)
result = cache.query_with_cache(query, agent_id=bank.unique_id)
```

---

## Testing

### Run Test Simulation
```bash
./venv/bin/python abm/test_simulation.py
```

### Unit Tests (To be added - Week 4)
```bash
pytest tests/test_abm/test_agents.py
pytest tests/test_abm/test_model.py
pytest tests/test_abm/test_network.py
```

---

## Performance

### Benchmarks (10 banks, 100 steps)
- Simulation time: ~1-2 seconds
- Memory usage: ~50MB
- Data export: ~3KB JSON

### Scaling (estimates)
- 20 banks, 200 steps: ~10 seconds
- 100 banks, 100 steps: ~5 minutes (10,000 agent steps)
- 100 banks, 200 steps with SLM: ~30 minutes (20,000 SLM calls @ 200ms each)

### Optimization Strategies
- **Caching:** 3-tier query cache (80% hit rate → 7 min vs 33 min)
- **Batching:** SLM batch inference (process multiple agents simultaneously)
- **Parallelization:** Run multiple simulations in parallel (for experiments)

---

## Known Issues & Limitations

### Current Issues
1. **Extreme contagion:** All banks fail immediately in test simulation
   - **Cause:** High leverage ratios + dense network
   - **Fix:** Adjust shock strength parameters (Week 3)

2. **Rule-based decisions:** Too simplistic
   - **Cause:** If/else logic doesn't capture nuance
   - **Fix:** Replace with SLM reasoning (Week 3)

3. **No historical learning:** Agents don't query KG
   - **Cause:** RAG not implemented yet
   - **Fix:** Add RAG retrieval (Week 4)

### Limitations
- **No learning:** Agents don't adapt strategies over time
- **Homogeneous agents:** All banks use same decision logic
- **Fixed network:** Topology doesn't change during simulation
- **No market microstructure:** No explicit order books, trading

---

## Future Enhancements

### Week 3-4
- [ ] SLM-based decision-making
- [ ] RAG retrieval for historical context
- [ ] Query caching for performance
- [ ] Parameter tuning (shock strength, thresholds)

### Later
- [ ] Heterogeneous agents (different bank types: commercial, investment, insurance)
- [ ] Learning agents (Q-learning, policy gradient)
- [ ] Dynamic network (entities can merge, split)
- [ ] Market microstructure (order books, price formation)
- [ ] Multi-country simulation (international contagion)

---

## References

### Papers
- Haldane & May (2011) - "Systemic risk in banking ecosystems" (Nature)
- Cont & Schaanning (2017) - "Fire sales, indirect contagion and systemic stress testing"
- Liu et al. (2024) - "Risk identification through knowledge association" (FE-EKG paper)

### Mesa Documentation
- Official docs: https://mesa.readthedocs.io/
- Examples: https://github.com/projectmesa/mesa-examples
- API reference: https://mesa.readthedocs.io/en/stable/apis/api_main.html

### Related Projects
- Bank Network ABM: https://github.com/Ashwini-Lande/BankNetwork
- Financial Contagion: https://github.com/kentwait/financial_contagion

---

## Contact

For questions about this component:
- See main `README.md` for project contact
- Refer to `ARCHITECTURE.md` for system design
- Check `PROJECT_STATUS.md` for current progress

---

**Status:** Foundation Complete ✅ → Week 3: SLM Integration ⏳
**Last Updated:** 2025-11-16
