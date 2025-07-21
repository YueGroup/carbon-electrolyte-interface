import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import defaultdict

# === SETTINGS ===
species = "water"
nnacl = 18
nbin = 200
input_base = f"/Users/nhinguyen/Desktop/Pic/Figures/density_csv_{nbin}bin"
output_prefix = f"fig3_{species}_{nnacl}nacl_{nbin}bins"
font_size = 17

functional_group_map = {
    "UNFUNC": "Unfunctionalized",
    "CH3": "-CH₃",
    "COOH": "-COOH",
    "OH": "-OH",
    "CO": "=O"
}
coverage_label_map = {
    0: "Unfunctionalized",
    8: "Low (2.2%)",
    16: "Medium (4.4%)",
    24: "High (6.6%)"
}
plot_groups = ["COOH", "OH", "CO", "CH3"]
coverage_colors = {
    "Unfunctionalized": "#000000",
    "Low (2.2%)": "#7FB3D5",
    "Medium (4.4%)": "#F4D03F",
    "High (6.6%)": "#C0392B"
}

def format_one_sigfig(x, _):
    if x == 0:
        return "0"
    abs_x = abs(x)
    if abs_x < 1:
        return f"{x:.1f}".rstrip("0").rstrip(".")
    elif abs_x < 10:
        return f"{x:.0f}"
    elif abs_x < 100:
        return f"{round(x, -1):.0f}"
    elif abs_x < 1000:
        return f"{round(x, -2):.0f}"
    else:
        return f"{x:.0e}"

def parse_filename(fname):
    parts = fname.split("_")
    try:
        info = parts[2]
        for fg in functional_group_map:
            if fg in info:
                nfunc = int(info.replace(fg, ""))
                return nfunc, fg
    except:
        return None, None
    return None, None

def add_panel_label(ax, label):
    ax.text(0.04, 0.96, label, transform=ax.transAxes,
            fontsize=font_size - 2, fontweight="bold", ha="left", va="top")

# === LOAD DATA ===
group_profiles = {fg: defaultdict(list) for fg in plot_groups}
unfunc_curves = []

for folder in os.listdir(input_base):
    path = os.path.join(input_base, folder)
    if not os.path.isdir(path):
        continue
    for fname in os.listdir(path):
        if not fname.startswith(f"density_{species}_") or f"{nnacl}nacl" not in fname:
            continue
        nfunc, fg = parse_filename(fname)
        if fg is None or nfunc is None:
            continue
        label = coverage_label_map.get(nfunc, f"{nfunc} sites")
        df = pd.read_csv(os.path.join(path, fname))
        z = (df["z_wall_nm"] * 10).round(1)  # Convert nm → Ångström
        d = df["density (g/cm^3)"]
        if fg == "UNFUNC":
            unfunc_curves.append((z, d))
        elif fg in plot_groups:
            group_profiles[fg][label].append((z, d))

# === PLOT COMBINED 4×1 ===
plt.rcParams["font.family"] = "Helvetica"
fig, axes = plt.subplots(1, 4, figsize=(12, 3), sharey=True)

for idx, fg in enumerate(plot_groups):
    ax = axes[idx]
    group_label = functional_group_map[fg]

    # Plot unfunctionalized
    if unfunc_curves:
        df = pd.concat([pd.DataFrame({"z": z, "density": dens}) for z, dens in unfunc_curves], axis=0)
        df = df.groupby("z").agg(["mean", "std"])
        z = df.index.values
        mean = df[("density", "mean")].values
        std = df[("density", "std")].values
        ax.plot(z, mean, color=coverage_colors["Unfunctionalized"], linewidth=2, label="Unfunctionalized")
        ax.fill_between(z, mean - std, mean + std, alpha=0.3, color=coverage_colors["Unfunctionalized"])

    # Plot each coverage
    for cov_level in ["Low (2.2%)", "Medium (4.4%)", "High (6.6%)"]:
        curves = group_profiles[fg][cov_level]
        if not curves:
            continue
        df = pd.concat([pd.DataFrame({"z": z, "density": dens}) for z, dens in curves], axis=0)
        df = df.groupby("z").agg(["mean", "std"])
        z = df.index.values
        mean = df[("density", "mean")].values
        std = df[("density", "std")].values
        ax.plot(z, mean, label=cov_level, color=coverage_colors[cov_level], linewidth=2)
        ax.fill_between(z, mean - std, mean + std, alpha=0.3, color=coverage_colors[cov_level])

    ax.set_title(group_label, fontsize=font_size)
    ax.set_xlabel("z (Å)", fontsize=font_size)  # ← Updated label
    ax.tick_params(direction="in", length=4, width=1, labelsize=font_size - 2.5)
    ax.xaxis.set_major_formatter(FuncFormatter(format_one_sigfig))
    ax.yaxis.set_major_formatter(FuncFormatter(format_one_sigfig))
    for spine in ax.spines.values():
        spine.set_linewidth(1)

    # Add panel label
    add_panel_label(ax, f"({chr(ord('a') + idx)})")

axes[0].set_ylabel("Density (g/cm³)", fontsize=font_size)
axes[-1].legend(frameon=False, fontsize=font_size - 6)

fig.tight_layout()
plt.savefig(f"{output_prefix}.pdf", dpi=300, bbox_inches="tight")
print(f"[✓] Figure saved to {output_prefix}.pdf with x-axis in Ångström.")
