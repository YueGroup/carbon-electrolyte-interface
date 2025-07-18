#!/bin/bash
#SBATCH --job-name="auto_lammps1"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH -t 1:00:00

# CHANGE BELOW
python /home/fs01/lth26/Projects/graphene_sandwich_project/automation_run/submit_files.py -s lammps1

