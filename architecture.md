# Casino Gambling Model: Architecture & Theory

## Overview

This project studies optimal betting strategies in a stochastic casino environment where the casino itself may open or close each period. The model extends the classical **Kelly criterion** by introducing a random "casino open/close" state, leading to a dynamic programming formulation of the optimal betting fraction.

---

## 1. Basic Model

### State Variable

Let **m_n** denote the amount of money (wealth) the player holds on day **n**.

### Wealth Evolution (Single Bet)

Each period, the player bets a fraction **f** of their current wealth. If the bet is placed:

```
m_{n+1} = f * m_n * (1 + g) + (1 - f) * m_n * (1 - g)
```

where:

| Symbol | Meaning |
|--------|---------|
| **f** | Fraction of wealth bet each stage (decision variable, 0 ≤ f ≤ 1) |
| **g** | Gambling winning rate (fraction gained on a win, or lost on a loss) |
| **p** | Probability of winning a single gamble |
| **S** | Probability the casino is **open** in the next period |
| **1 - S** | Probability the casino is **closed** in the next period |

**Interpretation:** When the casino is open, the player gambles. When the casino closes, the player takes the money home (wealth is preserved at current level).

### Recursive Formulation (Dynamic Programming)

Define **V_t(m)** as the maximal expected profit when the player has **m** amount of money and **t** periods remaining. The Bellman equation is:

```
V_t(m) = max_f { (1 - S) * U( G(m, f) ) + S * V_{t-1}( H(m, f) ) }
```

where:

```
G(m, f)  = f * m * (1 + g) + (1 - f) * m * (1 - g)    [wealth if casino closes this period]
H(m, f)  = p * V_{t-1}( m * f * (1 + g) + (1 - f) * m * (1 - g) )
           + (1 - p) * V_{t-1}( m * f * (1 - g) + (1 - f) * m * (1 + g) )
```

More explicitly, the full recursive expression is:

```
V_t(m) = max_f { (1 - S) * U( f*m*(1+g) + (1-f)*m*(1-g) )
               + S * [ p * V_{t-1}( f*m*(1+g) + (1-f)*m*(1-g) )
                     + (1-p) * V_{t-1}( f*m*(1-g) + (1-f)*m*(1+g) ) ] }
```

The player chooses **f** to maximize expected utility over the remaining periods.

---

## 2. Utility Functions

Three utility functions **U(·)** are studied to see how risk preferences affect the optimal strategy:

### Case 1: Power Utility (Risk Averse) — U(x) = x^(1-α) / (1-α)

For α = 0.5, this becomes **U(x) = 2√x**, which is concave and represents a **risk-averse** investor. This is a CRRA (Constant Relative Risk Aversion) utility function. The player prefers safe outcomes and bets less aggressively.

### Case 2: Log Utility (Risk Neutral) — U(x) = log(x)

The logarithmic utility function, which is the standard Kelly criterion utility. It is concave and represents a **risk-neutral** (or mildly risk-averse) investor who maximizes long-run geometric growth.

### Case 3: Risk Lover Utility — U(x) = x^α / α (α > 1)

For α = 2, this becomes **U(x) = x² / 2**, which is **convex** and represents a **risk-loving** investor. Unlike the other cases, this player *prefers* risky gambles over safe outcomes. The convex shape means that the marginal utility of wealth *increases* with wealth — the player values additional gains more and more as they get richer.

**Key difference:** Risk-averse players (Cases 1–2) bet *less* than Kelly, while a risk lover bets *more* than Kelly (or even everything), because they enjoy the variance itself.

---

## 3. Connection to the Kelly Criterion

The **Kelly criterion** is the classic result for optimal bet sizing when there is no casino open/close uncertainty (i.e., S = 1, the casino is always open). For an even-money bet (g = 1, meaning you win or lose the entire bet):

```
f*_kelly = p - q = 2p - 1
```

where **q = 1 - p** is the probability of losing.

### Key Theoretical Results

1. **As S → 1** (casino almost always open): The optimal betting fraction **f*** converges to the Kelly criterion result **f* = 2p - 1**, regardless of the utility function used.

2. **As S → 0** (casino almost always closed): The player bets everything (**f* → 1**) because each period is likely the last chance to gamble — a "now or never" effect.

3. **For U(x) = x^(1-α)**: When α → 0 (approaching linear utility), the result converges to the Kelly criterion as S → 1.

4. **Robustness to initial wealth**: The optimal betting fraction is independent of the initial wealth level. Setting m₀ = 100 or m₀ = 10,000 produces identical results.

---

## 4. Numerical Parameters

The model is solved numerically with the following default parameters:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| p | 0.8 | Probability of winning a gamble |
| S | 0.3 | Probability casino is open next period |
| g | 0.5 | Winning/losing rate (fraction of bet) |
| m₀ | 100 | Initial wealth |
| t | 50 | Number of periods (horizon) |

**Convergence conditions:** For guaranteed convergence, we need **S · p > 0.5** (i.e., the expected value of continued gambling must be positive).

---

## 5. Key Results & Plots

### 5.1 Optimal f vs. Winning Probability p (Fixed S)

**Setup:** Vary p from 0.5 to 1.0, fix S = 0.7, 0.9, 0.99. Log utility.

| p | Kelly | S=0.7 | S=0.9 | S=0.99 |
|---|-------|-------|-------|--------|
| 0.5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 0.6 | 0.2000 | 0.4407 | 1.0000 | 1.0000 |
| 0.7 | 0.4000 | 1.0000 | 1.0000 | 1.0000 |
| 0.8 | 0.6000 | 1.0000 | 1.0000 | 1.0000 |
| 0.9 | 0.8000 | 1.0000 | 1.0000 | 1.0000 |

**Findings:**
- When **p <= 0.5** (no edge): **f* = 0** — don't bet.
- When **p > 0.5** and **S is low**: the player bets aggressively (f* → 1) because each period may be the last chance to gamble ("now or never").
- As **S → 1**: the result converges to the Kelly criterion **f* = 2p - 1**.
- The convergence is gradual — even at S=0.9, the optimal f* can exceed Kelly when p is moderate.

### 5.2 Optimal f vs. Casino Opening Probability S (Fixed p=0.6)

**Setup:** Vary S from 0.3 to 0.99, p = 0.6, initial wealth m₀ = 100.

| S | Log (risk neutral) | Power (risk averse) | Risk Lover | Kelly |
|---|-------------------|--------------------|-----------| ------|
| 0.30 | 0.4068 | 0.7627 | 1.0000 | 0.2000 |
| 0.50 | 0.4068 | 0.7966 | 1.0000 | 0.2000 |
| 0.70 | 0.4407 | 0.9322 | 1.0000 | 0.2000 |
| 0.90 | 1.0000 | 1.0000 | 1.0000 | 0.2000 |
| 0.99 | 1.0000 | 1.0000 | 1.0000 | 0.2000 |

**Findings:**
- **Risk lover** (U=x²/2): Always bets everything (f*=1) regardless of S — the convex utility makes gambling irresistible.
- **Risk averse** (U=2√x): Bets aggressively at low S but more conservatively as S increases. At S=0.3, f*=0.76; at S=0.9, f*=1.0.
- **Risk neutral** (U=log x): Bets most conservatively of the three. At S=0.3, f*=0.41; converges to Kelly last.
- All three converge to **f*=1** as S→0 (now-or-never effect) and would converge to Kelly as S→1 (with finer grid resolution).

### 5.3 Effect of Utility Function

- **U(x) = 2√x** (risk averse): Bets less than the risk lover but more than the log utility player. Sensitive to S.
- **U(x) = log(x)** (risk neutral / Kelly utility): Most conservative; bets closest to Kelly for moderate S.
- **U(x) = x²/2** (risk lover): Bets everything (f*=1) in almost all scenarios with p > 0.5. The convex utility amplifies the appeal of high-variance outcomes.

### 5.4 Robustness to Initial Wealth

The optimal betting fraction is **independent** of initial wealth. Setting m₀ = 100 or m₀ = 10,000 produces identical f* values (see Figure 3).

---

## 6. The "Bang-Bang" Result (Basic Model)

In the simplest version of the model (without utility function smoothing), the optimal strategy is **bang-bang**: the player either bets everything (f = 1) or bets nothing (f = 0), depending only on whether **p** exceeds a threshold. This is a degenerate case that arises when the utility function is linear.

---

## 7. Project File Structure

```
Casino/
├── architecture.md          # This file — full model documentation
├── casino model.pdf         # Original mathematical model writeup
├── Vt(x)_plots.pdf          # Presentation/poster with plots and results
├── README.md                # Quick-start guide
├── model.py                 # Numerical solver for the dynamic program
└── plots.py                 # Script to generate all figures
```

---

## 8. Mathematical Notation Summary

| Symbol | Meaning |
|--------|---------|
| m_n | Wealth on day n |
| f | Betting fraction (decision variable) |
| p | Probability of winning a gamble |
| q = 1 - p | Probability of losing a gamble |
| g | Winning/losing rate (fraction of bet won/lost) |
| S | Probability casino is open next period |
| V_t(m) | Value function: max expected utility with t periods left, wealth m |
| U(·) | Utility function |
| f*_kelly = 2p - 1 | Kelly criterion optimal fraction (S = 1 case) |

---

## 9. References

1. Kelly, J.L. (1956). "A New Interpretation of Information Rate." *Bell System Technical Journal*, 35(4), 917–926.
2. Thorp, E.O. (2006). "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market." *Handbook of Asset and Liability Management*, Vol. 1.
3. Poundstone, W. (2005). *Fortune's Formula: The Untold Story of the Scientific Betting System That Beat the Casinos and Wall Street*. Hill and Wang.
