"""
Financial Crisis Agent Classes

Implements three types of agents:
1. BankAgent - Commercial/investment banks with decision-making
2. RegulatorAgent - Federal Reserve / Treasury interventions
3. MarketAgent - Aggregate market sentiment and conditions
"""

from mesa import Agent
from typing import Dict, List, Set, Optional
import numpy as np


class BankAgent(Agent):
    """
    Bank agent representing a financial institution

    Attributes:
        name (str): Bank name (e.g., "Lehman Brothers", "AIG")
        capital (float): Tier 1 capital in billions
        liquidity (float): Liquid assets in billions
        assets (float): Total assets in billions
        liabilities (float): Total liabilities in billions
        risk_score (float): Systemic risk metric (0-1)
        failed (bool): Failure state
        entity_id (str): KG entity ID (e.g., "ent_lehman_brothers")

    Decision-making:
        - DEFENSIVE: Reduce exposure, increase reserves
        - MAINTAIN: Continue current strategy
        - AGGRESSIVE: Expand lending, take risks
        - SEEK_LIQUIDITY: Request Fed assistance
    """

    def __init__(
        self,
        model,
        unique_id: int,
        name: str,
        entity_id: str,
        capital: float = 10.0,
        liquidity: float = 5.0,
        assets: float = 100.0,
        liabilities: float = 90.0
    ):
        super().__init__(model)

        # Set unique_id manually (Mesa 3.x auto-assigns, but we override)
        self.unique_id = unique_id

        # Identity
        self.name = name
        self.entity_id = entity_id

        # Financial state
        self.capital = capital  # Tier 1 capital ($B)
        self.liquidity = liquidity  # Liquid assets ($B)
        self.assets = assets  # Total assets ($B)
        self.liabilities = liabilities  # Total liabilities ($B)

        # Risk metrics
        self.risk_score = 0.0  # Systemic risk (0-1)
        self.leverage_ratio = liabilities / capital if capital > 0 else float('inf')
        self.liquidity_ratio = liquidity / liabilities if liabilities > 0 else 1.0

        # State
        self.failed = False
        self.bailout_received = False
        self.defensive_mode = False

        # History
        self.decision_history = []
        self.failure_step = None

        # Network
        self.counterparties: Set[int] = set()  # Agent IDs
        self.total_exposure = 0.0  # Total interbank exposure

    def step(self):
        """
        Execute one time step of agent behavior

        Process:
        1. Update metrics (leverage, liquidity ratio)
        2. Query KG for historical context (if SLM available)
        3. Make decision (defensive/maintain/aggressive)
        4. Execute action
        5. Check failure condition
        6. Propagate shocks if failed
        """
        if self.failed:
            return  # Dead agents don't act

        # 1. Update metrics
        self.update_metrics()

        # 2. Assess current situation
        context = self.get_situation_context()

        # 3. Make decision
        action = self.decide_action(context)

        # 4. Execute action
        self.execute_action(action)

        # 5. Check failure
        if self.check_failure_condition():
            self.fail()

        # 6. Record decision
        self.decision_history.append({
            'step': self.model.total_steps,
            'action': action,
            'capital': self.capital,
            'liquidity': self.liquidity,
            'risk_score': self.risk_score
        })

    def update_metrics(self):
        """Update leverage and liquidity ratios"""
        if self.capital > 0:
            self.leverage_ratio = self.liabilities / self.capital
        else:
            self.leverage_ratio = float('inf')

        if self.liabilities > 0:
            self.liquidity_ratio = self.liquidity / self.liabilities
        else:
            self.liquidity_ratio = 1.0

        # Calculate risk score (higher leverage + lower liquidity = higher risk)
        leverage_risk = min(self.leverage_ratio / 30.0, 1.0)  # 30x leverage = max risk
        liquidity_risk = max(1.0 - self.liquidity_ratio, 0.0)
        self.risk_score = (leverage_risk + liquidity_risk) / 2.0

    def get_situation_context(self) -> Dict:
        """
        Get current situation context for decision-making

        Returns dict with current state, market conditions, network position
        """
        return {
            'capital': self.capital,
            'liquidity': self.liquidity,
            'leverage_ratio': self.leverage_ratio,
            'liquidity_ratio': self.liquidity_ratio,
            'risk_score': self.risk_score,
            'market_vix': self.model.market_agent.vix if hasattr(self.model, 'market_agent') else 20.0,
            'market_ted_spread': self.model.market_agent.ted_spread if hasattr(self.model, 'market_agent') else 0.5,
            'n_failed_banks': len(self.model.failed_banks),
            'crisis_intensity': self.model.crisis_intensity,
            'counterparty_risk': self.assess_counterparty_risk()
        }

    def decide_action(self, context: Dict) -> str:
        """
        Decide what action to take based on context

        For now uses rule-based logic. Will be replaced with SLM in Week 3.

        Returns:
            str: One of 'DEFENSIVE', 'MAINTAIN', 'AGGRESSIVE', 'SEEK_LIQUIDITY'
        """
        # Simple rule-based decision logic (placeholder for SLM)

        # Critical condition: seek emergency liquidity
        if context['liquidity_ratio'] < 0.15 or context['capital'] < 2.0:
            return 'SEEK_LIQUIDITY'

        # High risk: go defensive
        if context['risk_score'] > 0.7 or context['crisis_intensity'] > 0.6:
            return 'DEFENSIVE'

        # Moderate risk or failed banks: maintain
        if context['risk_score'] > 0.4 or context['n_failed_banks'] > 0:
            return 'MAINTAIN'

        # Low risk: can be aggressive
        return 'AGGRESSIVE'

    def execute_action(self, action: str):
        """
        Execute the decided action

        DEFENSIVE: Reduce exposure by 10%, increase liquidity buffer
        MAINTAIN: Status quo
        AGGRESSIVE: Increase exposure by 5%
        SEEK_LIQUIDITY: Request Fed intervention
        """
        if action == 'DEFENSIVE':
            # Reduce exposure
            self.assets *= 0.9
            self.liabilities *= 0.9
            # Increase liquidity buffer
            self.liquidity *= 1.1
            self.defensive_mode = True

        elif action == 'MAINTAIN':
            # Status quo - natural market drift
            pass

        elif action == 'AGGRESSIVE':
            # Expand lending
            self.assets *= 1.05
            self.liabilities *= 1.05
            self.defensive_mode = False

        elif action == 'SEEK_LIQUIDITY':
            # Request Fed assistance
            if hasattr(self.model, 'regulator_agent'):
                granted = self.model.regulator_agent.provide_liquidity(self)
                if granted:
                    self.bailout_received = True

    def assess_counterparty_risk(self) -> float:
        """
        Assess risk from counterparty exposures

        Returns float (0-1) representing counterparty risk
        """
        if not self.counterparties:
            return 0.0

        # Check for failed counterparties
        failed_counterparties = 0
        risky_counterparties = 0

        for cp_id in self.counterparties:
            # Find counterparty in bank_agents list
            cp_agent = None
            for bank in self.model.bank_agents:
                if bank.unique_id == cp_id:
                    cp_agent = bank
                    break

            if cp_agent and isinstance(cp_agent, BankAgent):
                if cp_agent.failed:
                    failed_counterparties += 1
                elif cp_agent.risk_score > 0.6:
                    risky_counterparties += 1

        total_counterparties = len(self.counterparties)
        risk = (failed_counterparties * 0.5 + risky_counterparties * 0.3) / total_counterparties
        return min(risk, 1.0)

    def check_failure_condition(self) -> bool:
        """
        Check if bank should fail

        Failure conditions:
        1. Capital below $1B
        2. Liquidity ratio below 10%
        3. Leverage ratio above 40x

        Returns True if should fail
        """
        if self.capital < 1.0:
            return True
        if self.liquidity_ratio < 0.1:
            return True
        if self.leverage_ratio > 40.0:
            return True
        return False

    def fail(self):
        """
        Mark bank as failed and propagate shocks to counterparties
        """
        if self.failed:
            return  # Already failed

        self.failed = True
        self.failure_step = self.model.total_steps

        print(f"💥 {self.name} FAILED at step {self.failure_step}")
        print(f"   Capital: ${self.capital:.1f}B, Liquidity: {self.liquidity_ratio:.1%}")

        # Propagate shock to counterparties
        for cp_id in self.counterparties:
            # Find counterparty in bank_agents list
            cp_agent = None
            for bank in self.model.bank_agents:
                if bank.unique_id == cp_id:
                    cp_agent = bank
                    break

            if cp_agent and isinstance(cp_agent, BankAgent) and not cp_agent.failed:
                cp_agent.absorb_shock(
                    strength=0.3,  # 30% exposure loss
                    source=self
                )

    def absorb_shock(self, strength: float, source: Agent):
        """
        Absorb shock from failed counterparty

        Args:
            strength: Shock magnitude (0-1)
            source: Failed bank agent
        """
        # Direct exposure loss
        exposure_loss = self.assets * 0.1 * strength  # Assume 10% of assets exposed
        self.capital -= exposure_loss

        # Liquidity impact (50% of capital loss becomes liquidity drain)
        liquidity_shock = exposure_loss * 0.5
        self.liquidity -= liquidity_shock

        # Mark-to-market losses in crisis
        if self.model.crisis_intensity > 0.7:
            mtm_loss = self.assets * 0.05 * self.model.crisis_intensity
            self.capital -= mtm_loss

        print(f"   ⚠️  {self.name} absorbed ${exposure_loss:.1f}B shock from {source.name}")
        print(f"       Capital: ${self.capital:.1f}B, Liquidity: ${self.liquidity:.1f}B")


class RegulatorAgent(Agent):
    """
    Regulator agent (Federal Reserve / Treasury)

    Attributes:
        available_funds: Bailout capacity in billions
        intervention_threshold: Crisis trigger level (0-1)
        interest_rate: Policy rate (%)
        bailouts_provided: Count of bailouts

    Actions:
        - Monitor systemic risk
        - Provide emergency liquidity
        - Adjust interest rates
        - Coordinate bailouts
    """

    def __init__(
        self,
        model,
        unique_id: int,
        available_funds: float = 500.0,
        intervention_threshold: float = 0.6
    ):
        super().__init__(model)

        # Set unique_id manually
        self.unique_id = unique_id

        self.available_funds = available_funds  # Bailout capacity ($B)
        self.intervention_threshold = intervention_threshold  # Crisis trigger
        self.interest_rate = 2.0  # Policy rate (%)
        self.bailouts_provided = 0

    def step(self):
        """
        Monitor system and intervene if necessary
        """
        # Calculate systemic risk
        systemic_risk = self.calculate_systemic_risk()

        # Update interest rate based on crisis
        if systemic_risk > 0.8:
            self.interest_rate = max(0.0, self.interest_rate - 0.5)  # Emergency rate cut
        elif systemic_risk < 0.3:
            self.interest_rate = min(5.0, self.interest_rate + 0.25)  # Gradual tightening

    def calculate_systemic_risk(self) -> float:
        """
        Calculate overall systemic risk level

        Returns float (0-1) based on:
        - Number of failed banks
        - Average bank risk scores
        - Market conditions
        """
        banks = self.model.bank_agents

        if not banks:
            return 0.0

        # Failed bank ratio
        failed_ratio = len([b for b in banks if b.failed]) / len(banks)

        # Average risk score of surviving banks
        surviving_banks = [b for b in banks if not b.failed]
        avg_risk = np.mean([b.risk_score for b in surviving_banks]) if surviving_banks else 0.0

        # Market stress
        market_stress = self.model.market_agent.get_stress_level() if hasattr(self.model, 'market_agent') else 0.0

        # Weighted average
        systemic_risk = (failed_ratio * 0.5 + avg_risk * 0.3 + market_stress * 0.2)
        return min(systemic_risk, 1.0)

    def provide_liquidity(self, bank: BankAgent) -> bool:
        """
        Provide emergency liquidity to distressed bank

        Args:
            bank: Bank requesting assistance

        Returns:
            bool: True if liquidity provided, False if denied
        """
        # Calculate needed amount
        liquidity_need = max(bank.liabilities * 0.15 - bank.liquidity, 0)

        # Check if we have funds
        if liquidity_need > self.available_funds:
            print(f"   ❌ Fed cannot bail out {bank.name} (insufficient funds)")
            return False

        # Provide liquidity
        bank.liquidity += liquidity_need
        self.available_funds -= liquidity_need
        self.bailouts_provided += 1

        print(f"   🏦 Fed provided ${liquidity_need:.1f}B to {bank.name}")
        return True


class MarketAgent(Agent):
    """
    Market sentiment agent

    Attributes:
        vix: Volatility index (fear gauge)
        ted_spread: Credit stress indicator
        sentiment: Market confidence (-1 to 1)

    Behaviors:
        - Update market conditions based on crisis
        - Amplify shocks through panic
        - Trigger fire sales
    """

    def __init__(
        self,
        model,
        unique_id: int,
        initial_vix: float = 20.0,
        initial_ted_spread: float = 0.5
    ):
        super().__init__(model)

        # Set unique_id manually
        self.unique_id = unique_id

        self.vix = initial_vix  # Volatility index (10-80)
        self.ted_spread = initial_ted_spread  # TED spread (%)
        self.sentiment = 0.0  # Market confidence (-1 to 1)

    def step(self):
        """
        Update market conditions based on crisis intensity
        """
        # Count failed banks
        banks = self.model.bank_agents
        failed_banks = [b for b in banks if b.failed]
        failed_ratio = len(failed_banks) / len(banks) if banks else 0.0

        # Update VIX (volatility increases with failures)
        target_vix = 20.0 + (failed_ratio * 60.0)  # 20-80 range
        self.vix = self.vix * 0.7 + target_vix * 0.3  # Smooth transition

        # Update TED spread (credit stress)
        target_ted = 0.5 + (failed_ratio * 3.5)  # 0.5-4.0% range
        self.ted_spread = self.ted_spread * 0.7 + target_ted * 0.3

        # Update sentiment (-1 = panic, 0 = neutral, 1 = euphoria)
        self.sentiment = 1.0 - (failed_ratio * 2.0)  # More failures = worse sentiment

    def get_stress_level(self) -> float:
        """
        Calculate overall market stress (0-1)

        Returns float combining VIX and TED spread
        """
        vix_stress = min(self.vix / 80.0, 1.0)
        ted_stress = min(self.ted_spread / 4.0, 1.0)
        return (vix_stress + ted_stress) / 2.0
