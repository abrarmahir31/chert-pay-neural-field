#!/usr/bin/env python
"""All manuscript figures, drawn ONLY from files in results/ (no model runs, no raw data).

Usage: python scripts/make_figures.py      -> figures/fig*.pdf (vector) and .png (preview)
Source file of every panel: docs/traceability.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
R, F = ROOT / "results", ROOT / "figures"
# Okabe-Ito colour-blind-safe palette (blue, vermillion, bluish green), the set most often
# recommended for journal figures; checked for colour-vision-deficiency separation.
# Marker shape repeats the colour encoding, so figures also read in greyscale.
BLUE, ORANGE, AQUA = "#0072B2", "#D55E00", "#009E73"
INK, MUTED, GRID = "#000000", "#4d4d4d", "#e0e0e0"
SINGLE_COL, DOUBLE_COL = 3.54, 7.48   # Elsevier column widths: 90 mm and 190 mm
plt.rcParams.update({
    # Arial / Helvetica as asked for by Elsevier artwork guidelines; Liberation Sans is the
    # metric-compatible fallback on Linux, DejaVu Sans the last resort.
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom", "mathtext.rm": "sans", "font.size": 8,
    "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
    "axes.linewidth": 0.6, "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "legend.frameon": False, "pdf.fonttype": 42, "ps.fonttype": 42,
    "figure.facecolor": "white", "savefig.bbox": "tight",
    "figure.dpi": 150, "savefig.dpi": 600, "axes.titlelocation": "left",
})
DOT = dict(s=34, edgecolor="white", linewidth=0.8, zorder=3)


def save(fig, name):
    F.mkdir(exist_ok=True)
    fig.savefig(F / f"{name}.pdf")
    fig.savefig(F / f"{name}.png")
    plt.close(fig)


def strip(ax, y, vals, color, marker="o"):
    vals = np.asarray(vals, float)
    off = np.linspace(-0.12, 0.12, len(vals)) if len(vals) > 1 else [0.0]
    ax.scatter(vals, y + np.asarray(off), color=color, marker=marker, **DOT)


def fig1_map():
    w = pd.read_csv(R / "splits/frozen_wells_v1.csv")
    x, y = w.x_km - w.x_km.min(), w.y_km - w.y_km.min()
    fig, ax = plt.subplots(figsize=(SINGLE_COL + 0.6, 4.0))
    for lab, name, c, mk, s in ((-1, "unlabelled (n = {})", "#9a9a9a", "o", 9),
                                (1, "Mississippian producer (n = {})", BLUE, "o", 13),
                                (0, "dry hole (n = {})", ORANGE, "D", 22)):
        m = w.label == lab
        ax.scatter(x[m], y[m], s=s, c=c, marker=mk, edgecolor="white", linewidth=0.4,
                   label=name.format(int(m.sum())), zorder=2 + (lab == 0))
    b = 8.0
    for v in np.arange(0, x.max() + b, b):
        ax.axvline(v, color=GRID, lw=0.6, zorder=1)
    for v in np.arange(0, y.max() + b, b):
        ax.axhline(v, color=GRID, lw=0.6, zorder=1)
    ax.grid(False)
    ax.set_aspect("equal")
    ax.set_xlabel("Easting (km, local)")
    ax.set_ylabel("Northing (km, local)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1, handletextpad=0.2)
    save(fig, "fig1_wells_map")


def fig2_identifiability():
    v1 = pd.read_csv(R / "identifiability/runs.csv")
    v2 = pd.read_csv(R / "identifiability_v2/runs.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
    rows = [("m  (same-family truth, v1)", v1[v1.experiment == "base"].m_r, BLUE, "o"),
            ("m  (same-family truth, v2 settings)", v2[v2.experiment == "v2_same_family"].m_r, BLUE, "o"),
            ("m  (different-family truth, v2)", v2[v2.experiment == "v2_base"].m_r, ORANGE, "D"),
            ("n  (same-family truth, v1)", v1[v1.experiment == "base"].n_r, ORANGE, "D"),
            ("micro-porosity fraction (v1)", v1[v1.experiment == "base"].f_micro_r, ORANGE, "D")]
    for i, (_, vals, c, mk) in enumerate(rows):
        strip(a, len(rows) - 1 - i, vals, c, mk)
    a.axvline(0.70, color=INK, lw=0.8)
    a.text(0.69, -0.72, "pre-registered threshold 0.70", fontsize=7, color=MUTED, ha="right", va="center")
    a.set_yticks(range(len(rows)))
    a.set_yticklabels([r[0] for r in rows][::-1])
    a.set_xlim(-0.05, 1.0)
    a.set_ylim(-0.95, len(rows) - 0.5)
    a.set_xlabel("Correlation of recovered and true parameter (one dot per seed)")
    a.set_title("(a) Parameter recovery on synthetic benchmarks")
    a.grid(axis="y", visible=False)
    s1 = json.load(open(R / "identifiability/summary.json"))["decision_rule_D20"]["null_control_n"]
    s2 = json.load(open(R / "identifiability_v2/summary.json"))["decision_rule_D24a"]["m_null_control"]
    n_sd = v1[v1.experiment == "null_n"].n_sd_est
    strip(b, 1, n_sd, ORANGE, "D")
    strip(b, 0, s2["sd_m_hat"], ORANGE, "D")
    for yy, lim in ((1, s1["limit"]), (0, s2["limit"])):
        b.plot([lim, lim], [yy - 0.3, yy + 0.3], color=INK, lw=0.8)
    for yy, lim in ((1, s1["limit"]), (0, s2["limit"])):
        b.text(lim + 0.004, yy + 0.36, "pre-registered limit", fontsize=7, color=MUTED, ha="left")
    b.set_yticks([0, 1])
    b.set_yticklabels(["m  (true m constant)", "n  (true n constant)"])
    b.set_ylim(-0.6, 1.7)
    b.set_xlim(0, 0.3)
    b.set_xlabel("Spread (SD) of the recovered parameter")
    b.set_title("(b) Null controls: structure invented from nothing")
    b.grid(axis="y", visible=False)
    h = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="parameter passes the pre-registered rule"),
         plt.Line2D([], [], marker="D", ls="", color=ORANGE, label="parameter fails the rule")]
    fig.legend(handles=h, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.07))
    fig.tight_layout()
    save(fig, "fig2_identifiability")


def fig3_synthetic_pay():
    v3 = pd.read_csv(R / "pay_indicator_benchmark/runs.csv")
    rows = [("Archie inversion, spatial field", "v3_archie_field", BLUE, "o"),
            ("Archie inversion, well by well", "v3_archie_perwell", ORANGE, "D"),
            ("Archie inversion, one global m", "v3_archie_const", ORANGE, "D"),
            ("Dual-porosity inversion, spatial field", "v3_dual_field", BLUE, "o"),
            ("Dual-porosity inversion, well by well", "v3_dual_perwell", ORANGE, "D"),
            ("Fixed-parameter Archie (no inversion)", None, ORANGE, "s")]
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.9), sharey=True)
    for ax, col, fcol, ttl in ((axs[0], "auc_pay_vs_wet", "fixed_archie_auc_vs_wet",
                                "(a) Pay wells vs fully wet wells"),
                               (axs[1], "auc_pay_vs_dry", "fixed_archie_auc_vs_dry",
                                "(b) Pay wells vs all dry wells (incl. marginal)")):
        for i, (_, ex, c, mk) in enumerate(rows):
            vals = v3[v3.experiment == ex][col] if ex else v3[v3.experiment == "v3_archie_field"][fcol]
            strip(ax, len(rows) - 1 - i, vals, c, mk)
        ax.set_xlim(0.72, 1.0)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.set_title(ttl)
        ax.set_xlabel("AUC, synthetic benchmark v3 (one dot per seed)", fontsize=7.5)
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks(range(len(rows)))
    axs[0].set_yticklabels([r[0] for r in rows][::-1])
    h = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="spatial neural field"),
         plt.Line2D([], [], marker="D", ls="", color=ORANGE, label="same inversion without the field"),
         plt.Line2D([], [], marker="s", ls="", color=ORANGE, label="no inversion")]
    fig.legend(handles=h, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.07))
    fig.tight_layout()
    save(fig, "fig3_synthetic_pay_indicator")


NAMES = {"supervised_gbm": ("Supervised gradient boosting", AQUA, "s"),
         "supervised_mlp": ("Supervised MLP", AQUA, "s"),
         "inversion_archie_per_well": ("Archie inversion, well by well", ORANGE, "D"),
         "fixed_archie": ("Fixed-parameter Archie", ORANGE, "D"),
         "fixed_simandoux": ("Fixed-parameter Simandoux", ORANGE, "D"),
         "inversion_dual_per_well": ("Dual-porosity inversion, well by well", ORANGE, "D"),
         "archie_field": ("Archie neural field (primary entry)", BLUE, "o"),
         "inversion_archie_constant": ("Archie inversion, one global m", ORANGE, "D"),
         "dual_field": ("Dual-porosity neural field (second entry)", BLUE, "o")}
LEG = [plt.Line2D([], [], marker="o", ls="", color=BLUE, label="neural-field entries"),
       plt.Line2D([], [], marker="D", ls="", color=ORANGE, label="label-free baselines"),
       plt.Line2D([], [], marker="s", ls="", color=AQUA, label="supervised baselines (use labels)")]


def fig4_real_auc():
    e = json.load(open(R / "real/evaluation.json"))
    order = sorted(e["auc"], key=lambda m: e["auc"][m]["auc"])
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    for i, m in enumerate(order):
        v, (_, c, mk) = e["auc"][m], NAMES[m]
        ax.plot(v["ci95"], [i, i], color=c, lw=2, solid_capstyle="round", zorder=2)
        ax.scatter([v["auc"]], [i], color=c, marker=mk, **DOT)
        ax.text(v["ci95"][1] + 0.008, i, f"{v['auc']:.3f}", va="center", fontsize=7.5, color=INK)
    ax.axvline(0.5, color=INK, lw=0.8)
    ax.text(0.503, -0.75, "chance", fontsize=7, color=MUTED)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NAMES[m][0] for m in order])
    ax.set_xlim(0.45, 0.9)
    ax.set_ylim(-1, len(order) - 0.5)
    ax.set_xlabel("AUC, producers vs dry holes on held-out spatial blocks (95 % bootstrap interval)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=LEG, loc="lower center", bbox_to_anchor=(0.32, -0.36), ncol=3,
              handletextpad=0.2, columnspacing=1.0)
    save(fig, "fig4_real_data_auc")


def fig5_exploratory():
    d = json.load(open(R / "real/diagnostics_exploratory.json"))
    e = json.load(open(R / "real/evaluation.json"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.7), gridspec_kw={"width_ratios": [1.15, 1]})
    key = ["supervised_gbm", "inversion_archie_per_well", "fixed_archie", "archie_field"]
    for i, m in enumerate(key[::-1]):
        name, c, mk = NAMES[m]
        vals = list(d["auc_per_fold"][m].values())
        a.plot([min(vals), max(vals)], [i, i], color=c, lw=1, alpha=0.35, zorder=1)
        a.scatter(vals, [i] * len(vals), color=c, marker=mk, **DOT)
    a.axvline(0.5, color=INK, lw=0.8)
    a.set_yticks(range(len(key)))
    a.set_yticklabels([NAMES[m][0].replace(" (primary entry)", "") for m in key[::-1]])
    a.set_xlim(0.35, 1.0)
    a.set_ylim(-0.6, len(key) - 0.4)
    a.set_xlabel("AUC within each of the 5 held-out blocks")
    a.set_title("(a) Exploratory: performance varies by area")
    a.grid(axis="y", visible=False)
    f = d["auc_single_descriptive_feature"]
    rows = [("Mean density-neutron porosity", f["mean_dn_porosity"], MUTED, "^"),
            ("Low mean deep resistivity", f["low_resistivity (-mean log10 Rt)"], MUTED, "^"),
            ("Low mean gamma ray", f["low_gamma_ray"], MUTED, "^"),
            ("Archie inversion, well by well", e["auc"]["inversion_archie_per_well"]["auc"], ORANGE, "D"),
            ("Archie neural field", e["auc"]["archie_field"]["auc"], BLUE, "o")]
    for i, (_, v, c, mk) in enumerate(rows[::-1]):
        b.plot([0.5, v], [i, i], color=c, lw=2, solid_capstyle="butt", zorder=2)
        b.scatter([v], [i], color=c, marker=mk, **DOT)
        b.text(v + 0.012, i, f"{v:.3f}", va="center", fontsize=7.5)
    b.axvline(0.5, color=INK, lw=0.8)
    b.set_yticks(range(len(rows)))
    b.set_yticklabels([r[0] for r in rows][::-1])
    b.set_xlim(0.45, 0.85)
    b.set_ylim(-0.6, len(rows) - 0.4)
    b.set_xlabel("AUC, producers vs dry holes (all labelled wells)")
    b.set_title("(b) Exploratory: single raw log statistics")
    b.grid(axis="y", visible=False)
    fig.text(0.5, -0.03, "Post hoc, hypothesis-generating only: not part of the pre-registered test.",
             ha="center", fontsize=7.5, color=MUTED)
    fig.tight_layout()
    save(fig, "fig5_exploratory")


if __name__ == "__main__":
    for f in (fig1_map, fig2_identifiability, fig3_synthetic_pay, fig4_real_auc, fig5_exploratory):
        f()
    print("figures written to", F)
