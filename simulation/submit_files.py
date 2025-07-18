import subprocess
import argparse
import os
import time

parser = argparse.ArgumentParser(description="Run files of chosen type")
parser.add_argument('-s', type=str, dest='script', required=True, help='script to run') # lammps1, lammps2, sheet_distance determines which files are submitted
args = parser.parse_args()

script = args.script

# Define the values you want to loop over
functional_groups = ['OH','CH3','COOH','CO'] # OH, CH3, COOH, CO, submit UNFUNC separately
nfunc_values = [8,16,24] #8, 16, 24, for UNFUNC put 0
nnacl_values = [0,4,9,18,27,36,45] #0, 4, 9, 18, 27, 36, 45
trials = [1,2,3] #1, 2, 3

# CHANGE BELOW
home = "/home/fs01/lth26/Projects/graphene_sandwich_project/automation_run" # Home directory (eg where this file is located)
# CHANGE ABOVE
job_dir = f"{home}/{script}_files"
log_dir = f"{home}/slurm_logs"
run_script = f"{job_dir}/{script}.sh"
# Ensure job and log directories exist before starting job submissions
os.makedirs(job_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Loop and submit jobs
for trial in trials:
    for functional in functional_groups:
        for nfunc in nfunc_values:
            for nnacl in nnacl_values:
                time.sleep(2)

                short_job_name = f"{nfunc}{functional}_{nnacl}"
                job_name = f"{script}_{nfunc}{functional}_{nnacl}nacl_trial{trial}"
                output_file = f"{log_dir}/{job_name}.out"

                print(f"Submitting job: {job_name}")

                # sbatch command with positional args for run.sh
                cmd = [
                    "sbatch",
                    "--job-name", short_job_name,
                    "--output", output_file,
                    run_script,
                    str(nfunc),
                    str(nnacl),
                    str(functional),
                    str(trial)
                ]

                # Submit the job
                try:
                    result = subprocess.run(cmd, cwd=job_dir, capture_output=True, text=True, check=True)
                    job_id = result.stdout.strip().split()[-1]
                    print(f"  Submitted with Job ID: {job_id}")
                except subprocess.CalledProcessError as e:
                    print(f"  Error submitting job {job_name}:")
                    print(f"  STDOUT: {e.stdout}")
                    print(f"  STDERR: {e.stderr}")
                except Exception as e:
                    print(f"  An unexpected error occurred during job submission: {e}")
