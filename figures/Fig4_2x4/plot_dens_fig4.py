import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import defaultdict
from scipy.signal import savgol_filter

# === SETTINGS ===
nnacl = 27
nbin = 200
input_base = f"/Users/nhinguyen/Desktop/Pic/Figures/density_csv_{nbin}bin"
output_prefix = f"fig4_na_cl_{nnacl}nacl_{nbin}bins"
font_size = 17

savgol_window = 7 # use 11 for 4, 9, 18 nnacl
savgol_poly = 2

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

def load_profiles(species):
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
            z = (df["z_wall_nm"] * 10).round(1)  # Convert to Ångström
            d = df["density (g/cm^3)"]
            if fg == "UNFUNC":
                unfunc_curves.append((z, d))
            elif fg in plot_groups:
                group_profiles[fg][label].append((z, d))
    return group_profiles, unfunc_curves

# === LOAD DATA ===
na_profiles, na_unfunc = load_profiles("na")
cl_profiles, cl_unfunc = load_profiles("cl")

# === GLOBAL AXIS RANGE ===
all_densities = []
for group_dict in [na_profiles, cl_profiles]:
    for fg in plot_groups:
        for curves in group_dict[fg].values():
            all_densities += [d for _, d in curves]
for unfunc_list in [na_unfunc, cl_unfunc]:
    all_densities += [d for _, d in unfunc_list]
global_min = min([d.min() for d in all_densities])
global_max = max([d.max() for d in all_densities])

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

# === PLOT ===
plt.rcParams["font.family"] = "Helvetica"
fig, axes = plt.subplots(2, 4, figsize=(12, 6), sharex=True, sharey=True)

panel_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)']
panel_idx = 0

for row_idx, (species_profiles, unfunc_curves, row_label) in enumerate(
    [(na_profiles, na_unfunc, "Na⁺"), (cl_profiles, cl_unfunc, "Cl⁻")]
):
    for col_idx, fg in enumerate(plot_groups):
        ax = axes[row_idx, col_idx]
        label = functional_group_map[fg]

        ax.text(0.03, 0.95, panel_labels[panel_idx], transform=ax.transAxes,
                fontsize=font_size - 2, fontweight='bold', va='top', ha='left')
        panel_idx += 1

        if unfunc_curves:
            df = pd.concat([pd.DataFrame({"z": z, "density": dens}) for z, dens in unfunc_curves], axis=0)
            df = df.groupby("z").agg(["mean", "std"])
            z = df.index.values
            mean = df[("density", "mean")].values
            std = df[("density", "std")].values
            label_unfunc = "Unfunctionalized"
            if len(mean) >= savgol_window:
                mean_smooth = savgol_filter(mean, savgol_window, savgol_poly)
                upper_smooth = savgol_filter(mean + std, savgol_window, savgol_poly)
                lower_smooth = savgol_filter(mean - std, savgol_window, savgol_poly)
            else:
                mean_smooth = mean
                upper_smooth = mean + std
                lower_smooth = mean - std
            ax.plot(z, mean_smooth, color=coverage_colors[label_unfunc], linewidth=2, label=label_unfunc)
            ax.fill_between(z, lower_smooth, upper_smooth, alpha=0.3, color=coverage_colors[label_unfunc])

        for cov_level in ["Low (2.2%)", "Medium (4.4%)", "High (6.6%)"]:
            curves = species_profiles[fg][cov_level]
            if not curves:
                continue
            df = pd.concat([pd.DataFrame({"z": z, "density": dens}) for z, dens in curves], axis=0)
            df = df.groupby("z").agg(["mean", "std"])
            z = df.index.values
            mean = df[("density", "mean")].values
            std = df[("density", "std")].values
            if len(mean) >= savgol_window:
                mean_smooth = savgol_filter(mean, savgol_window, savgol_poly)
                upper_smooth = savgol_filter(mean + std, savgol_window, savgol_poly)
                lower_smooth = savgol_filter(mean - std, savgol_window, savgol_poly)
            else:
                mean_smooth = mean
                upper_smooth = mean + std
                lower_smooth = mean - std
            ax.plot(z, mean_smooth, label=cov_level, color=coverage_colors[cov_level], linewidth=2)
            ax.fill_between(z, lower_smooth, upper_smooth, alpha=0.3, color=coverage_colors[cov_level])

        ax.set_ylim(global_min, global_max)
        ax.xaxis.set_major_formatter(FuncFormatter(format_one_sigfig))
        ax.yaxis.set_major_formatter(FuncFormatter(format_one_sigfig))
        ax.set_title(label, fontsize=font_size)
        ax.tick_params(direction="in", length=4, width=1, labelsize=font_size - 2.5)
        for spine in ax.spines.values():
            spine.set_linewidth(1)

        if col_idx == 0:
            ax.set_ylabel("Density (g/cm³)", fontsize=font_size)
            ax.annotate(row_label, xy=(-0.28, 0.5), xycoords="axes fraction",
                        rotation=90, ha="center", va="center", fontsize=font_size)
        if row_idx == 1:
            ax.set_xlabel("z (Å)", fontsize=font_size)  # ← updated unit
        if row_idx == 0 and col_idx == 3:
            ax.legend(loc="upper right", frameon=False, fontsize=font_size - 5.5)

fig.tight_layout()
plt.savefig(f"{output_prefix}.pdf", dpi=300, bbox_inches="tight")
print(f"[✓] Figure saved to {output_prefix}.pdf with z-axis in Å.")
