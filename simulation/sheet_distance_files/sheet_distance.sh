#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-core=1
#SBATCH -t 23:00:00

n_func="$1"
n_nacl="$2"
functional="$3"
trial="$4"

python compute_graphene_sheet_distance.py -i ../lammps1_files/gap_files/gap_vs_time_${n_func}${functional}_${n_nacl}nacl_trial${trial}.txt -o ../${functional}/wall_positions/${n_func}${functional}_${n_nacl}nacl_trial${trial}_positions
