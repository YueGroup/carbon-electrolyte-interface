# Simulation

This folder contains LAMMPS input files and SLURM job scripts.

## Repository Structure:

```
simulation/
├── lammps1_files/       # LAMMPS input scripts and run templates for sheet distance equilibration
├── sheet_distance_files/          # Python input scripts and run templates for generating sheet distance files
├── lammps2_files/         # LAMMPS input scripts and run templates for production run
├── OH/          # -OH input files
├── COOH/          # -COOH input files
├── CO/          # =O input files
├── CH3/          # -CH3 input files
├── UNFUNC/          # Unfunctionalized input files
├── submit_files.py/          # Python script to submit lammps1, sheet distance, or lammps2 files
├── groups.py/          # Modified groups.py file for generating initial configurations: `carbonstructures/src/carbonstructures/functionalization`
└── README.md         # This file
```

## Dependencies:

LAMMPS package - 23Jun2022: [`lammps`](https://www.lammps.org/#gsc.tab=0)

## Usage:

### 1. Run `lammps1_files` scripts.
- lammps1 files are for sheet distance equilibration.
- Produces dump files for vmd analysis.
- Produces files that record graphene sheet locations versus time.
### 2. Run `sheet_distance_files` scripts.
- Reads sheet distance files and generates files for lammps2 input.
### 3. Run `lammps2_files` scripts.
- lammps2 files are for production trajectories.
- Produces dump files for trajectory analysis.
