"""
Casino Gambling Model — Dynamic Programming Solver

This module solves for the optimal betting fraction f* in a stochastic
casino environment where the casino opens with probability S each period.

The model uses backward induction on a discretized wealth grid to solve
the Bellman equation:

    V_t(m) = max_f { (1-S) * U(wealth_after_bet) 
                   + S * [ p * V_{t-1}(wealth_if_win) 
                         + (1-p) * V_{t-1}(wealth_if_lose) ] }

Three utility functions are supported to study different risk preferences:
  - "power":      U(x) = 2*sqrt(x)        — risk averse (concave)
  - "log":        U(x) = log(x)           — risk neutral (concave)
  - "risk_lover": U(x) = x^2 / 2          — risk lover (convex)

Reference: architecture.md for full mathematical derivation.
"""

import numpy as np


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def utility_power(x, alpha=0.5):
    """
    CRRA (Constant Relative Risk Aversion) power utility.
    
        U(x) = x^(1-alpha) / (1-alpha)
    
    For alpha=0.5: U(x) = 2*sqrt(x)
    
    This is a CONCAVE function — the player is risk averse.
    Marginal utility decreases as wealth increases, so the player
    prefers safe outcomes and bets conservatively.
    
    Parameters
    ----------
    x : array-like
        Wealth level(s).
    alpha : float
        Risk aversion parameter. Higher alpha = more risk averse.
        alpha=0 gives linear utility (risk neutral).
    
    Returns
    -------
    array-like
        Utility values.
    """
    return x ** (1 - alpha) / (1 - alpha)


def utility_log(x):
    """
    Logarithmic utility.
    
        U(x) = log(x)
    
    This is the standard Kelly criterion utility function.
    It is CONCAVE — the player is mildly risk averse.
    Maximizing log-wealth is equivalent to maximizing the
    long-run geometric growth rate of wealth.
    
    Parameters
    ----------
    x : array-like
        Wealth level(s).
    
    Returns
    -------
    array-like
        Utility values (natural logarithm).
    """
    return np.log(x)


def utility_risk_lover(x, alpha=2.0):
    """
    Convex (risk-loving) power utility.
    
        U(x) = x^alpha / alpha    (alpha > 1)
    
    For alpha=2: U(x) = x^2 / 2
    
    This is a CONVEX function — the player is risk seeking.
    Marginal utility INCREASES as wealth increases, so the player
    prefers risky gambles and bets aggressively (often everything).
    
    Parameters
    ----------
    x : array-like
        Wealth level(s).
    alpha : float
        Risk-seeking parameter. Must be > 1.
        Higher alpha = more risk seeking.
    
    Returns
    -------
    array-like
        Utility values.
    """
    return x ** alpha / alpha


# =============================================================================
# INTERPOLATION HELPER
# =============================================================================

def interp(V_prev, wealth_grid, m_val):
    """
    Vectorized linear interpolation of the value function.
    
    The DP is solved on a discrete wealth grid. When the wealth after
    a bet falls between grid points, we interpolate linearly to estimate
    the value function at that wealth level.
    
    Parameters
    ----------
    V_prev : np.ndarray
        Value function from the previous period (shape: n_grid).
    wealth_grid : np.ndarray
        Discretized wealth levels (shape: n_grid, strictly increasing).
    m_val : np.ndarray
        Wealth points to evaluate at (shape: any, values in [grid_min, grid_max]).
    
    Returns
    -------
    np.ndarray
        Interpolated value function values at m_val.
    """
    # Find the index of the grid point just below each m_val
    idx = np.searchsorted(wealth_grid, m_val) - 1
    # Clamp to valid range [0, n_grid-2] so idx and idx+1 are both valid
    idx = np.clip(idx, 0, len(wealth_grid) - 2)
    # Compute the fractional distance between grid points
    frac = (m_val - wealth_grid[idx]) / (wealth_grid[idx + 1] - wealth_grid[idx])
    # Linear interpolation: V = V[idx]*(1-frac) + V[idx+1]*frac
    return V_prev[idx] * (1 - frac) + V_prev[idx + 1] * frac


# =============================================================================
# MAIN DP SOLVER
# =============================================================================

def solve_dp(p, S, g, m0, T, utility="log", n_grid=300, m_max_factor=3.0, n_f=80):
    """
    Solve the casino gambling DP via backward induction.
    
    Algorithm:
    1. Discretize wealth into a grid of n_grid points from 0.01 to m0*m_max_factor.
    2. Discretize the betting fraction f into n_f points from 0 to 1.
    3. Precompute wealth outcomes for all (m, f) pairs using broadcasting.
    4. Initialize V_0(m) = U(m) (terminal payoff when no rounds remain).
    5. For t = 1 to T (backward):
         For each wealth level m on the grid:
           - Compute expected value if casino opens (gamble happens)
           - Compute value if casino closes (wealth preserved)
           - Take the weighted average and pick the best f.
    6. After filling the value function table, extract the optimal f at m0.
    
    Parameters
    ----------
    p : float
        Probability of winning a single gamble (0 < p < 1).
    S : float
        Probability the casino is open next period (0 < S < 1).
    g : float
        Win/loss rate — fraction of bet won on a win, lost on a loss.
        For example, g=0.5 means you win or lose 50% of your bet.
    m0 : float
        Initial wealth.
    T : int
        Number of periods (time horizon).
    utility : str
        Which utility function to use:
          "power"      — risk averse:  U(x) = 2*sqrt(x)
          "log"        — risk neutral: U(x) = log(x)
          "risk_lover" — risk lover:   U(x) = x^2/2
    n_grid : int
        Number of wealth grid points. More = more accurate but slower.
    m_max_factor : float
        Maximum wealth on the grid as a multiple of m0.
        E.g., m_max_factor=3 means grid goes up to 3*m0.
    n_f : int
        Number of betting fraction candidates to try.
    
    Returns
    -------
    f_opt : float
        Optimal betting fraction at wealth m0 with T periods remaining.
    V : np.ndarray
        Full value function table (T+1 x n_grid).
    wealth_grid : np.ndarray
        The wealth grid used for discretization.
    """
    # --- Step 1: Select the utility function ---
    if utility == "log":
        U = utility_log
    elif utility == "power":
        U = lambda x: utility_power(x, alpha=0.5)
    elif utility == "risk_lover":
        U = lambda x: utility_risk_lover(x, alpha=2.0)
    else:
        raise ValueError(f"Unknown utility: {utility}. Choose 'log', 'power', or 'risk_lover'.")

    # --- Step 2: Set up the wealth and betting fraction grids ---
    wealth_grid = np.linspace(0.01, m0 * m_max_factor, n_grid)
    f_grid = np.linspace(0, 1, n_f)

    # --- Step 3: Precompute wealth outcomes for all (m, f) pairs ---
    # Using numpy broadcasting: m2d is (n_grid, 1), f2d is (1, n_f)
    # Result matrices are (n_grid, n_f) — one entry per (wealth, bet fraction) pair.
    m2d = wealth_grid[:, None]   # Column vector: each wealth level
    f2d = f_grid[None, :]        # Row vector:    each bet fraction

    # If you bet fraction f of wealth m and WIN:
    #   wealth_win = f*m*(1+g) + (1-f)*m = m * [f*(1+g) + (1-f)]
    # If you bet fraction f of wealth m and LOSE:
    #   wealth_lose = f*m*(1-g) + (1-f)*m = m * [f*(1-g) + (1-f)]
    wealth_win  = m2d * (f2d * (1 + g) + (1 - f2d))   # (n_grid, n_f)
    wealth_lose = m2d * (f2d * (1 - g) + (1 - f2d))   # (n_grid, n_f)

    # --- Step 4: Initialize the value function ---
    # V[t, i] = max expected utility with t periods left, starting at wealth_grid[i]
    # At t=0 (no periods left), the value is just the utility of current wealth.
    V = np.zeros((T + 1, n_grid))
    V[0, :] = U(wealth_grid)

    # --- Step 5: Backward induction ---
    for t in range(1, T + 1):
        V_prev = V[t - 1]  # Value function from one period earlier

        # Expected value if casino OPENS (gamble happens):
        #   With prob p:  you win  -> value is V_{t-1}(wealth_win)
        #   With prob 1-p: you lose -> value is V_{t-1}(wealth_lose)
        EV_win  = interp(V_prev, wealth_grid, wealth_win)    # (n_grid, n_f)
        EV_lose = interp(V_prev, wealth_grid, wealth_lose)   # (n_grid, n_f)
        EV_open = p * EV_win + (1 - p) * EV_lose             # (n_grid, n_f)

        # Expected value if casino CLOSES (no gamble, wealth preserved):
        #   Your wealth stays at m, so the value is U(m).
        EV_close = U(wealth_grid)[:, None]                   # (n_grid, 1)

        # Total expected value = weighted average of open vs. close:
        #   With prob (1-S): casino closes -> get EV_close
        #   With prob S:     casino opens  -> get EV_open
        EV_total = (1 - S) * EV_close + S * EV_open          # (n_grid, n_f)

        # For each wealth level, pick the f that maximizes expected value
        V[t, :] = np.max(EV_total, axis=1)

    # --- Step 6: Extract optimal f at the initial wealth m0 ---
    # Re-evaluate at m0 specifically (m0 may not be exactly on the grid)
    EV_close_m0 = U(m0)
    w_win  = m0 * (f_grid * (1 + g) + (1 - f_grid))   # Wealth if win, for each f
    w_lose = m0 * (f_grid * (1 - g) + (1 - f_grid))   # Wealth if lose, for each f
    ev_win  = interp(V[T - 1], wealth_grid, w_win)
    ev_lose = interp(V[T - 1], wealth_grid, w_lose)
    ev_open = p * ev_win + (1 - p) * ev_lose
    ev_total = (1 - S) * EV_close_m0 + S * ev_open

    # The optimal f is the one that gives the highest total expected value
    f_opt = f_grid[np.argmax(ev_total)]

    return f_opt, V, wealth_grid


# =============================================================================
# KELLY CRITERION BENCHMARK
# =============================================================================

def kelly_criterion(p):
    """
    Kelly criterion optimal betting fraction for an even-odds bet.
    
        f* = 2p - 1
    
    This is the classical result when:
      - The casino is always open (S = 1)
      - The bet is even-money (win/lose the same amount)
      - The utility is logarithmic (maximizing geometric growth)
    
    For p > 0.5, the player has an edge and should bet a positive fraction.
    For p <= 0.5, the player has no edge and should not bet (f* = 0).
    
    Parameters
    ----------
    p : float
        Probability of winning a single gamble.
    
    Returns
    -------
    float
        Optimal betting fraction.
    """
    return 2 * p - 1


# =============================================================================
# MAIN: Run the solver and display results
# =============================================================================

if __name__ == "__main__":
    # Default parameters for the model
    params = {"p": 0.8, "S": 0.3, "g": 0.5, "m0": 100, "T": 50}

    print("=" * 60)
    print("CASINO GAMBLING MODEL — Dynamic Programming Solver")
    print("=" * 60)
    print(f"\nParameters:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    print()

    # --- Solve for each utility type and display optimal f ---
    f_log, _, _ = solve_dp(utility="log", **params)
    print(f"Optimal f (log utility / risk neutral):  {f_log:.4f}")

    f_power, _, _ = solve_dp(utility="power", **params)
    print(f"Optimal f (power utility / risk averse): {f_power:.4f}")

    f_risk, _, _ = solve_dp(utility="risk_lover", **params)
    print(f"Optimal f (risk lover):                  {f_risk:.4f}")

    print(f"Kelly criterion benchmark:               {kelly_criterion(params['p']):.4f}")

    # --- Sweep: f* vs p for different S values (log utility) ---
    print("\n" + "=" * 60)
    print("SWEEP: f* vs p for different S values (log utility)")
    print("=" * 60)

    for S_val in [0.7, 0.9, 0.99]:
        print(f"\n  S = {S_val}:")
        for p_val in [0.5, 0.6, 0.7, 0.8, 0.9]:
            f_opt, _, _ = solve_dp(p=p_val, S=S_val, g=0.5, m0=100, T=30,
                                   utility="log", n_grid=200, n_f=60)
            kelly = kelly_criterion(p_val)
            print(f"    p={p_val:.1f} -> f*={f_opt:.4f}  (Kelly={kelly:.4f})")

    # --- Sweep: f* vs S for different utility types (p=0.6) ---
    print("\n" + "=" * 60)
    print("SWEEP: f* vs S for different utility types (p=0.6)")
    print("=" * 60)

    for S_val in [0.3, 0.5, 0.7, 0.9, 0.99]:
        f_log_s, _, _ = solve_dp(p=0.6, S=S_val, g=0.5, m0=100, T=30,
                                 utility="log", n_grid=200, n_f=60)
        f_power_s, _, _ = solve_dp(p=0.6, S=S_val, g=0.5, m0=100, T=30,
                                   utility="power", n_grid=200, n_f=60)
        f_risk_s, _, _ = solve_dp(p=0.6, S=S_val, g=0.5, m0=100, T=30,
                                  utility="risk_lover", n_grid=200, n_f=60)
        print(f"  S={S_val:.2f} | log={f_log_s:.4f}  power={f_power_s:.4f}  "
              f"risk_lover={f_risk_s:.4f}  (Kelly={kelly_criterion(0.6):.4f})")
