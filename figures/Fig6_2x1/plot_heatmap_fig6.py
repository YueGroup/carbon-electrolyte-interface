import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter

# === SETTINGS ===
nnacl = 27
input_dir = "/Users/nhinguyen/Desktop/Pic/Figures/diffusion_csv/8000ps"
species = "Water"
surface_file = os.path.join(input_dir, "diff_water.csv")
bulk_file = os.path.join(input_dir, "diff_waterbulk.csv")
global_font_size = 15

# === MAPPINGS ===
functional_group_map = {
    "CH3": "-CH₃",
    "COOH": "-COOH",
    "OH": "-OH",
    "CO": "=O"
}
sorted_fg_order = ["COOH", "OH", "CO", "CH3"]
nfunc_to_coverage = {
    8: "Low (2.2%)",
    16: "Medium (4.4%)",
    24: "High (6.6%)"
}
coverage_order = [8, 16, 24]

# === GLOBAL FONT SIZE CONTROL ===
label_fontsize = global_font_size
tick_fontsize = global_font_size - 1
title_fontsize = global_font_size
panel_label_fontsize = global_font_size
colorbar_tick_fontsize = global_font_size - 1

# === Load and Pivot ===
def load_and_pivot(file_path):
    df = pd.read_csv(file_path)
    df = df[df["functional_group"].isin(functional_group_map.keys())]
    df = df[df["nfunc"].isin(nfunc_to_coverage.keys())]
    df = df[df["nnacl"] == nnacl]
    df = df.replace("", np.nan)
    df[["D_trial1", "D_trial2", "D_trial3"]] = df[["D_trial1", "D_trial2", "D_trial3"]].apply(pd.to_numeric, errors='coerce')
    df["D_avg"] = df[["D_trial1", "D_trial2", "D_trial3"]].mean(axis=1)
    df = df.dropna(subset=["D_avg"])
    df = df[df["D_avg"] > 0]

    pivot = pd.DataFrame(index=[nfunc_to_coverage[n] for n in coverage_order],
                         columns=[functional_group_map[fg] for fg in sorted_fg_order])

    for _, row in df.iterrows():
        x = functional_group_map[row["functional_group"]]
        y = nfunc_to_coverage[row["nfunc"]]
        pivot.loc[y, x] = row["D_avg"]

    return pivot.astype(float)

# === Custom formatter to always show two sig figs with trailing zeros ===
def format_two_sigfigs_strict(x, _):
    if x == 0:
        return "0.00"
    elif x < 1:
        return f"{x:.2f}"
    elif x < 10:
        return f"{x:.2g}" if x % 1 else f"{x:.1f}"
    elif x < 100:
        return f"{x:.2g}" if x % 1 else f"{x:.1f}"
    else:
        return f"{x:.1e}"

# === Load Data ===
surface_data = load_and_pivot(surface_file)
bulk_data = load_and_pivot(bulk_file)

# === Plot ===
plt.style.use("default")
plt.rcParams["font.family"] = "Helvetica"

fig, (ax1, ax2) = plt.subplots(
    nrows=2, ncols=1, figsize=(5, 5), sharex=True, sharey=True,
    gridspec_kw={"height_ratios": [1, 1]}, constrained_layout=True
)

# Color limits
vmin = np.nanmin([surface_data.min().min(), bulk_data.min().min()])
vmax = np.nanmax([surface_data.max().max(), bulk_data.max().max()])
cmap = matplotlib.colormaps["RdYlBu"]

# Plot each heatmap
for ax, data, title, label in zip([ax1, ax2], [surface_data, bulk_data], ["Interface", "Bulk"], ["(a)", "(b)"]):
    im = ax.imshow(data.values, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto', interpolation='nearest')

    ax.set_yticks(range(len(coverage_order)))
    ax.set_yticklabels([nfunc_to_coverage[n] for n in coverage_order], fontsize=tick_fontsize)

    ax.set_xticks(range(len(sorted_fg_order)))
    ax.set_xticklabels([functional_group_map[fg] for fg in sorted_fg_order], fontsize=tick_fontsize)

    ax.set_title(title, fontsize=title_fontsize, pad=4)
    ax.tick_params(length=3, width=1, direction="in", labelsize=tick_fontsize)
    for spine in ax.spines.values():
        spine.set_linewidth(1)

    # Add panel label to top-left
    ax.text(-0.15, 1.03, label, transform=ax.transAxes, fontsize=panel_label_fontsize, fontweight='bold')

# Shared axis labels (with offsets)
fig.text(0.51, -0.05, "Functional Groups", ha='center', fontsize=label_fontsize)
fig.text(-0.07, 0.5, "Surface Coverage (%)", va='center', rotation='vertical', fontsize=label_fontsize)

# Shared colorbar
cbar = fig.colorbar(im, ax=[ax1, ax2], orientation='vertical', pad=0.15, aspect=30, shrink=0.85)
cbar.ax.yaxis.set_major_formatter(FuncFormatter(format_two_sigfigs_strict))
cbar.ax.tick_params(labelsize=colorbar_tick_fontsize)
cbar.set_label(
    r"$D_{\parallel}$ (×$10^{-5}$ cm$^2$/s)",
    fontsize=label_fontsize,
    rotation=90+180,
    labelpad=25
)

# Save
fig.savefig(f"fig6_heatmap_water_surface_vs_bulk_{nnacl}nacl.pdf", format="pdf", dpi=300, bbox_inches="tight")
print(f"[✓] Saved: fig6_heatmap_water_surface_vs_bulk_{nnacl}nacl.pdf")
