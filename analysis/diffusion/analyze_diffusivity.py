import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.signal import savgol_filter
import argparse
from glob import glob

# === Constants ===
timestep_fs = 1.0
species_list = ["water", "na", "cl"]
savgol_window = 51
savgol_poly = 2
ma_window = 201
fit_start_ps_default = 1000
slide_step = 100
min_window_ps = 8000

# === Argument Parser (compatible with rerun_msd.sh) ===
parser = argparse.ArgumentParser(description="Analyze MSD data for a single experiment.")
parser.add_argument("--input-dir", required=True, help="Directory containing MSD .dat files")
parser.add_argument("--output-dir", required=True, help="Directory to save outputs")
parser.add_argument("--experiment-name", required=True, help="Experiment name prefix")
args = parser.parse_args()

msd_dir = args.input_dir
base_dir = args.output_dir
exp = args.experiment_name

plot_dir = os.path.join(base_dir, "msd_vs_time_plots")
tables_dir = os.path.join(base_dir, "diffusivity_tables")
os.makedirs(plot_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)

summary_csv_path = os.path.join(tables_dir, "diffusivity_summary.csv")
summary_rows = []

def moving_average(x, window):
    return np.convolve(x, np.ones(window)/window, mode='same')

for species in species_list:
    filename = f"msd_{species}_{exp}.dat"
    filepath = os.path.join(msd_dir, filename)
    if not os.path.exists(filepath):
        continue

    try:
        data = np.loadtxt(filepath)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        continue

    time_ps = data[:, 0] * timestep_fs / 1000
    msd_xy = data[:, 1] + data[:, 2]

    smoothed = moving_average(msd_xy, ma_window)
    win_len = min(savgol_window, len(smoothed) // 2 * 2 + 1)
    smoothed_msd = savgol_filter(smoothed, window_length=win_len, polyorder=savgol_poly) if win_len >= savgol_poly + 2 else smoothed

    best_score = -np.inf
    best_fit = (0, np.array([]), np.array([]), 0, 0)

    available_time = time_ps[-1] - fit_start_ps_default
    min_window_effective = min_window_ps if available_time > min_window_ps else max(slide_step, int(available_time * 0.5))

    for window_ps in range(min_window_effective, int(available_time) + 1, slide_step):
        for start_ps in range(fit_start_ps_default, int(time_ps[-1]) - window_ps + 1, slide_step):
            end_ps = start_ps + window_ps
            start_idx = np.searchsorted(time_ps, start_ps)
            end_idx = np.searchsorted(time_ps, end_ps)
            if end_idx - start_idx < 10:
                continue
            X = time_ps[start_idx:end_idx].reshape(-1, 1)
            y = smoothed_msd[start_idx:end_idx]
            model = LinearRegression().fit(X, y)
            slope = model.coef_[0]
            r2 = model.score(X, y)
            score = r2 * np.log10(window_ps) if slope > 0.01 else -np.inf
            if score > best_score:
                best_score = score
                best_fit = (slope, X.flatten(), model.predict(X), time_ps[start_idx], time_ps[end_idx - 1])

    slope, Xfit, Yfit, fit_start, fit_end = best_fit
    D_cm2_s = (slope / 4) * 1e-4
    D_rounded = round(D_cm2_s * 1e5, 2)

    log_mask = (time_ps > 0) & (msd_xy > 0)
    alpha = 0.0
    if np.count_nonzero(log_mask) > 1:
        log_time = np.log10(time_ps[log_mask])
        log_msd = np.log10(msd_xy[log_mask])
        try:
            log_model = LinearRegression().fit(log_time.reshape(-1, 1), log_msd)
            alpha = log_model.coef_[0]
        except:
            alpha = 0.0

    summary_rows.append([exp, species, D_rounded, f"{fit_start:.0f}-{fit_end:.0f}", f"{best_score:.5f}", f"{alpha:.2f}"])

    # Plot linear MSD
    plt.figure(figsize=(6, 4))
    plt.plot(time_ps, msd_xy, label="MSD_x + MSD_y", alpha=0.6)
    if len(Xfit) > 0:
        plt.plot(Xfit, Yfit, '--', label=f'D = {D_rounded:.2f}×10⁻⁵ cm²/s')
    else:
        plt.text(0.5, 0.5, "No valid fit", transform=plt.gca().transAxes,
                 ha='center', va='center', color='red')
    plt.title(f"{species.upper()} MSD — {exp}")
    plt.xlabel("Time (ps)")
    plt.ylabel("MSD (Å²)")
    plt.grid(True)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f"{exp}_{species}_msd_linear.png"), dpi=300)
    plt.close()

# Update summary CSV
df_new = pd.DataFrame(summary_rows, columns=["experiment", "species", "D", "fit_range_ps", "R2", "alpha"])
if os.path.exists(summary_csv_path):
    df_old = pd.read_csv(summary_csv_path)
    df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates()
else:
    df_combined = df_new

def parse_expname(exp):
    match = re.match(r"(\d*)([A-Za-z0-9]+)_(\d+)nacl(?:_trial(\d+))?", exp)
    if match:
        nfunc = int(match.group(1)) if match.group(1) else 0
        functional = match.group(2).upper()
        nnacl = int(match.group(3))
        trial = int(match.group(4)) if match.group(4) else 1
        return pd.Series([functional, nfunc, nnacl, trial])
    else:
        raise ValueError(f"Failed to parse experiment name: {exp}")

df_combined[["functional", "nfunc", "nnacl", "trial"]] = df_combined["experiment"].apply(parse_expname)
df_combined.to_csv(summary_csv_path, index=False)

print(f"[DONE] Diffusivity analysis for {exp}")
print(f"       Summary → {summary_csv_path}")
print(f"       Plots → {plot_dir}")
