# Figures

This folder contains all finalized figures and their corresponding plotting scripts used in the manuscript and Supporting Information for the graphene–electrolyte interface study.

## Structure

Each subfolder corresponds to a specific figure and contains:
- Final panel figure in PDF format (e.g., `fig3_water_27nacl_200bins.pdf`)
- Plotting script (e.g., `plot_dens_fig3.py`) used to generate the full figure or panel
- Intermediate individual subplots used to assemble the figure

Example:
```
figures/
├── Fig3_1x4/
│   ├── fig3_water_0nacl_200bins.pdf
│   ├── fig3_water_18nacl_200bins.pdf
│   ├── ...
│   └── plot_dens_fig3.py
├── Fig4_2x4/
│   ├── ...
```

## Plotting Standards

- All figures are generated using Python (matplotlib)
- Vector output (`.pdf`) for publication quality
- Helvetica font, no gridlines, inward-pointing ticks
- Axis labels include physical units
- Shaded regions represent the standard deviation across three independent simulations
- Colors encode surface coverage and functional group identity

## Reproducibility

To regenerate a figure, navigate to the corresponding subfolder and run the associated script:
```bash
python plot_<figure>.py
```
Ensure that the required `.csv` or data files obtained from simulation post-procesing are present or correctly referenced in the script.

## Contact

For figure scripts and questions, please contact: **npn25@cornell.edu**
