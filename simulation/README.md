# Simulation

This folder contains LAMMPS input files and SLURM job scripts.

# Usage:

1. Run lammps1 scripts.
  lammps1 files are used to determine fixed sheet distance.
  Produces dump files for vmd analysis.
  Produces gap_vs_time.txt files that record graphene sheet locations versus time.
3. Run graphene_sheet distance scripts.
  Reads gap_vs_time.txt files and generates files that  sheet distance.
  gap
4. Run lammps2 scripts.
