import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.cm as cm

# === SETTINGS ===
species = "water"
fixed_nnacl = 36
input_dir = "/Users/nhinguyen/Desktop/Pic/Figures/diffusion_csv/8000ps"
font_size = 17  # Global font size scaling

# === FILES ===
input_surface = os.path.join(input_dir, f"diff_{species}.csv")
input_bulk = os.path.join(input_dir, f"diff_{species}bulk.csv")
output_pdf = f"fig5_{species}_diffusion_{fixed_nnacl}nacl.pdf"

# === MAPPINGS ===
functional_group_map = {
    "COOH": "-COOH",
    "OH": "-OH",
    "CO": "=O",
    "CH3": "-CH₃"
}
group_order = ["-COOH", "-OH", "=O", "-CH₃"]
nfunc_to_x = {8: 2.2, 16: 4.4, 24: 6.6}
x_ticks = [2.2, 4.4, 6.6]

# === COLORS: darker muted blue tones ===
# colors = {
#     "-COOH": "#a1dab4",
#     "-OH":   "#41b6c4",
#     "=O":    "#2c7fb8",
#     "-CH₃":  "#253494"
# }
# colors = {
#     "-COOH": "#238b45",  # darker green (vs. old pale green)
#     "-OH":   "#1d91c0",  # moderate blue
#     "=O":    "#225ea8",  # rich blue
#     "-CH₃":  "#081d58"   # very dark navy
# }
colors = {
    "-COOH": "#238b45",  # rich green
    "-OH":   "#1d91c0",  # medium blue
    "=O":    "#225ea8",  # strong blue
    "-CH₃":  "#54278f"   # dark purple → visibly different from blue
}

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

# === DATA LOADING ===
def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df = df[df["functional_group"].isin(functional_group_map.keys())]
    df = df[df["nnacl"] == fixed_nnacl]
    df = df[df["nfunc"].isin(nfunc_to_x.keys())]
    df = df.replace("", np.nan)
    df[["D_trial1", "D_trial2", "D_trial3"]] = df[["D_trial1", "D_trial2", "D_trial3"]].apply(pd.to_numeric, errors='coerce')
    df["D_avg"] = df[["D_trial1", "D_trial2", "D_trial3"]].mean(axis=1)
    df["D_std"] = df[["D_trial1", "D_trial2", "D_trial3"]].std(axis=1)
    df = df.dropna(subset=["D_avg"])
    df = df[df["D_avg"] > 0]
    df["functional_group_label"] = df["functional_group"].map(functional_group_map)
    df["coverage"] = df["nfunc"].map(nfunc_to_x)
    df = df.sort_values(by=["functional_group_label", "coverage"])
    return df

# === LOAD DATA ===
df_surf = load_and_process(input_surface)
df_bulk = load_and_process(input_bulk)

# === PLOT ===
plt.style.use("default")
plt.rcParams["font.family"] = "Helvetica"
fig, axes = plt.subplots(1, 2, figsize=(6.8, 3), sharey=True)

# === Plotting Loop ===
for idx, (ax, df, panel_label) in enumerate(zip(axes, [df_surf, df_bulk], ["(a)", "(b)"])):
    for group in group_order:
        group_df = df[df["functional_group_label"] == group]
        x_vals = group_df["coverage"]
        y_vals = group_df["D_avg"]
        y_errs = group_df["D_std"]
        ax.errorbar(
            x_vals, y_vals, yerr=y_errs,
            label=group,
            fmt='o-', markersize=5, capsize=4,
            linewidth=2, elinewidth=1.3,
            color=colors[group],
            markerfacecolor='white',
            markeredgewidth=1.5
        )
    ax.set_xticks(x_ticks)
    ax.set_xlabel("Surface Coverage (%)", fontsize=font_size)
    ax.tick_params(direction="in", length=4, width=1, labelsize=font_size - 1)
    ax.xaxis.set_major_formatter(FuncFormatter(format_two_sigfigs_strict))
    ax.yaxis.set_major_formatter(FuncFormatter(format_two_sigfigs_strict))
    for spine in ax.spines.values():
        spine.set_linewidth(1)

    # Subplot titles
    ax.set_title("Interface" if idx == 0 else "Bulk", fontsize=font_size)

    # Shifted panel label (moved right to x=0.10)
    ax.text(0.06, 0.95, panel_label, transform=ax.transAxes,
            fontsize=font_size - 2, fontweight="bold", ha="left", va="top")

# Shared y-axis
axes[0].set_ylabel(r"$D_{\parallel}$ (×10⁻⁵ cm²/s)", fontsize=font_size)

# Legend (right plot only)
axes[1].legend(loc="upper right", frameon=False, fontsize=font_size - 5)

# === Final Touches ===
fig.tight_layout()

def set_size(w, h, ax=None):
    if ax is None:
        ax = plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w) / (r - l)
    figh = float(h) / (t - b)
    ax.figure.set_size_inches(figw, figh)

set_size(6.8, 3, axes[0])
fig.savefig(output_pdf, format="pdf", dpi=300, bbox_inches="tight")
print(f"[✓] Figure saved to {output_pdf} with panel labels and enforced trailing zero sig figs.")
