# Alcohol Amination: Trends and Correlations Analysis

Supporting code and data for the article:

> **Advances in alcohols amination using amines or nitroarenes – comprehensive analysis of trends and correlations of various reaction parameters**
> Andrey S. Kozlov, Mikhail A. Losev, Oleg I. Afanasyev,\* Denis A. Chusov\*

This repository contains the Jupyter notebook and helper functions used to analyze literature data on borrowing hydrogen (BH) amination of alcohols with amines and on amination of alcohols with nitroarenes, and to generate the figures and consolidated tables presented in the paper.

## Repository structure

```
├── trends_hb_nitro.ipynb    # Main analysis notebook
├── plotting_functions.py    # Helper module (plots, tables, formatting)
├── base_data/               # Literature datasets (tab-separated CSV)
│   ├── PhNH2_BnOH.csv       # PhNH2 + BnOH reaction, incl. optimization data
│   ├── PhNO2_BnOH.csv       # PhNO2 + BnOH reaction, incl. optimization data
│   ├── substrates.csv       # Substrate scope data (amines and nitro compounds)
│   └── MeOH.csv             # N-Methylation with MeOH
└── doc_tables/              # Output folder for generated .docx tables
```

## What the notebook does

`trends_hb_nitro.ipynb` is organized in two main parts:

**1. Borrowing hydrogen amination (amines + alcohols)**
- Catalyst activity classification by TON (low < 100 ≤ medium < 500 ≤ active) and metal usage statistics (full dataset vs. publications since 2022)
- Comparison of metal-catalyzed vs. transition-metal-free reactions: bases, solvents, base/alcohol ratios, temperatures
- pKa–temperature "landscape" for base-mediated (catalyst-free) amination
- Detailed analysis of the model PhNH₂ + BnOH reaction: base success rates, base/metal vs. temperature correlation maps, solvent dielectric constant vs. success rate
- Substrate-type trends (amides, heteroaromatic, aromatic, aliphatic amines)

**2. Amination with nitro compounds**
- Same type of analysis for ArNO₂/AlkNO₂/HetNO₂ substrates (reductive H₂ atmospheres excluded)
- PhNO₂ + BnOH model reaction and substrate scope analysis
- N-Methylation with MeOH as a separate case

For each part the notebook also builds consolidated "metal leaders" tables (max TON, lowest working temperature, base-free performance, most popular working bases per metal) and exports them to Word documents in `doc_tables/`.

**Key convention:** throughout the analysis a reaction is considered *successful* if the yield exceeds **65%**.

`plotting_functions.py` provides the reusable helpers: correlation/difference maps (`plot_diff_graph`, `d3_diagram`), paired pie charts (`compare_pie`), chemical formula formatting for labels (`to_chem`), a solvent dielectric constant lookup, and .docx table export.

## Requirements

Python 3.12+ (f-strings with nested quotes are used) with:

```
pandas, numpy, matplotlib, seaborn, scipy, adjustText, rdkit, python-docx, tqdm
```

```bash
pip install pandas numpy matplotlib seaborn scipy adjustText rdkit python-docx tqdm
```

## Usage

1. Place the datasets in `base_data/` (as in this repository).
2. Run `trends_hb_nitro.ipynb` from top to bottom.
3. Figures are rendered inline; consolidated tables are saved to `doc_tables/`.

## Citation

If you use this code or data, please cite the article above.
