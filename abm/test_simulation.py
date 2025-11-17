#!/usr/bin/env python3
"""
Test Script for Mesa ABM Simulation

Runs a basic 10-bank simulation to verify ABM infrastructure is working.

Usage:
    python abm/test_simulation.py
    ./venv/bin/python abm/test_simulation.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abm.model import FinancialCrisisModel
from abm.network import load_network_from_kg, create_default_network
from abm.metrics import CrisisMetricsCollector, analyze_contagion_paths, calculate_systemic_importance
import matplotlib.pyplot as plt


def run_basic_simulation(n_steps: int = 100, n_banks: int = 10, trigger_crisis: bool = True):
    """
    Run a basic ABM simulation

    Args:
        n_steps: Number of simulation steps
        n_banks: Number of bank agents
        trigger_crisis: Whether to trigger exogenous shock

    Returns:
        FinancialCrisisModel: Completed model
    """
    print("=" * 70)
    print("  Financial Crisis ABM - Test Simulation")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Banks: {n_banks}")
    print(f"  Steps: {n_steps}")
    print(f"  Crisis shock: {'Yes (step 30)' if trigger_crisis else 'No'}")
    print()

    # Create model
    print("🏗️  Creating model...")

    # Try to load network from KG
    try:
        network, entity_metadata = load_network_from_kg(entity_limit=n_banks)
        print(f"   ✅ Loaded network from Knowledge Graph")
        print(f"   Nodes: {network.number_of_nodes()}, Edges: {network.number_of_edges()}")
    except Exception as e:
        print(f"   ⚠️  Could not load from KG: {e}")
        network, entity_metadata = create_default_network(n=n_banks)

    model = FinancialCrisisModel(
        n_banks=n_banks,
        network=network,
        initial_capital_range=(5.0, 20.0),
        crisis_trigger_step=30 if trigger_crisis else None,
        random_seed=42
    )

    # Create metrics collector
    metrics = CrisisMetricsCollector(model)

    print(f"   ✅ Model created")
    print(f"\nStarting agents:")
    for bank in model.bank_agents[:5]:  # Show first 5
        print(f"   • {bank.name}: ${bank.capital:.1f}B capital, {bank.liquidity_ratio:.1%} liquidity")
    if len(model.bank_agents) > 5:
        print(f"   ... and {len(model.bank_agents) - 5} more")

    # Run simulation
    print(f"\n🎬 Running simulation...")
    print(f"{'='*70}")

    for step in range(n_steps):
        model.step()
        metrics.collect(step)

        # Print progress every 10 steps
        if (step + 1) % 10 == 0 or len(model.failed_banks) > 0 and step > 0:
            summary = model.get_summary()
            print(f"Step {step + 1:3d}: "
                  f"Failed: {summary['failed_banks']}/{summary['n_banks']} | "
                  f"VIX: {summary['market_vix']:.1f} | "
                  f"Crisis: {summary['crisis_intensity']:.2f} | "
                  f"Bailouts: {summary['bailouts_provided']}")

        # Stop if all banks failed
        if len(model.failed_banks) == n_banks:
            print(f"\n⚠️  All banks failed at step {step + 1}")
            break

    print(f"{'='*70}\n")

    # Print results
    print("📊 Simulation Results:")
    print("=" * 70)

    summary = model.get_summary()
    print(f"\nFinal State (Step {summary['step']}):")
    print(f"  • Total banks: {summary['n_banks']}")
    print(f"  • Failed banks: {summary['failed_banks']} ({summary['failed_banks']/summary['n_banks']*100:.1f}%)")
    print(f"  • Surviving banks: {summary['surviving_banks']}")
    print(f"  • Crisis intensity: {summary['crisis_intensity']:.2%}")

    print(f"\nMarket Indicators:")
    print(f"  • VIX: {summary['market_vix']:.1f}")
    print(f"  • TED Spread: {summary['market_ted_spread']:.2f}%")

    print(f"\nRegulatory Response:")
    print(f"  • Interest rate: {summary['regulator_interest_rate']:.2f}%")
    print(f"  • Bailouts provided: {summary['bailouts_provided']}")

    if summary['surviving_banks'] > 0:
        print(f"\nSurviving Banks:")
        print(f"  • Avg capital: ${summary['avg_capital']:.1f}B")
        print(f"  • Avg liquidity ratio: {summary['avg_liquidity_ratio']:.1%}")

    # Bank failures
    if model.failed_banks:
        print(f"\nFailed Banks:")
        for bank in sorted(model.failed_banks, key=lambda b: b.failure_step):
            print(f"  • {bank.name}: Step {bank.failure_step}, Capital: ${bank.capital:.1f}B")

    # Systemic importance
    print(f"\nSystemic Importance (Top 5):")
    importance = calculate_systemic_importance(model)
    for bank_name, score in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {bank_name}: {score:.3f}")

    # Contagion analysis
    contagion_paths = analyze_contagion_paths(model)
    if any(path['affected_count'] > 0 for path in contagion_paths):
        print(f"\nContagion Paths:")
        for path in contagion_paths:
            if path['affected_count'] > 0:
                print(f"  • {path['source']} (step {path['failure_step']}) → {path['affected_count']} banks")

    print("\n" + "=" * 70)

    # Export results
    print(f"\n💾 Exporting results...")

    # Export simulation data
    model.export_results('results/abm_simulation_results.json')

    # Export network visualization
    from abm.network import export_network_viz
    export_network_viz(network, entity_metadata, 'results/abm_network.json')

    # Generate crisis timeline plot
    metrics.plot_crisis_timeline(save_path='results/abm_crisis_timeline.png')

    # Generate report
    report = metrics.generate_report()

    print(f"\n✅ Simulation complete!")
    print(f"\nFiles created:")
    print(f"  • results/abm_simulation_results.json (simulation data)")
    print(f"  • results/abm_network.json (network topology)")
    print(f"  • results/abm_crisis_timeline.png (visualization)")

    return model


def main():
    """Main test function"""
    # Run simulation
    model = run_basic_simulation(
        n_steps=100,
        n_banks=10,
        trigger_crisis=True
    )

    print(f"\n{'='*70}")
    print("  Test completed successfully! 🎉")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Review results in results/ folder")
    print(f"  2. Adjust parameters in test_simulation.py")
    print(f"  3. Integrate with Knowledge Graph (Week 4)")
    print(f"  4. Add SLM decision-making (Week 3)")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
