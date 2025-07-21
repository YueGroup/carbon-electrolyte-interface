import os
import re
import argparse
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
from density_analysis import analyze_density

species_info = {'water': 'type 1', 'cl': 'type 3', 'na': 'type 4'}

def process_file(file, input_folder, output_folder, stride):
    full_path = os.path.join(input_folder, file)
    match = re.match(r'dump_prod2_wrapped_(.*?)\.lammpstrj', file)
    if not match:
        return [], []

    exp_name = match.group(1)
    log_lines = [f"[START] Processing experiment: {exp_name}"]
    errors = []
    centers = None
    densities = {}

    for species in ['water']:
        try:
            centers, profile = analyze_density(full_path, species, species_info[species], exp_name, output_folder, stride)
            densities[species] = profile
            log_lines.append(f"  - Completed: {species}")
        except Exception as e:
            err_msg = f"  [ERROR] {species} → {exp_name}: {str(e)}"
            log_lines.append(err_msg)
            errors.append(err_msg)

    if 'nacl' in exp_name.lower():
        digits = re.findall(r'(\d+)nacl', exp_name.lower())
        if digits and int(digits[0]) > 0:
            for species in ['na', 'cl']:
                try:
                    _, profile = analyze_density(full_path, species, species_info[species], exp_name, output_folder, stride)
                    densities[species] = profile
                    log_lines.append(f"  - Completed: {species}")
                except Exception as e:
                    err_msg = f"  [ERROR] {species} → {exp_name}: {str(e)}"
                    log_lines.append(err_msg)
                    errors.append(err_msg)

    if densities:
        fig, axs = plt.subplots(len(densities), 1, figsize=(6, 4 * len(densities)), sharex=True)
        if len(densities) == 1:
            axs = [axs]
        for ax, (species, profile) in zip(axs, densities.items()):
            ax.plot(centers, profile, label=species, linewidth=2)
            ax.set_ylabel('Density (g/cm$^3$)')
            ax.set_title(f"{species.capitalize()} density profile")
            ax.grid(True)
            ax.legend()
        axs[-1].set_xlabel('z ($\AA$)')
        plt.tight_layout()
        out_png = os.path.join(output_folder, f"density_{exp_name}.png")
        plt.savefig(out_png, dpi=300)
        plt.close()
        log_lines.append(f"  - Saved plot: {out_png}")

    log_lines.append(f"[FINISH] Density profile obtained for {exp_name}\n")
    return log_lines, errors

def main(input_folder, output_folder, nprocs, stride):
    os.makedirs(output_folder, exist_ok=True)
    dump_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".lammpstrj") and f.startswith("dump_prod2_wrapped_")])
    all_logs = []
    all_errors = []

    with Pool(processes=nprocs) as pool:
        func = partial(process_file, input_folder=input_folder, output_folder=output_folder, stride=stride)
        results = pool.map(func, dump_files)

    for logs, errs in results:
        all_logs.extend(logs)
        all_errors.extend(errs)

    log_path = os.path.join(output_folder, "density_analysis_log.txt")
    with open(log_path, 'w') as f:
        f.write("\n".join(all_logs))

    if all_errors:
        subject = "Density Analysis: Errors Detected"
        recipient = "npn25@cornell.edu"
        body = "\n".join(all_errors)
        email_msg = f"To: {recipient}\nSubject: {subject}\n\n{body}"
        try:
            with subprocess.Popen(["/usr/sbin/sendmail", recipient], stdin=subprocess.PIPE) as proc:
                proc.communicate(email_msg.encode())
        except Exception as e:
            print(f"[WARN] Could not send email via sendmail: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automate density analysis with multiprocessing")
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-n', '--nprocs', type=int, default=1)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    main(args.input, args.output, args.nprocs, args.stride)
