"""
Agent-Based Model for Financial Crisis Simulation

This module provides the ABM infrastructure for simulating financial crises
using historical knowledge graph data and SLM-powered agent decision-making.
"""

from .agents import BankAgent, RegulatorAgent, MarketAgent
from .model import FinancialCrisisModel
from .network import load_network_from_kg
from .metrics import CrisisMetricsCollector

__all__ = [
    'BankAgent',
    'RegulatorAgent',
    'MarketAgent',
    'FinancialCrisisModel',
    'load_network_from_kg',
    'CrisisMetricsCollector',
]

__version__ = '1.0.0'
