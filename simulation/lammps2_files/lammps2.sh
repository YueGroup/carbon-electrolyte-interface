#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-core=1
#SBATCH -t 200:00:00

n_func="$1"
n_nacl="$2"
functional="$3"
trial="$4"

export SLURM_EXPORT_ENV=ALL
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

echo "Starting job $SLURM_JOB_ID at $(date) on $(hostname)"
echo "Home directory is $HOME"

# CHANGE BELOW
code=/home/fs01/lth26/Packages/lammps-stable_23Jun2022/build/lmp_cac # location of LAMMPS executable
# CHANGE ABOVE

# Define scratch directory
MYTMP=/tmp/$USER/$SLURM_JOB_ID
/usr/bin/mkdir -p $MYTMP || exit $?
echo "Scratch directory created: $MYTMP"

# Copy input files
echo "Copying input files to scratch directory..."
cp -rp $SLURM_SUBMIT_DIR/* $MYTMP || exit $?   # Copy all files recursively
echo "Input files copied: $(ls -lh $MYTMP)"

# Navigate to the scratch directory
cd $MYTMP

# Run your program
echo "Running job..."
mpirun -np $SLURM_NTASKS $code -in lammps2.in -log none -v nfunc $n_func -v nnacl $n_nacl -v functional $functional -v trial $trial

# Copy all files back to the submission directory
echo "Copying all files back to submission directory..."
cp -rp $MYTMP/* $SLURM_SUBMIT_DIR || exit $?  # Copy all files from scratch back
echo "Files copied back to: $SLURM_SUBMIT_DIR"

# Clean up scratch directory
echo "Cleaning up scratch directory..."
rm -rf $MYTMP
echo "Scratch directory removed."

echo "Job $SLURM_JOB_ID ended at $(date) on $(hostname)"
exit 0
