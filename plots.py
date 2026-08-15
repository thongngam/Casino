"""
Generate all figures for the Casino Gambling Model.

Produces:
  Figure 1: f* vs p (S=0.7, power utility)
  Figure 2: f* vs p (S=0.9 and S=0.99, power utility)
  Figure 3: f* vs p with different initial wealth (S=0.99, power utility)
  Figure 4: f* vs p under log utility for S=0.7, 0.9, 0.99
  Figure 5: f* vs S (p=0.6, power utility, m0=100)
  Figure 6: f* vs S (p=0.6, power utility, m0=10000)
  Figure 7: f* vs S (p=0.6, log utility)
  Figure 8: f* vs p — comparison of all utility types (risk lover, risk neutral, risk averse)
"""

import numpy as np
import matplotlib.pyplot as plt
from model import solve_dp, kelly_criterion


def sweep_f_vs_p(S_val, p_range, utility, **kwargs):
    """Helper: compute optimal f for a range of p values."""
    return [solve_dp(p=p, S=S_val, utility=utility, **kwargs)[0] for p in p_range]


def plot_fig1():
    """Figure 1: f* vs p, S=0.7, power utility."""
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


def plot_fig2():
    """Figure 2: f* vs p, S=0.9 and S=0.99, power utility."""
    p_vals = np.linspace(0.5, 1.0, 25)
    f_09 = sweep_f_vs_p(0.9, p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
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


def plot_fig3():
    """Figure 3: f* vs p, S=0.99, power utility, different initial wealth."""
    p_vals = np.linspace(0.5, 1.0, 25)
    f_100 = sweep_f_vs_p(0.99, p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
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


def plot_fig4():
    """Figure 4: f* vs p under log utility for S=0.7, 0.9, 0.99."""
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

    fig.suptitle("Figure 4: f* vs p — Log Utility", fontsize=13)
    plt.tight_layout()
    plt.savefig("figure4.png", dpi=150)
    plt.close()
    print("Saved figure4.png")


def plot_fig5():
    """Figure 5: f* vs S, p=0.6, power utility, m0=100."""
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


def plot_fig6():
    """Figure 6: f* vs S, p=0.6, power utility, m0=10000."""
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


def plot_fig7():
    """Figure 7: f* vs S, p=0.6, log utility."""
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


def plot_fig8():
    """Figure 8: f* vs p — risk lover vs risk averse vs Kelly, S=0.9."""
    p_vals = np.linspace(0.5, 1.0, 25)
    f_risk_lover = sweep_f_vs_p(0.9, p_vals, "risk_lover", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    f_risk_averse = sweep_f_vs_p(0.9, p_vals, "power", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    f_log = sweep_f_vs_p(0.9, p_vals, "log", g=0.5, m0=100, T=30, n_grid=200, n_f=60)
    kelly = [kelly_criterion(p) for p in p_vals]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(p_vals, f_risk_lover, "m-^", label="Risk Lover (U=x^2)", markersize=5)
    ax.plot(p_vals, f_log, "g-s", label="Risk Neutral (U=log x)", markersize=5)
    ax.plot(p_vals, f_risk_averse, "b-o", label="Risk Averse (U=sqrt(x))", markersize=5)
    ax.plot(p_vals, kelly, "r--", label="Kelly criterion (2p-1)", linewidth=2)
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
