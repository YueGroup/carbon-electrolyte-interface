import os
import re
import pandas as pd

# === Constants ===
nbin = 200
#Trial 1 and 2:
SIM_DIR = "/home/fs01/lth26/Projects/graphene_sandwich_project/automation_run"
WORKDIR = f"/home/fs01/npn25/projects/automation_run/trial1_2_density_{nbin}bin"
TRIAL = 2  # Change this to 1 or 2 if needed

# # Trial 3:
# SIM_DIR = "/home/fs01/lth26/Projects/graphene_sandwich_project/automation_run_from_expanse"
# WORKDIR = f"/home/fs01/npn25/projects/automation_run_from_expanse/trial3_density_{nbin}bin"
# TRIAL = 3  

OUTPUT_BASE = f"/home/fs01/npn25/projects/Figures/density_csv_{nbin}bin"
OUTPUT_DIR = os.path.join(OUTPUT_BASE, f"density_trial{TRIAL}_csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Functions ===

def parse_filename(fname):
    match = re.match(r"density_(\w+)_(\d+)([A-Za-z0-9]+)_(\d+)nacl_trial(\d+).dat", fname)
    if match:
        species, nfunc, fg, nnacl, trial = match.groups()
        return species, int(nfunc), fg.upper(), int(nnacl), int(trial)
    return None

def extract_wall_positions(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    wall1_match = re.search(r'Average wall1:\s*([\d\.\-+Ee]+)', content)
    wall2_match = re.search(r'Average wall2:\s*([\d\.\-+Ee]+)', content)
    if wall1_match and wall2_match:
        wall1_mean = float(wall1_match.group(1).split('+')[0])
        wall2_mean = float(wall2_match.group(1).split('+')[0])
        return wall1_mean, wall2_mean
    return None, None

def process_dat_file(filepath, wall1, wall2):
    try:
        df = pd.read_csv(filepath, sep=r"\s+", engine="python", comment="#", header=None)
        df.columns = ["z (A)", "density (g/cm^3)"]

        # Round z to 2 decimal places and group
        df["z_rounded"] = df["z (A)"].round(2)
        df_grouped = df.groupby("z_rounded", as_index=False)["density (g/cm^3)"].mean()

        # Fold about z=0 by averaging mirrored densities
        df_grouped["z_abs"] = df_grouped["z_rounded"].abs()
        df_folded = df_grouped.groupby("z_abs", as_index=False)["density (g/cm^3)"].mean()

        # Normalize to wall position using corrected formula
        center = (wall1 + wall2) / 2
        wall_distance = abs(wall2 - center)
        df_folded["z_wall"] = wall_distance - df_folded["z_abs"]
        df_folded["z_wall"] = df_folded["z_wall"].round(2)

        # Final rounded z_wall in nanometers to 2 decimal places (instead of 3)
        df_folded["z_wall_nm"] = (df_folded["z_wall"] / 10).round(2)

        return df_folded[["z_wall_nm", "density (g/cm^3)"]]

    except Exception as e:
        print(f"⚠️ Error processing {filepath}: {e}")
        return None

# === Main Processing ===
for fname in os.listdir(WORKDIR):
    if not fname.endswith(f"trial{TRIAL}.dat"):
        continue
    parsed = parse_filename(fname)
    if not parsed:
        continue
    species, nfunc, fg, nnacl, trial = parsed
    if trial != TRIAL:
        continue

    expname = f"{nfunc}{fg}_{nnacl}nacl_trial{trial}"
    summary_path = os.path.join(SIM_DIR, fg, "wall_positions", f"{expname}_positions_summary.txt")
    wall1, wall2 = extract_wall_positions(summary_path)

    if wall1 is None or wall2 is None:
        print(f"❌ Skipping {fname}: wall positions not found.")
        continue

    input_path = os.path.join(WORKDIR, fname)
    processed_df = process_dat_file(input_path, wall1, wall2)

    if processed_df is not None:
        output_csv = os.path.join(OUTPUT_DIR, fname.replace(".dat", ".csv"))
        processed_df.to_csv(output_csv, index=False)
        print(f"[✓] Processed and saved: {output_csv}")