# Whisky Cask Investment — A Monte Carlo Risk Model

A valuation and risk model for an illiquid alternative asset (Scotch whisky casks), built to stress-test the marketed returns against physical decay, exit costs, illiquidity, and a demand-decline scenario — from the perspective of an Indian investor buying into a UK-based asset class.

## The thesis

Cask investment platforms market whisky as a tax-efficient, steadily-appreciating store of value. This project tests that claim with a 10,000-run Monte Carlo simulation rather than a single point estimate, and asks what the real distribution of returns looks like once you account for evaporation, ABV limits, broker costs, illiquidity, and the possibility that whisky demand doesn't hold up over a 10-15 year hold.

## The finding

Under a base case where demand holds steady, the model returns a mean IRR of **4.40%**, with 90% of outcomes between 1.7% and 7.0%, and zero losses across 10,000 runs. Under a demand-decline scenario — grounded in a real 53% drop in Scotch auction values between late 2024 and early 2025 — every single simulation loses money, averaging **-6.8%**. The two distributions barely overlap. There's very little middle ground between "modest win" and "loss," and the deciding factor is the aging premium (price appreciation), not the evaporation rate most marketing focuses on.

Full writeup: [`Investment_Memo.md`](./Investment_Memo.md)

## Repo structure

```
alt-asset-valuation/
├── cask_model.py              # the model — run this
├── Investment_Memo.md         # full writeup with findings and verdict
├── README.md
├── charts/                    # output visualisations
│   ├── cask_returns_histogram.png
│   ├── cask_sensitivity_tornado.png
│   └── cask_value_quality_divergence.png
└── data/
    └── sources.md             # where every assumption range came from
```

## How to run it

```bash
pip install numpy pandas matplotlib numpy_financial
python cask_model.py
```

This runs both scenarios (10,000 simulations each), prints summary statistics to the console, and regenerates all three charts into `/charts`.

## What this doesn't model (yet)

Indian capital gains tax on the eventual sale, and GBP/INR currency movement over the holding period. Both apply to a real Indian buyer and would change the after-tax, after-FX number. The UK's capital-gains exemption on whisky casks (the "tax-free" pitch most marketing leans on) does not extend to Indian tax residents — see `data/sources.md` for the detail.

## Why whisky

During my CA articleship I did consulting work for a wine business, which got me curious about alcohol as an asset class rather than just a product. Cask investing turned out to be a genuinely interesting illiquid-asset valuation problem: no public price, physical decay built into the asset itself, and a marketed return story that doesn't fully survive contact with a proper risk model.

## Built with

Python, numpy, numpy_financial, matplotlib.
