import numpy as np


def utility_power(x, alpha=0.5):
    """Power utility: U(x) = x^(1-alpha) / (1-alpha)."""
    return x ** (1 - alpha) / (1 - alpha)


def utility_log(x):
    """Log utility: U(x) = log(x)."""
    return np.log(x)


def utility_risk_lover(x, alpha=2.0):
    """Risk lover utility: U(x) = x^alpha / alpha (convex, alpha > 1)."""
    return x ** alpha / alpha


def interp(V_prev, wealth_grid, m_val):
    """Vectorized linear interpolation of V_prev at points m_val."""
    idx = np.searchsorted(wealth_grid, m_val) - 1
    idx = np.clip(idx, 0, len(wealth_grid) - 2)
    frac = (m_val - wealth_grid[idx]) / (wealth_grid[idx + 1] - wealth_grid[idx])
    return V_prev[idx] * (1 - frac) + V_prev[idx + 1] * frac


def solve_dp(p, S, g, m0, T, utility="log", n_grid=300, m_max_factor=3.0, n_f=80):
    """
    Solve the DP via backward induction with vectorized operations.

    Returns: (f_opt, V, wealth_grid)
    """
    if utility == "log":
        U = utility_log
    elif utility == "power":
        U = lambda x: utility_power(x, alpha=0.5)
    elif utility == "risk_lover":
        U = lambda x: utility_risk_lover(x, alpha=2.0)
    else:
        raise ValueError(f"Unknown utility: {utility}")

    wealth_grid = np.linspace(0.01, m0 * m_max_factor, n_grid)
    f_grid = np.linspace(0, 1, n_f)  # (n_f,)

    # wealth_win[i,j] = wealth_grid[i] * (f_grid[j] * (1+g) + (1 - f_grid[j]))
    # wealth_lose[i,j] = wealth_grid[i] * (f_grid[j] * (1-g) + (1 - f_grid[j]))
    m2d = wealth_grid[:, None]          # (n_grid, 1)
    f2d = f_grid[None, :]              # (1, n_f)

    wealth_win = m2d * (f2d * (1 + g) + (1 - f2d))     # (n_grid, n_f)
    wealth_lose = m2d * (f2d * (1 - g) + (1 - f2d))    # (n_grid, n_f)

    V = np.zeros((T + 1, n_grid))
    V[0, :] = U(wealth_grid)

    for t in range(1, T + 1):
        V_prev = V[t - 1]

        # Expected value if casino opens: E[V_{t-1} | open]
        EV_win = interp(V_prev, wealth_grid, wealth_win)    # (n_grid, n_f)
        EV_lose = interp(V_prev, wealth_grid, wealth_lose)  # (n_grid, n_f)
        EV_open = p * EV_win + (1 - p) * EV_lose             # (n_grid, n_f)

        # Total EV for each (m, f) pair
        # EV_close = U(m) (no gamble, wealth unchanged)
        EV_close = U(wealth_grid)[:, None]                   # (n_grid, 1)
        EV_total = (1 - S) * EV_close + S * EV_open          # (n_grid, n_f)

        # Take best f for each wealth level
        V[t, :] = np.max(EV_total, axis=1)

    # Find optimal f at initial wealth m0
    EV_close_m0 = U(m0)
    EV_win_m0 = interp(V[T - 1], wealth_grid, wealth_win[np.searchsorted(wealth_grid, m0)])
    # Re-evaluate properly at m0
    w_win = m0 * (f_grid * (1 + g) + (1 - f_grid))
    w_lose = m0 * (f_grid * (1 - g) + (1 - f_grid))
    ev_win = interp(V[T - 1], wealth_grid, w_win)
    ev_lose = interp(V[T - 1], wealth_grid, w_lose)
    ev_open = p * ev_win + (1 - p) * ev_lose
    ev_total = (1 - S) * EV_close_m0 + S * ev_open
    f_opt = f_grid[np.argmax(ev_total)]

    return f_opt, V, wealth_grid


def kelly_criterion(p):
    """Kelly criterion optimal fraction: f* = 2p - 1."""
    return 2 * p - 1


if __name__ == "__main__":
    params = {"p": 0.8, "S": 0.3, "g": 0.5, "m0": 100, "T": 50}

    print("=" * 60)
    print("CASINO GAMBLING MODEL — Dynamic Programming Solver")
    print("=" * 60)
    print(f"\nParameters:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    print()

    f_log, _, _ = solve_dp(utility="log", **params)
    print(f"Optimal f (log utility):      {f_log:.4f}")

    f_power, _, _ = solve_dp(utility="power", **params)
    print(f"Optimal f (power utility):    {f_power:.4f}")

    f_risk, _, _ = solve_dp(utility="risk_lover", **params)
    print(f"Optimal f (risk lover):       {f_risk:.4f}")

    print(f"Kelly criterion f*:           {kelly_criterion(params['p']):.4f}")

    print("\n" + "=" * 60)
    print("Sweep: f* vs p for different S values")
    print("=" * 60)

    for S_val in [0.7, 0.9, 0.99]:
        print(f"\n  S = {S_val}:")
        for p_val in [0.5, 0.6, 0.7, 0.8, 0.9]:
            f_opt, _, _ = solve_dp(p=p_val, S=S_val, g=0.5, m0=100, T=30,
                                   utility="log", n_grid=200, n_f=60)
            print(f"    p={p_val:.1f} -> f*={f_opt:.4f}  (Kelly={kelly_criterion(p_val):.4f})")
