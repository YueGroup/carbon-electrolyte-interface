import numpy as np
import matplotlib.pyplot as plt
import MDAnalysis as mda
import os

nbins = 200
cut = 10.0  # +/- range in Å around COM
dt_fs = 1.0
dump_interval = 1000
frame_spacing_ps = dump_interval * dt_fs / 1000.0

zmin = -cut
zmax = +cut
edges = np.linspace(zmin, zmax, nbins + 1)
binwidth = edges[1] - edges[0]
centers = 0.5 * (edges[:-1] + edges[1:])

mw_dict = {'water': 18.01528, 'na': 22.989769, 'cl': 35.453}
species_info = {'water': 'type 1', 'cl': 'type 3', 'na': 'type 4'}

def compute_density_profile(file_path, species, atom_type, skip_frame=0, stride=1):
    u = mda.Universe(file_path, format='LAMMPSDUMP', timeunit='ps', dt=frame_spacing_ps)
    u.transfer_to_memory()

    atoms = u.select_atoms(atom_type)
    if atoms.n_atoms == 0:
        raise ValueError(f"No atoms found for {species} in {file_path}")

    hist_total = np.zeros(nbins)
    nframes = 0
    for ts in u.trajectory[skip_frame::stride]:
        com_z = atoms.center_of_mass()[2]
        lz = ts.dimensions[2]
        z_pos = atoms.positions[:, 2]
        z_pos = np.where(z_pos < 0.0, z_pos + lz, z_pos)
        z_pos = np.where(z_pos > lz, z_pos - lz, z_pos)
        z_shifted = z_pos - com_z
        z_shifted = np.where(z_shifted < -lz/2.0, z_shifted + lz, z_shifted)
        z_shifted = np.where(z_shifted > +lz/2.0, z_shifted - lz, z_shifted)
        mask = (z_shifted >= zmin) & (z_shifted <= zmax)
        hist, _ = np.histogram(z_shifted[mask], bins=edges)
        hist_total += hist
        nframes += 1

    if nframes == 0:
        raise ValueError(f"No valid frames for {species} in {file_path}")

    lx = u.trajectory[0].dimensions[0]
    ly = u.trajectory[0].dimensions[1]
    volume_per_bin = lx * ly * binwidth * 1e-24  # cm³
    density_profile = (hist_total / nframes) / volume_per_bin * mw_dict[species] / 6.022e23
    return centers, density_profile

def analyze_density(file_path, species, atom_type, out_prefix, output_folder, stride=1):
    centers, density_profile = compute_density_profile(file_path, species, atom_type, stride=stride)
    out_data = os.path.join(output_folder, f"density_{species}_{out_prefix}.dat")
    np.savetxt(out_data, np.column_stack([centers, density_profile]), header='z (A), density (g/cm^3)')
    print(f"[DONE] {species} → {out_data}")
    return centers, density_profile
