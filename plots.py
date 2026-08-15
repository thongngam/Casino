"""
Casino Gambling Model — Plot Generation Script

Generates all figures documenting the optimal betting behavior under
different risk preferences and casino opening probabilities.

Figures produced:
  Figure 1: f* vs p (S=0.7, risk averse / power utility)
  Figure 2: f* vs p (S=0.9 and S=0.99, risk averse) — convergence to Kelly
  Figure 3: f* vs p (S=0.99, risk averse, m0=100 vs 10000) — wealth robustness
  Figure 4: f* vs p (S=0.7/0.9/0.99, log utility) — log utility panels
  Figure 5: f* vs S (p=0.6, risk averse, m0=100)
  Figure 6: f* vs S (p=0.6, risk averse, m0=10000) — wealth robustness
  Figure 7: f* vs S (p=0.6, log utility)
  Figure 8: f* vs p (S=0.9) — all three risk types compared

Usage:
    python plots.py
"""

import numpy as np
import matplotlib.pyplot as plt
from model import solve_dp, kelly_criterion


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def sweep_f_vs_p(S_val, p_range, utility, **kwargs):
    """
    Sweep over a range of winning probabilities p and compute the
    optimal betting fraction f* for each p.
    
    Parameters
    ----------
    S_val : float
        Casino opening probability (fixed for all p values).
    p_range : array-like
        Winning probabilities to evaluate.
    utility : str
        Utility function name ("log", "power", or "risk_lover").
    **kwargs
        Additional arguments passed to solve_dp (g, m0, T, n_grid, n_f).
    
    Returns
    -------
    list of float
        Optimal f* for each p in p_range.
    """
    return [solve_dp(p=p, S=S_val, utility=utility, **kwargs)[0] for p in p_range]


# =============================================================================
# FIGURE 1: f* vs p, S=0.7, risk averse (power utility)
# =============================================================================

def plot_fig1():
    """
    Figure 1: How optimal f* changes with winning probability p
    when the casino opens with probability S=0.7.
    
    Uses power utility (risk averse, U=2*sqrt(x)).
    Shows that as p increases, f* increases but stays below the Kelly line.
    """
    p_vals = np.linspace(0.5, 1.0, 25)
    f_vals = sweep_f_vs_p(0.7, p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    kelly = [kelly_criterion(p) for p in p_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(p_vals, f_vals, "b-o", label="Optimal f* (S=0.7)", markersize=4)
    ax.plot(p_vals, kelly, "r--", label="Kelly criterion (2p-1)")
    ax.set_xlabel("Gambling winning probability p")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 1: Optimal f* vs p (S=0.7, Power Utility)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, 1.0)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure1.png", dpi=150)
    plt.close()
    print("Saved figure1.png")


# =============================================================================
# FIGURE 2: f* vs p, S=0.9 and S=0.99, risk averse — Kelly convergence
# =============================================================================

def plot_fig2():
    """
    Figure 2: Convergence to Kelly criterion as S -> 1.
    
    Two panels: S=0.9 (left) and S=0.99 (right).
    As the casino stays open more often, the optimal f* approaches the
    Kelly line f* = 2p - 1. At S=0.99 the match is nearly exact.
    """
    p_vals = np.linspace(0.5, 1.0, 25)
    f_09  = sweep_f_vs_p(0.9,  p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    f_099 = sweep_f_vs_p(0.99, p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    kelly = [kelly_criterion(p) for p in p_vals]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, f_data, s in zip(axes, [f_09, f_099], [0.9, 0.99]):
        ax.plot(p_vals, f_data, "b-o", label=f"Optimal f* (S={s})", markersize=4)
        ax.plot(p_vals, kelly, "r--", label="Kelly (2p-1)")
        ax.set_xlabel("p")
        ax.set_ylabel("f*")
        ax.set_title(f"S = {s}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.5, 1.0)
        ax.set_ylim(0, 1)

    fig.suptitle("Figure 2: f* vs p — Convergence to Kelly as S -> 1 (Power Utility)", fontsize=13)
    plt.tight_layout()
    plt.savefig("figure2.png", dpi=150)
    plt.close()
    print("Saved figure2.png")


# =============================================================================
# FIGURE 3: f* vs p, S=0.99, different initial wealth — robustness check
# =============================================================================

def plot_fig3():
    """
    Figure 3: Does initial wealth matter?
    
    Compares f* for m0=100 vs m0=10,000 with S=0.99, power utility.
    The curves overlap exactly — the optimal fraction is independent
    of how much money you start with (a key property of CRRA utilities).
    """
    p_vals = np.linspace(0.5, 1.0, 25)
    f_100   = sweep_f_vs_p(0.99, p_vals, "power", g=0.5, m0=100,   T=30, n_grid=200, n_f=60)
    f_10000 = sweep_f_vs_p(0.99, p_vals, "power", g=0.5, m0=10000, T=30, n_grid=200, n_f=60)
    kelly = [kelly_criterion(p) for p in p_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(p_vals, f_100, "b-o", label="m0=100", markersize=4)
    ax.plot(p_vals, f_10000, "g-s", label="m0=10000", markersize=4)
    ax.plot(p_vals, kelly, "r--", label="Kelly (2p-1)")
    ax.set_xlabel("Gambling winning probability p")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 3: Robustness to Initial Wealth (S=0.99, Power Utility)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, 1.0)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure3.png", dpi=150)
    plt.close()
    print("Saved figure3.png")


# =============================================================================
# FIGURE 4: f* vs p, log utility, S=0.7/0.9/0.99
# =============================================================================

def plot_fig4():
    """
    Figure 4: Same as Figures 1-2 but using log utility (risk neutral).
    
    Three panels for S=0.7, 0.9, 0.99. The log utility converges to
    Kelly more smoothly than the power utility case.
    """
    p_vals = np.linspace(0.5, 1.0, 25)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, S_val in zip(axes, [0.7, 0.9, 0.99]):
        f_vals = sweep_f_vs_p(S_val, p_vals, "log", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
        kelly = [kelly_criterion(p) for p in p_vals]
        ax.plot(p_vals, f_vals, "b-o", label=f"Optimal f* (S={S_val})", markersize=4)
        ax.plot(p_vals, kelly, "r--", label="Kelly (2p-1)")
        ax.set_xlabel("p")
        ax.set_ylabel("f*")
        ax.set_title(f"S = {S_val}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.5, 1.0)
        ax.set_ylim(0, 1)

    fig.suptitle("Figure 4: f* vs p — Log Utility (Risk Neutral)", fontsize=13)
    plt.tight_layout()
    plt.savefig("figure4.png", dpi=150)
    plt.close()
    print("Saved figure4.png")


# =============================================================================
# FIGURE 5: f* vs S, p=0.6, power utility, m0=100
# =============================================================================

def plot_fig5():
    """
    Figure 5: How optimal f* changes with casino opening probability S.
    
    Fix p=0.6 (small edge), power utility (risk averse).
    As S -> 0: f* -> 1 (bet everything, "now or never").
    As S -> 1: f* -> Kelly = 0.2 (standard result).
    The relationship is convex and decreasing.
    """
    S_vals = np.linspace(0.05, 0.99, 20)
    f_vals = [solve_dp(p=0.6, S=S, g=0.5, m0=100, T=30,
                       utility="power", n_grid=200, n_f=60)[0] for S in S_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_vals, f_vals, "b-o", markersize=4)
    ax.axhline(y=kelly_criterion(0.6), color="r", linestyle="--", label="Kelly (0.2)")
    ax.set_xlabel("Casino opening probability S")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 5: f* vs S (p=0.6, Power Utility, m0=100)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure5.png", dpi=150)
    plt.close()
    print("Saved figure5.png")


# =============================================================================
# FIGURE 6: f* vs S, p=0.6, power utility, m0=10000
# =============================================================================

def plot_fig6():
    """
    Figure 6: Same as Figure 5 but with m0=10,000.
    
    The curve is identical to Figure 5, confirming that the optimal
    betting fraction does not depend on initial wealth.
    """
    S_vals = np.linspace(0.05, 0.99, 20)
    f_vals = [solve_dp(p=0.6, S=S, g=0.5, m0=10000, T=30,
                       utility="power", n_grid=200, n_f=60)[0] for S in S_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_vals, f_vals, "b-o", markersize=4)
    ax.axhline(y=kelly_criterion(0.6), color="r", linestyle="--", label="Kelly (0.2)")
    ax.set_xlabel("Casino opening probability S")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 6: f* vs S (p=0.6, Power Utility, m0=10000)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure6.png", dpi=150)
    plt.close()
    print("Saved figure6.png")


# =============================================================================
# FIGURE 7: f* vs S, p=0.6, log utility
# =============================================================================

def plot_fig7():
    """
    Figure 7: Same as Figure 5 but with log utility (risk neutral).
    
    The relationship is smoother than the power utility case.
    The log utility player drops their bet size more gradually as
    the casino becomes less reliable.
    """
    S_vals = np.linspace(0.05, 0.99, 20)
    f_vals = [solve_dp(p=0.6, S=S, g=0.5, m0=100, T=30,
                       utility="log", n_grid=200, n_f=60)[0] for S in S_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_vals, f_vals, "b-o", markersize=4)
    ax.axhline(y=kelly_criterion(0.6), color="r", linestyle="--", label="Kelly (0.2)")
    ax.set_xlabel("Casino opening probability S")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 7: f* vs S (p=0.6, Log Utility)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure7.png", dpi=150)
    plt.close()
    print("Saved figure7.png")


# =============================================================================
# FIGURE 8: All three risk types compared, S=0.9
# =============================================================================

def plot_fig8():
    """
    Figure 8: Direct comparison of all three risk preferences.
    
    Fix S=0.9, sweep p from 0.5 to 1.0.
    
    - Risk lover (U=x^2/2): bets MORE than Kelly, often everything.
    - Risk neutral (U=log x): bets close to Kelly.
    - Risk averse (U=2*sqrt(x)): bets LESS than Kelly.
    
    This figure shows how the shape of the utility function (convex vs
    concave) directly determines whether the player over- or under-bets
    relative to the Kelly benchmark.
    """
    p_vals = np.linspace(0.5, 1.0, 25)
    f_risk_lover = sweep_f_vs_p(0.9, p_vals, "risk_lover", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    f_risk_averse = sweep_f_vs_p(0.9, p_vals, "power",     g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    f_log         = sweep_f_vs_p(0.9, p_vals, "log",        g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    kelly = [kelly_criterion(p) for p in p_vals]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(p_vals, f_risk_lover, "m-^", label="Risk Lover (U=x^2/2)", markersize=5)
    ax.plot(p_vals, f_log,        "g-s", label="Risk Neutral (U=log x)", markersize=5)
    ax.plot(p_vals, f_risk_averse,"b-o", label="Risk Averse (U=2*sqrt(x))", markersize=5)
    ax.plot(p_vals, kelly,        "r--", label="Kelly criterion (2p-1)", linewidth=2)
    ax.set_xlabel("Gambling winning probability p")
    ax.set_ylabel("Optimal betting fraction f*")
    ax.set_title("Figure 8: Risk Preference Comparison (S=0.9)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, 1.0)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figure8.png", dpi=150)
    plt.close()
    print("Saved figure8.png")


# =============================================================================
# MAIN: Generate all figures
# =============================================================================

if __name__ == "__main__":
    print("Generating all figures...\n")
    plot_fig1()
    plot_fig2()
    plot_fig3()
    plot_fig4()
    plot_fig5()
    plot_fig6()
    plot_fig7()
    plot_fig8()
    print("\nAll figures generated!")
