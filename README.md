# Casino Gambling Model

Optimal betting strategies in a stochastic casino environment with random open/close states.

## Problem

A player gambles at a casino that opens with probability **S** each period. The player must decide what fraction **f** of their wealth to bet each round to maximize expected utility over a finite horizon.

## Key Result

As the casino opening probability **S → 1**, the optimal betting fraction converges to the **Kelly criterion**: `f* = 2p - 1`, where `p` is the probability of winning a gamble.

## Utility Functions

| Type | Function | Shape | Behavior |
|------|----------|-------|----------|
| Risk Averse | `U(x) = 2√x` | Concave | Bets less than Kelly |
| Risk Neutral | `U(x) = log(x)` | Concave | Bets close to Kelly |
| Risk Lover | `U(x) = x²/2` | Convex | Bets more than Kelly |

## Files

| File | Description |
|------|-------------|
| `architecture.md` | Full mathematical model and theory |
| `model.py` | Numerical dynamic programming solver |
| `plots.py` | Generate all figures from the paper |
| `casino model.pdf` | Original model writeup |
| `Vt(x)_plots.pdf` | Presentation with result plots |

## Quick Start

```bash
pip install numpy matplotlib
python model.py       # Run the solver with default parameters
python plots.py       # Generate all plots
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `p` | 0.8 | Win probability |
| `S` | 0.3 | Casino open probability |
| `g` | 0.5 | Win/loss rate |
| `m0` | 100 | Initial wealth |
| `T` | 50 | Time horizon |
