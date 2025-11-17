"""
Financial Crisis Agent-Based Model

Main simulation model that orchestrates banks, regulators, and market dynamics.
"""

from mesa import Model
from mesa.datacollection import DataCollector
import networkx as nx
import numpy as np
from typing import List, Dict, Optional
import json
import random

from .agents import BankAgent, RegulatorAgent, MarketAgent


class FinancialCrisisModel(Model):
    """
    Agent-Based Model for Financial Crisis Simulation

    Simulates systemic risk propagation through a network of financial institutions
    using historical knowledge graph data and agent decision-making.

    Parameters:
        n_banks (int): Number of bank agents
        network (nx.Graph): Interbank network topology
        initial_capital_range (tuple): Range for initial capital (min, max) in $B
        crisis_trigger_step (int): Step to trigger exogenous shock
        random_seed (int): Random seed for reproducibility

    Attributes:
        crisis_intensity (float): Overall crisis level (0-1)
        failed_banks (list): List of failed bank agents
        total_steps (int): Total simulation steps run
    """

    def __init__(
        self,
        n_banks: int = 10,
        network: Optional[nx.Graph] = None,
        initial_capital_range: tuple = (5.0, 20.0),
        crisis_trigger_step: Optional[int] = None,
        random_seed: Optional[int] = 42
    ):
        # Set random seed (Mesa 3.x uses seed parameter)
        super().__init__(seed=random_seed)

        # Model parameters
        self.n_banks = n_banks
        self.crisis_trigger_step = crisis_trigger_step
        self.crisis_intensity = 0.0

        # Network
        if network is None:
            # Default: Erdős-Rényi random network
            self.network = nx.erdos_renyi_graph(n_banks, p=0.3, seed=random_seed)
        else:
            self.network = network

        # Agent tracking
        self.failed_banks = []
        self.bank_agents = []

        # Create agents
        self._create_agents(initial_capital_range)

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Failed_Banks": lambda m: len(m.failed_banks),
                "Crisis_Intensity": lambda m: m.crisis_intensity,
                "Avg_Capital": lambda m: np.mean([a.capital for a in m.bank_agents if not a.failed]) if any(not a.failed for a in m.bank_agents) else 0,
                "Avg_Liquidity_Ratio": lambda m: np.mean([a.liquidity_ratio for a in m.bank_agents if not a.failed]) if any(not a.failed for a in m.bank_agents) else 0,
                "Market_VIX": lambda m: m.market_agent.vix,
                "Market_TED_Spread": lambda m: m.market_agent.ted_spread,
                "Regulator_Interest_Rate": lambda m: m.regulator_agent.interest_rate,
                "Bailouts_Provided": lambda m: m.regulator_agent.bailouts_provided
            },
            agent_reporters={
                "Capital": lambda a: a.capital if isinstance(a, BankAgent) else None,
                "Liquidity": lambda a: a.liquidity if isinstance(a, BankAgent) else None,
                "Risk_Score": lambda a: a.risk_score if isinstance(a, BankAgent) else None,
                "Failed": lambda a: a.failed if isinstance(a, BankAgent) else None
            }
        )

        self.running = True
        self.total_steps = 0

    def _create_agents(self, capital_range: tuple):
        """
        Create bank, regulator, and market agents

        Args:
            capital_range: Tuple of (min_capital, max_capital) in $B
        """
        # Default bank names (will be replaced with KG entities later)
        bank_names = [
            "Lehman Brothers", "AIG", "Bear Stearns", "Merrill Lynch",
            "Morgan Stanley", "Goldman Sachs", "Citigroup", "Bank of America",
            "JPMorgan", "Wells Fargo", "Wachovia", "Washington Mutual",
            "Deutsche Bank", "Barclays", "UBS", "Credit Suisse",
            "HSBC", "Royal Bank of Scotland", "Fortis", "Dexia"
        ]

        # Create bank agents
        for i in range(self.n_banks):
            # Random capital within range
            capital = self.random.uniform(*capital_range)
            liquidity = capital * self.random.uniform(0.3, 0.6)  # 30-60% of capital
            assets = capital * self.random.uniform(8, 12)  # 8-12x leverage
            liabilities = assets - capital

            # Create bank (Mesa 3.x: model comes first)
            bank = BankAgent(
                model=self,
                unique_id=i,
                name=bank_names[i] if i < len(bank_names) else f"Bank_{i}",
                entity_id=f"ent_bank_{i}",
                capital=capital,
                liquidity=liquidity,
                assets=assets,
                liabilities=liabilities
            )

            self.bank_agents.append(bank)

        # Create network connections (counterparty relationships)
        for edge in self.network.edges():
            bank_a = self.bank_agents[edge[0]]
            bank_b = self.bank_agents[edge[1]]
            bank_a.counterparties.add(bank_b.unique_id)
            bank_b.counterparties.add(bank_a.unique_id)

        # Create regulator agent (Mesa 3.x: model comes first)
        self.regulator_agent = RegulatorAgent(
            model=self,
            unique_id=self.n_banks,
            available_funds=500.0,  # $500B bailout fund
            intervention_threshold=0.6
        )

        # Create market agent (Mesa 3.x: model comes first)
        self.market_agent = MarketAgent(
            model=self,
            unique_id=self.n_banks + 1,
            initial_vix=20.0,
            initial_ted_spread=0.5
        )

    def step(self):
        """
        Execute one simulation step

        Process:
        1. Trigger crisis shock (if specified)
        2. All agents take actions (banks, regulator, market)
        3. Update crisis intensity
        4. Collect data
        """
        # Trigger crisis shock
        if self.crisis_trigger_step is not None and self.total_steps == self.crisis_trigger_step:
            self.trigger_crisis_shock()

        # All agents act (Mesa 3.x: use agents.do())
        # Shuffle and activate all agents
        all_agents = self.bank_agents + [self.regulator_agent, self.market_agent]
        random.shuffle(all_agents)
        for agent in all_agents:
            if hasattr(agent, 'step'):
                agent.step()

        # Update crisis intensity
        self.update_crisis_intensity()

        # Collect data
        self.datacollector.collect(self)

        self.total_steps += 1
        self.steps += 1  # Mesa 3.x tracks steps

    def trigger_crisis_shock(self):
        """
        Trigger an exogenous crisis shock

        Simulates a major event (e.g., Lehman bankruptcy) by:
        1. Forcing one bank to fail
        2. Creating market panic
        3. Liquidity freeze
        """
        print(f"\n🔥 CRISIS SHOCK TRIGGERED AT STEP {self.total_steps} 🔥\n")

        # Find highest-leverage bank (most vulnerable)
        surviving_banks = [b for b in self.bank_agents if not b.failed]
        if not surviving_banks:
            return

        target_bank = max(surviving_banks, key=lambda b: b.leverage_ratio)

        # Force failure
        target_bank.capital = 0.5  # Below failure threshold
        target_bank.fail()

        # Market panic
        self.market_agent.vix = 60.0  # Spike volatility
        self.market_agent.ted_spread = 3.0  # Credit freeze
        self.market_agent.sentiment = -0.8  # Panic

        # Increase crisis intensity
        self.crisis_intensity = 0.8

    def update_crisis_intensity(self):
        """
        Update overall crisis intensity based on system state

        Crisis intensity (0-1) combines:
        - Percentage of failed banks
        - Market stress (VIX, TED spread)
        - Average bank risk scores
        """
        # Failed bank ratio
        failed_ratio = len(self.failed_banks) / self.n_banks if self.n_banks > 0 else 0.0

        # Market stress
        market_stress = self.market_agent.get_stress_level()

        # Average bank risk
        surviving_banks = [b for b in self.bank_agents if not b.failed]
        avg_risk = np.mean([b.risk_score for b in surviving_banks]) if surviving_banks else 0.0

        # Weighted average
        self.crisis_intensity = (failed_ratio * 0.5 + market_stress * 0.3 + avg_risk * 0.2)

        # Track failed banks
        self.failed_banks = [b for b in self.bank_agents if b.failed]

    def get_network_stats(self) -> Dict:
        """
        Get network statistics

        Returns:
            dict: Network metrics (density, clustering, centrality)
        """
        return {
            'nodes': self.network.number_of_nodes(),
            'edges': self.network.number_of_edges(),
            'density': nx.density(self.network),
            'avg_clustering': nx.average_clustering(self.network),
            'connected_components': nx.number_connected_components(self.network)
        }

    def get_summary(self) -> Dict:
        """
        Get simulation summary

        Returns:
            dict: Current state summary
        """
        surviving_banks = [b for b in self.bank_agents if not b.failed]

        return {
            'step': self.total_steps,
            'n_banks': self.n_banks,
            'failed_banks': len(self.failed_banks),
            'surviving_banks': len(surviving_banks),
            'crisis_intensity': self.crisis_intensity,
            'market_vix': self.market_agent.vix,
            'market_ted_spread': self.market_agent.ted_spread,
            'regulator_interest_rate': self.regulator_agent.interest_rate,
            'bailouts_provided': self.regulator_agent.bailouts_provided,
            'avg_capital': np.mean([b.capital for b in surviving_banks]) if surviving_banks else 0.0,
            'avg_liquidity_ratio': np.mean([b.liquidity_ratio for b in surviving_banks]) if surviving_banks else 0.0
        }

    def export_results(self, output_path: str):
        """
        Export simulation results to JSON

        Args:
            output_path: Path to save results
        """
        # Get model-level data
        model_data = self.datacollector.get_model_vars_dataframe()

        # Get agent-level data
        agent_data = self.datacollector.get_agent_vars_dataframe()

        # Combine into dict
        results = {
            'metadata': {
                'n_banks': self.n_banks,
                'total_steps': self.total_steps,
                'crisis_trigger_step': self.crisis_trigger_step,
                'final_failed_banks': len(self.failed_banks)
            },
            'model_data': model_data.to_dict(orient='index'),
            'bank_failures': [
                {
                    'name': b.name,
                    'failure_step': b.failure_step,
                    'capital_at_failure': b.capital,
                    'liquidity_ratio_at_failure': b.liquidity_ratio
                }
                for b in self.failed_banks
            ],
            'network_stats': self.get_network_stats(),
            'final_summary': self.get_summary()
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"✅ Results exported to: {output_path}")
