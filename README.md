# Carbon–Electrolyte Interface Toolkit

This repository contains molecular simulation inputs, analysis scripts, and data processing tools used in:

**“Tuning Interfacial Electrolyte Structure and Dynamics via Surface Functionalization of Graphene”**  
Lyndon Hess, Nhi P.T. Nguyen, et al.  
Cornell University

---

## 🔬 Project Overview

This study explores how chemical functionalization of graphene surfaces modulates the structure and dynamics of confined aqueous NaCl electrolytes. Using molecular dynamics (MD) simulations, we investigate a matrix of functional group types (–COOH, –OH, =O, –CH₃), surface coverages, and NaCl concentrations.

We also introduce [`carbonstructures`](https://github.com/YueGroup/carbonstructures), an open-source Python tool developed to generate functionalized graphene structures for simulation.

---

## 📁 Repository Structure

```
carbon-electrolyte-interface/
├── simulation/       # LAMMPS input scripts and run templates
├── analysis/         # Python scripts to analyze trajectories
├── figures/          # Publication-ready figures
├── requirements.txt  # Python dependencies for analysis
├── .gitignore        # Ignored files (e.g., dumps, logs)
└── README.md         # This file
```

---

## 📦 Dependencies

### Python environment setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Additional tool used:  
🔗 [`carbonstructures`](https://github.com/YueGroup/carbonstructures)

> This external package was used to build functionalized graphene surfaces. Clone and install from its own repository if needed.

---

## 🚀 Usage

### 1. Structure Generation
Use [`carbonstructures`](https://github.com/YueGroup/carbonstructures) to generate graphene sheets with desired functional groups and coverage.

### 2. Simulation
Use the files in `simulation/` to run LAMMPS MD simulations. Example job scripts are provided for HPC environments.

### 3. Analysis
Run scripts in `analysis/` to compute:
- Water and ion density profiles
- Interfacial and bulk diffusion coefficients
- Figure generation (e.g., heatmaps, line plots)

---

## 📊 Figures

All plots shown in the manuscript are available in `figures/`. Each figure corresponds to a panel in the Results & Discussion section. See `figures/README.md` for descriptions.

---

## 📄 License

This repository is released under the **MIT License**. See `LICENSE` file for details.

---

## 🧠 Citation & Data Availability

If you use this toolkit or structure generation method in your work, please cite:

> Hess, Nguyen, et al. *Tuning Interfacial Electrolyte Structure and Dynamics via Surface Functionalization of Graphene*. 2025.

All data and scripts are available via this GitHub repository. For questions, contact:

📧 [shuwen.yue@cornell.edu](mailto:shuwen.yue@cornell.edu)
