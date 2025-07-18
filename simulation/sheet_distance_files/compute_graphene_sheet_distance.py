import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

parser = argparse.ArgumentParser(description="Compute equilibrium Z positions of graphene sheets")
parser.add_argument('-i', type=str, dest='file', required=True, help='gap vs time file')
parser.add_argument('-o', type=str, dest='outname', default='graphene_zpos', help='output filename prefix')
args = parser.parse_args()

file = args.file
outname = args.outname

def analyze_lammps_data(filename="gap_vs_time.txt", plot = False, nequilsteps = 10000):
    """
    Reads time-averaged LAMMPS data, and computes stats
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found. Please ensure the file exists in the correct directory.")
        return

    print(f"Analyzing data from: {filename}")

    try:
        data = np.genfromtxt(filename, skip_header=2, dtype=float)

    except ValueError as e:
        print(f"Error reading data: {e}")
        print("Please ensure the file format matches 'TimeStep v_gap c_zmin2 c_zmax1' with space-separated numbers.")
        return
    except Exception as e:
        print(f"An unexpected error occurred during file reading: {e}")
        return

    # Ensure we have enough columns
    if data.shape[1] < 4:
        print(f"Error: Expected at least 4 columns (TimeStep, v_gap, c_zmin2, c_zmax1), but found {data.shape[1]}.")
        return

    # Extract columns
    time_steps = data[:, 0]
    v_gap = data[:, 1]
    c_zmin2 = data[:, 2]
    c_zmax1 = data[:, 3]

    # --- Compute Average and Standard Deviation of the Second Column (v_gap) ---
    avg_v_gap = np.mean(v_gap)
    std_v_gap = np.std(v_gap)
    avg_c_zmin2 = np.mean(c_zmin2)
    std_c_zmin2 = np.std(c_zmin2)
    avg_c_zmax1 = np.mean(c_zmax1)
    std_c_zmax1 = np.std(c_zmax1)

    # write file to be read by lammps2.in file 
    with open(f"{outname}.txt", "w") as f:
        f.write(f'variable shift2_rate equal {(avg_c_zmin2-50)/nequilsteps}\n')
        f.write(f'variable shift1_rate equal {(avg_c_zmax1)/nequilsteps}\n')
    # write file summarizing results
    with open(f"{outname}_summary.txt", "w") as f:
        f.write(f'Average gap: {avg_v_gap}+-{std_v_gap}\n')
        f.write(f'Average wall1: {avg_c_zmax1}+-{std_c_zmax1}\n')
        f.write(f'Average wall2: {avg_c_zmin2}+-{std_c_zmin2}\n')
        f.write(f'variable shift2_rate equal {(avg_c_zmin2-50)/nequilsteps}\n')
        f.write(f'variable shift1_rate equal {(avg_c_zmax1)/nequilsteps}\n')

    if plot:  
        # --- Plotting ---
        plt.figure(figsize=(12, 7))
        plt.plot(time_steps, v_gap, label='Gap Distance (v_gap)', marker='o', markersize=4, linestyle='-')
        plt.plot(time_steps, c_zmin2, label='Min Z of Wall 2 (c_zmin2)', marker='x', markersize=4, linestyle='--')
        plt.plot(time_steps, c_zmax1, label='Max Z of Wall 1 (c_zmax1)', marker='s', markersize=4, linestyle=':')
        plt.xlabel('TimeStep')
        plt.ylabel('Value (Angstroms or whatever units you use)')
        plt.title('Gap Distance and Wall Z-Positions Over Time')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        # Save the plot
        # plt.savefig("gap_vs_time_plot.png", dpi=300) 

        plt.show() # Display the plot

# --- Run the analysis ---
if __name__ == "__main__":
    analyze_lammps_data(file, plot = False)
