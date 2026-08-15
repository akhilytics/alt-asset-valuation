"""
Whisky Cask Investment — Monte Carlo Valuation Model
Author: Akhila Nayak

Models a single 500-litre new-fill Scotch hogshead over a 12-year hold.
Runs 10,000 simulations under two demand scenarios (base case vs demand-decline)
to produce a distribution of possible IRR outcomes rather than a single point estimate.

Sources and assumption ranges are documented in data/sources.md.
"""

import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

# --- Fixed assumptions (don't vary between simulations) ---
starting_litres = 500
starting_abv = 63.5
holding_years = 12
purchase_price = 400000        # INR, ~500L new-fill hogshead
annual_cost = 150               # storage + insurance, INR/year
exit_commission_pct = 0.10      # broker commission on sale
illiquidity_haircut_pct = 0.05  # discount to book value on exit


def run_simulation(n_sims, aging_premium_low, aging_premium_high):
    """
    Runs the full cask model n_sims times. Angel's share and the aging
    premium are redrawn randomly each run from the given ranges. Also
    checks the ABV cliff each year — if strength drops below 40%, the
    cask can no longer legally be sold as Scotch, and the payout is zero.
    """
    results = []
    for _ in range(n_sims):
        angels_share = np.random.uniform(0.015, 0.025)
        aging_premium_rate = np.random.uniform(aging_premium_low, aging_premium_high)
        base_price_per_litre = purchase_price / starting_litres

        litres = starting_litres
        abv = starting_abv
        total_costs = 0
        unsellable = False

        for year in range(1, holding_years + 1):
            litres = litres * (1 - angels_share)
            abv = abv - np.random.uniform(0.2, 0.4)
            price_per_litre = base_price_per_litre * (1 + aging_premium_rate) ** year
            gross_value = litres * price_per_litre
            total_costs += annual_cost

            if abv < 40:
                unsellable = True

        if unsellable:
            net_sale_proceeds = 0
        else:
            exit_commission = gross_value * exit_commission_pct
            illiquidity_loss = gross_value * illiquidity_haircut_pct
            net_sale_proceeds = gross_value - exit_commission - illiquidity_loss - total_costs

        cashflows = [-purchase_price] + [0] * (holding_years - 1) + [net_sale_proceeds]
        irr = npf.irr(cashflows)
        results.append(irr)

    return np.array(results)


def run_single(angels_share, aging_premium_rate):
    """Deterministic single run — used for one-at-a-time sensitivity testing."""
    base_price_per_litre = purchase_price / starting_litres
    litres = starting_litres
    total_costs = 0

    for year in range(1, holding_years + 1):
        litres = litres * (1 - angels_share)
        price_per_litre = base_price_per_litre * (1 + aging_premium_rate) ** year
        gross_value = litres * price_per_litre
        total_costs += annual_cost

    exit_commission = gross_value * exit_commission_pct
    illiquidity_loss = gross_value * illiquidity_haircut_pct
    net_sale_proceeds = gross_value - exit_commission - illiquidity_loss - total_costs

    cashflows = [-purchase_price] + [0] * (holding_years - 1) + [net_sale_proceeds]
    return npf.irr(cashflows) * 100


def summarize(name, irrs):
    print(f"\n--- {name} ---")
    print(f"Mean IRR: {np.mean(irrs) * 100:.2f}%")
    print(f"Median IRR: {np.median(irrs) * 100:.2f}%")
    print(f"Probability of loss: {np.mean(irrs < 0) * 100:.1f}%")
    print(f"5th percentile: {np.percentile(irrs, 5) * 100:.2f}%")
    print(f"95th percentile: {np.percentile(irrs, 95) * 100:.2f}%")


# --- Run both scenarios ---
base_case = run_simulation(10000, 0.05, 0.11)
demand_decline_case = run_simulation(10000, -0.10, 0.03)

summarize("Base case (demand holds)", base_case)
summarize("Demand-decline case", demand_decline_case)

# --- Chart 1: return distribution, base vs demand-decline ---
plt.figure(figsize=(10, 6))
plt.hist(base_case * 100, bins=50, alpha=0.6, label="Base case (demand holds)", color="steelblue")
plt.hist(demand_decline_case * 100, bins=50, alpha=0.6, label="Demand-decline case", color="firebrick")
plt.axvline(0, color="black", linestyle="--", linewidth=1)
plt.xlabel("IRR (%)")
plt.ylabel("Number of simulations")
plt.title("Whisky Cask Investment: Return Distribution (Base vs Demand-Decline)")
plt.legend()
plt.tight_layout()
plt.savefig("charts/cask_returns_histogram.png")
plt.show()

# --- Sensitivity: one-at-a-time swing test ---
irr_low_angels = run_single(0.015, 0.08)
irr_high_angels = run_single(0.025, 0.08)
irr_low_aging = run_single(0.02, 0.05)
irr_high_aging = run_single(0.02, 0.11)

print(f"\nAngel's share swing: {irr_low_angels:.2f}% to {irr_high_angels:.2f}%")
print(f"Aging premium swing: {irr_low_aging:.2f}% to {irr_high_aging:.2f}%")

# --- Chart 2: sensitivity tornado ---
plt.figure(figsize=(8, 4))
inputs = ["Angel's share", "Aging premium"]
lows = [irr_low_angels, irr_low_aging]
highs = [irr_high_angels, irr_high_aging]

for name, low, high in zip(inputs, lows, highs):
    plt.barh(name, high - low, left=min(low, high), color="darkorange")

plt.axvline(0, color="black", linestyle="--", linewidth=1)
plt.xlabel("IRR (%)")
plt.title("Sensitivity: Impact of Each Input on IRR")
plt.tight_layout()
plt.savefig("charts/cask_sensitivity_tornado.png")
plt.show()

# --- Chart 3: value vs quality divergence (illustrative, not simulation output) ---
years_range = np.arange(0, 31)
quality_curve = np.where(
    years_range <= 18,
    100 * np.log(years_range + 1) / np.log(19),
    100 - 0.3 * (years_range - 18) ** 1.5
)
value_curve = 20 + 3 * years_range

plt.figure(figsize=(9, 5))
plt.plot(years_range, quality_curve, label="Perceived quality", color="seagreen", linewidth=2)
plt.plot(years_range, value_curve, label="Marketed value", color="firebrick", linewidth=2)
plt.axvline(18, color="gray", linestyle="--", linewidth=1, label="Quality peak (~18 yrs)")
plt.xlabel("Years in cask")
plt.ylabel("Index (illustrative, not to scale)")
plt.title("The Value-Quality Divergence: Marketed Value vs Perceived Quality")
plt.legend()
plt.tight_layout()
plt.savefig("charts/cask_value_quality_divergence.png")
plt.show()