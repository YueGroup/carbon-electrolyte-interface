#!/bin/bash
#SBATCH --job-name="MSDmid_RERUN"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH -t 48:00:00

export SLURM_EXPORT_ENV=ALL
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# === Paths ===
LAMMPS=/home/fs01/lth26/Packages/lammps-stable_23Jun2022/build/lmp_cac
SIM_DIR=/home/fs01/lth26/Projects/graphene_sandwich_project/automation_run
WORKDIR=/home/fs01/npn25/projects/automation_run/trial1_2_diffusion_mid
INPUT=rerun_msd_mid.in

# === Create output folders ===
mkdir -p ${WORKDIR}/{rerun.log,rerun_output,rerun_error,msd.dat,analyze_diffusivity_output.log,msd_vs_time_plots,diffusivity_tables}

# === Loop over dump files ===
for dumpfile in ${SIM_DIR}/dump_prod2_wrapped/dump_prod2_wrapped_*.lammpstrj; do
    filename=$(basename "$dumpfile")
    expname=${filename#dump_prod2_wrapped_}
    expname=${expname%.lammpstrj}

    first_field=$(echo $expname | cut -d_ -f1)
    nfunc=$(echo $first_field | grep -oE '^[0-9]+')
    functional=${first_field#$nfunc}
    nnacl=$(echo $expname | cut -d_ -f2 | tr -d -c 0-9)
    trial=$(echo $expname | cut -d_ -f3 | tr -d -c 0-9)
    nwater=500

    echo "[START] Rerun for $expname"

    # === Paths to wall position files ===
    summary_path="${SIM_DIR}/${functional}/wall_positions/${nfunc}${functional}_${nnacl}nacl_trial${trial}_positions_summary.txt"
    wallvars_file="${WORKDIR}/wall_vars_mid.txt"

    # Call the Python extractor
    module load python/3.12.2  # or whatever Python version in use
    source ~/venv_density/bin/activate

    python /home/fs01/npn25/projects/automation_script/slab_diffusion/extract_wall_positions.py \
        "$summary_path" "$wallvars_file"

    if [[ ! -s "$wallvars_file" ]]; then
        echo "[ERROR] wall_vars_mid.txt is empty. Skipping $expname"
        continue
    fi

    $LAMMPS -var SIM_DIR $SIM_DIR \
            -var WRAPPED_FILE $dumpfile \
            -var WORKDIR $WORKDIR \
            -var EXPNAME $expname \
            -var FUNCTIONAL $functional \
            -var NFUNC $nfunc \
            -var NNACL $nnacl \
            -var TRIAL $trial \
            -var NWATER $nwater \
            -var WALLVARFILE $wallvars_file \
            -in $INPUT \
            -log ${WORKDIR}/rerun.log/rerun_${expname}.log \
            > ${WORKDIR}/rerun_output/rerun_${expname}.out \
            2> ${WORKDIR}/rerun_error/rerun_${expname}.err

    success=false
    if [[ -f ${WORKDIR}/msd.dat/msd_water_${expname}.dat ]]; then
        echo "[DONE] Rerun for water → msd_water_${expname}.dat"
        success=true
    fi
    if [[ $nnacl -gt 0 ]]; then
        if [[ -f ${WORKDIR}/msd.dat/msd_na_${expname}.dat ]]; then
            echo "[DONE] Rerun for na → msd_na_${expname}.dat"
            success=true
        fi
        if [[ -f ${WORKDIR}/msd.dat/msd_cl_${expname}.dat ]]; then
            echo "[DONE] Rerun for cl → msd_cl_${expname}.dat"
            success=true
        fi
    fi

    if [[ "$success" = true ]]; then
        echo "[START] Post-analysis for $expname"
        module load python/3.12.2
        source ~/venv_density/bin/activate
        python analyze_diffusivity.py \
            --input-dir ${WORKDIR}/msd.dat \
            --output-dir ${WORKDIR} \
            --experiment-name $expname \
            > ${WORKDIR}/analyze_diffusivity_output.log/analyze_diffusivity_output_${expname}.log \
            2>&1
        echo "[DONE] Post-analysis for $expname"
    else
        echo "[FAIL] No MSD .dat for $expname. Skipping analysis."
    fi

    echo "[FINISH] $expname"
    echo
done
