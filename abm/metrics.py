"""
Metrics Collection for ABM Simulation

Provides custom data collectors and analysis tools for tracking
simulation dynamics and exporting results.
"""

from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt


class CrisisMetricsCollector:
    """
    Extended metrics collector for financial crisis simulation

    Tracks:
    - Bank failures over time
    - Capital depletion rates
    - Network fragmentation
    - Systemic risk evolution
    - Regulatory interventions
    """

    def __init__(self, model):
        self.model = model
        self.data = {
            'failures_by_step': [],
            'capital_distribution': [],
            'network_metrics': [],
            'intervention_events': []
        }

    def collect(self, step: int):
        """
        Collect metrics for current step

        Args:
            step: Current simulation step
        """
        # Bank failures
        failed_this_step = [
            b for b in self.model.bank_agents
            if b.failed and b.failure_step == step
        ]

        self.data['failures_by_step'].append({
            'step': step,
            'n_failures': len(failed_this_step),
            'cumulative_failures': len(self.model.failed_banks),
            'failure_names': [b.name for b in failed_this_step]
        })

        # Capital distribution
        surviving_banks = [b for b in self.model.bank_agents if not b.failed]
        if surviving_banks:
            capitals = [b.capital for b in surviving_banks]
            self.data['capital_distribution'].append({
                'step': step,
                'mean': np.mean(capitals),
                'std': np.std(capitals),
                'min': np.min(capitals),
                'max': np.max(capitals),
                'total': np.sum(capitals)
            })

        # Network metrics
        self.data['network_metrics'].append({
            'step': step,
            'density': self.model.network.number_of_edges() / (self.model.n_banks * (self.model.n_banks - 1) / 2),
            'active_nodes': len(surviving_banks),
            'fragmentation': 1.0 - len(surviving_banks) / self.model.n_banks
        })

    def get_failure_timeline(self) -> pd.DataFrame:
        """
        Get bank failure timeline as DataFrame

        Returns:
            DataFrame with columns: step, bank_name, capital_at_failure
        """
        failures = []
        for bank in self.model.failed_banks:
            failures.append({
                'step': bank.failure_step,
                'bank_name': bank.name,
                'capital_at_failure': bank.capital,
                'liquidity_ratio': bank.liquidity_ratio,
                'leverage_ratio': bank.leverage_ratio
            })

        return pd.DataFrame(failures)

    def get_capital_evolution(self) -> pd.DataFrame:
        """
        Get capital evolution over time

        Returns:
            DataFrame with capital statistics by step
        """
        return pd.DataFrame(self.data['capital_distribution'])

    def get_network_evolution(self) -> pd.DataFrame:
        """
        Get network metrics evolution

        Returns:
            DataFrame with network stats by step
        """
        return pd.DataFrame(self.data['network_metrics'])

    def plot_crisis_timeline(self, save_path: str = None):
        """
        Create comprehensive crisis timeline visualization

        Args:
            save_path: Path to save figure (None = show only)
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Financial Crisis Timeline', fontsize=16, fontweight='bold')

        # 1. Cumulative failures
        failures_df = pd.DataFrame(self.data['failures_by_step'])
        axes[0, 0].plot(failures_df['step'], failures_df['cumulative_failures'], 'r-', linewidth=2)
        axes[0, 0].set_title('Cumulative Bank Failures')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Number of Failed Banks')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Capital evolution
        if self.data['capital_distribution']:
            capital_df = self.get_capital_evolution()
            axes[0, 1].plot(capital_df['step'], capital_df['mean'], 'b-', label='Mean', linewidth=2)
            axes[0, 1].fill_between(
                capital_df['step'],
                capital_df['mean'] - capital_df['std'],
                capital_df['mean'] + capital_df['std'],
                alpha=0.3,
                label='±1 Std'
            )
            axes[0, 1].set_title('Average Bank Capital')
            axes[0, 1].set_xlabel('Step')
            axes[0, 1].set_ylabel('Capital ($B)')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

        # 3. Market indicators
        model_data = self.model.datacollector.get_model_vars_dataframe()
        if 'Market_VIX' in model_data.columns:
            ax3a = axes[1, 0]
            ax3b = ax3a.twinx()

            ax3a.plot(model_data.index, model_data['Market_VIX'], 'g-', label='VIX', linewidth=2)
            ax3b.plot(model_data.index, model_data['Market_TED_Spread'], 'orange', label='TED Spread', linewidth=2)

            ax3a.set_title('Market Stress Indicators')
            ax3a.set_xlabel('Step')
            ax3a.set_ylabel('VIX', color='g')
            ax3b.set_ylabel('TED Spread (%)', color='orange')
            ax3a.grid(True, alpha=0.3)

        # 4. Network fragmentation
        network_df = self.get_network_evolution()
        axes[1, 1].plot(network_df['step'], network_df['fragmentation'], 'purple', linewidth=2)
        axes[1, 1].set_title('Network Fragmentation')
        axes[1, 1].set_xlabel('Step')
        axes[1, 1].set_ylabel('Fragmentation (0-1)')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Crisis timeline saved to: {save_path}")
        else:
            plt.show()

    def generate_report(self) -> Dict:
        """
        Generate comprehensive simulation report

        Returns:
            dict: Summary statistics and key metrics
        """
        failures_df = pd.DataFrame(self.data['failures_by_step'])
        final_failures = failures_df['cumulative_failures'].iloc[-1] if len(failures_df) > 0 else 0

        report = {
            'simulation_summary': {
                'total_steps': self.model.total_steps,
                'total_banks': self.model.n_banks,
                'total_failures': final_failures,
                'failure_rate': final_failures / self.model.n_banks if self.model.n_banks > 0 else 0
            },
            'failure_timeline': self.get_failure_timeline().to_dict(orient='records'),
            'peak_crisis_step': int(failures_df['n_failures'].idxmax()) if len(failures_df) > 0 else None,
            'regulatory_interventions': {
                'bailouts_provided': self.model.regulator_agent.bailouts_provided,
                'final_interest_rate': self.model.regulator_agent.interest_rate,
                'funds_remaining': self.model.regulator_agent.available_funds
            },
            'market_indicators': {
                'final_vix': self.model.market_agent.vix,
                'final_ted_spread': self.model.market_agent.ted_spread,
                'final_sentiment': self.model.market_agent.sentiment
            },
            'network_stats': self.model.get_network_stats()
        }

        return report


def analyze_contagion_paths(model) -> List[Dict]:
    """
    Analyze contagion propagation paths

    Traces how failures propagated through the network

    Args:
        model: FinancialCrisisModel instance

    Returns:
        List of contagion path dicts
    """
    contagion_paths = []

    # Sort failures by step
    sorted_failures = sorted(
        [b for b in model.failed_banks],
        key=lambda b: b.failure_step
    )

    for i, failed_bank in enumerate(sorted_failures):
        # Find which banks this failure affected
        affected_banks = []
        for cp_id in failed_bank.counterparties:
            # Find counterparty in bank_agents list
            cp_agent = None
            for bank in model.bank_agents:
                if bank.unique_id == cp_id:
                    cp_agent = bank
                    break

            if cp_agent and isinstance(cp_agent, model.bank_agents[0].__class__):
                if cp_agent.failed and cp_agent.failure_step > failed_bank.failure_step:
                    affected_banks.append({
                        'name': cp_agent.name,
                        'failure_step': cp_agent.failure_step,
                        'delay': cp_agent.failure_step - failed_bank.failure_step
                    })

        contagion_paths.append({
            'source': failed_bank.name,
            'failure_step': failed_bank.failure_step,
            'affected_count': len(affected_banks),
            'affected_banks': affected_banks
        })

    return contagion_paths


def calculate_systemic_importance(model) -> Dict[str, float]:
    """
    Calculate systemic importance scores for banks

    Uses network centrality metrics

    Args:
        model: FinancialCrisisModel instance

    Returns:
        Dict mapping bank name -> importance score (0-1)
    """
    import networkx as nx

    # Calculate degree centrality
    degree_centrality = nx.degree_centrality(model.network)

    # Map to bank names
    importance = {}
    for node_id, centrality in degree_centrality.items():
        if node_id < len(model.bank_agents):
            bank = model.bank_agents[node_id]
            # Combine centrality with capital size
            capital_weight = bank.capital / max(b.capital for b in model.bank_agents)
            importance[bank.name] = (centrality + capital_weight) / 2.0

    return importance
