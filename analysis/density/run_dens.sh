#!/bin/bash
#SBATCH --job-name=density_analysis
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=24:00:00
#SBATCH --output=run_dens_%j.out
#SBATCH --error=run_dens_%j.err

set -euo pipefail

# === Load modules and activate environment ===
module load python/3.12.2
source ~/venv_density/bin/activate

# === Define paths ===
#Trial 1 and 2
AUTOMATION_FOLDER="automation_run"
SCRIPT_DIR="/home/fs01/npn25/projects/automation_script/slab_diffusion"
INPUT_DIR="/home/fs01/lth26/Projects/graphene_sandwich_project/${AUTOMATION_FOLDER}/dump_prod2_wrapped"
OUTPUT_DIR="/home/fs01/npn25/projects/${AUTOMATION_FOLDER}/trial1_2_density_150bin"

# #Trial 3
# AUTOMATION_FOLDER="automation_run_from_expanse"
# SCRIPT_DIR="/home/fs01/npn25/projects/automation_script/slab_diffusion"
# INPUT_DIR="/home/fs01/lth26/Projects/graphene_sandwich_project/${AUTOMATION_FOLDER}/dump_prod2_wrapped"
# OUTPUT_DIR="/home/fs01/npn25/projects/${AUTOMATION_FOLDER}/trial3_density_${nbin}bin"
# mkdir -p ${OUTPUT_DIR}

echo "[INFO] Job started on $(hostname) at $(date)"
echo "[INFO] INPUT_DIR = ${INPUT_DIR}"
echo "[INFO] OUTPUT_DIR = ${OUTPUT_DIR}"
ls ${INPUT_DIR} || echo "[WARN] No files found in INPUT_DIR"

# === Run analysis ===
python ${SCRIPT_DIR}/automate_density.py \
    -i ${INPUT_DIR} \
    -o ${OUTPUT_DIR} \
    -n 4 \
    --stride 1