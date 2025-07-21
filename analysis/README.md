# Analysis Scripts

This directory contains all post-processing scripts used to analyze molecular dynamics simulations of water at functionalized graphene–electrolyte interfaces. The analysis is divided into two main components:

## Density Profiles (`analysis/density/`)

Scripts in this folder compute spatial density profiles of water, Na⁺, and Cl⁻ species across the simulation box.

### Included scripts:
- `run_dens.sh` — Main SLURM batch submission script.
- `automate_density.py` — Entry point that orchestrates the analysis pipeline.
- `density_analysis.py` — Computes number density profiles using a fixed slab spacing (nbin=200), without wall position normalization.
- `process_density_profiles.py` — Normalizes the z-axis by wall positions from `.txt` files located in each simulation folder.

### How to use:
1. Run the shell script:
   ```
   sbatch run_dens.sh
   ```
   This executes `automate_density.py`, which calls `density_analysis.py` to compute raw profiles.

2. Normalize z coordinates:
   ```
   python process_density_profiles.py
   ```
   This will generate trial-specific subfolders containing `.csv` files of normalized density profiles for all experiments in each trial.

## Diffusion Coefficients (`analysis/diffusion/`)

Scripts in this folder compute the planar diffusion coefficient D_parallel for confined and bulk water.

### Included scripts:
- `rerun_msd.in` — LAMMPS input file to compute MSD from saved trajectories.
- `rerun.sh` — SLURM script to compute interfacial diffusion.
- `rerun_mid.sh` — SLURM script to compute bulk diffusion.
- `extract_wall_positions.py` — Helper to get static wall positions for defining interfacial region.
- `analyze_diffusivity.py` — Computes D_parallel by linearly fitting MSD vs. time, with COM correction and smoothing.

### How to use:
Run the rerun jobs:
   ```
   sbatch rerun.sh       # For interface
   sbatch rerun_mid.sh   # For bulk
   ```
   This will:
   - Fit the linear MSD segment (excluding initial ballistic regime)
   - Generate summary Excel tables of D_parallel for all trials
   - Plot MSD vs. time curves with linear fits

Contact: npn25@cornell.edu
