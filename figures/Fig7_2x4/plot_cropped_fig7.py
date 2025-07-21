import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import FuncFormatter

# === SETTINGS ===
species = "water"
font_size = 15
input_dir = "/Users/nhinguyen/Desktop/Pic/Figures/diffusion_csv/8000ps"
input_surface = os.path.join(input_dir, f"diff_{species}.csv")
input_bulk = os.path.join(input_dir, f"diff_{species}bulk.csv")

output_pdf_cooh = f"fig7_{species}_diffusion_COOH_only.pdf"
output_pdf_rest = f"fig7_{species}_diffusion_OH_CO_CH3.pdf"

# === MAPPINGS ===
functional_group_map = {
    "CH3": "-CH₃",
    "COOH": "-COOH",
    "OH": "-OH",
    "CO": "=O"
}
nfunc_to_coverage = {
    8: "Low (2.2%)",
    16: "Medium (4.4%)",
    24: "High (6.6%)"
}
coverage_colors = {
    "Low (2.2%)": "#7FB3D5",
    "Medium (4.4%)": "#F4D03F",
    "High (6.6%)": "#C0392B"
}
nnacl_to_conc = {
    0: 0,
    4: 0.44,
    9: 1,
    18: 2,
    27: 3,
    36: 4,
    45: 5
}

def format_two_sigfigs_strict(x, _):
    if x == 0:
        return "0"
    elif x < 1:
        return f"{x:.2f}"
    elif x < 10:
        return f"{x:.2g}" if x % 1 else f"{x:.1f}"
    elif x < 100:
        return f"{x:.2g}" if x % 1 else f"{x:.1f}"
    else:
        return f"{x:.1e}"

def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df = df[df["functional_group"].isin(functional_group_map.keys())]
    df["functional_group_label"] = df["functional_group"].map(functional_group_map)
    df["coverage_label"] = df["nfunc"].map(nfunc_to_coverage)
    df["electrolyte_conc"] = df["nnacl"].map(nnacl_to_conc)
    trial_cols = ["D_trial1", "D_trial2", "D_trial3"]
    df[trial_cols] = df[trial_cols].replace(0, np.nan)
    df = df.dropna(subset=trial_cols, how='all')
    df["D_avg"] = df[trial_cols].mean(axis=1)
    df["D_std"] = df[trial_cols].std(axis=1)
    return df

def plot_subset(df_surface, df_bulk, fg_subset, output_pdf, legend_fg_key=None):
    plt.style.use("default")
    plt.rcParams["font.family"] = "Helvetica"
    full_ncols = 4  # Always reserve 4 columns for layout consistency
    panel_width = 3.125  # inches
    fig, axs = plt.subplots(2, full_ncols, figsize=(panel_width * full_ncols, 5.5), sharex=True, sharey=True)

    panel_labels = [f"({chr(ord('a') + i)})" for i in range(8)]
    panel_idx = 0

    for row_idx, (df, is_bulk, row_label) in enumerate([(df_surface, False, "Surface"), (df_bulk, True, "Bulk")]):
        for col_idx in range(full_ncols):
            ax = axs[row_idx, col_idx]
            if col_idx >= len(fg_subset):
                ax.axis("off")  # Hide unused columns
                continue

            fg_key = fg_subset[col_idx]
            group_label = functional_group_map[fg_key]
            sub_df = df[df["functional_group"] == fg_key]

            ax.text(0.08, 0.95, panel_labels[panel_idx], transform=ax.transAxes,
                    fontsize=font_size - 2, fontweight='bold', va='top', ha='left')
            panel_idx += 1

            for cov in ["Low (2.2%)", "Medium (4.4%)", "High (6.6%)"]:
                cov_df = sub_df[sub_df["coverage_label"] == cov]
                if not cov_df.empty:
                    cov_df_sorted = cov_df.sort_values("electrolyte_conc")
                    ax.errorbar(
                        cov_df_sorted["electrolyte_conc"],
                        cov_df_sorted["D_avg"],
                        yerr=cov_df_sorted["D_std"],
                        label=cov,
                        fmt='o-',
                        linewidth=2,
                        capsize=4,
                        markersize=5,
                        elinewidth=1.5,
                        color=coverage_colors[cov]
                    )

            if len(fg_subset) > 1:
                ax.set_title(group_label, fontsize=font_size)

            ax.set_xticks([0, 1, 2, 3, 4, 5])
            ax.xaxis.set_major_formatter(FuncFormatter(format_two_sigfigs_strict))
            ax.yaxis.set_major_formatter(FuncFormatter(format_two_sigfigs_strict))
            ax.tick_params(direction="in", length=4, width=1, labelsize=font_size-3)
            for spine in ax.spines.values():
                spine.set_linewidth(1)

            if col_idx == 0:
                ylabel = rf"$D_{{\parallel,\mathrm{{{'bulk' if is_bulk else 'interface'}}}}}$ ($\times 10^{{-5}}$ cm$^2$/s)"
                ax.set_ylabel(ylabel, fontsize=font_size-1)
            if row_idx == 1:
                ax.set_xlabel(r"$\mathit{m}$ (mol/kg)", fontsize=font_size-1)

            if row_idx == 0 and fg_key == legend_fg_key:
                handles = [plt.Line2D([0], [0], color=coverage_colors[c], lw=2) for c in coverage_colors]
                labels = list(coverage_colors.keys())
                ax.legend(handles, labels, frameon=False, fontsize=font_size - 2, loc="upper right")

    fig.tight_layout()
    fig.savefig(output_pdf, format="pdf", dpi=300, bbox_inches="tight")
    print(f"[✓] Figure saved to {output_pdf}")


# === LOAD DATA ===
df_surface = load_and_process(input_surface)
df_bulk = load_and_process(input_bulk)

# === PLOTS ===
plot_subset(df_surface, df_bulk, fg_subset=["COOH"], output_pdf=output_pdf_cooh, legend_fg_key="COOH")
plot_subset(df_surface, df_bulk, fg_subset=["OH", "CO", "CH3"], output_pdf=output_pdf_rest, legend_fg_key="CH3")
