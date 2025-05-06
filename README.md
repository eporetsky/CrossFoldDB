# 🧬 CrossFoldDB
**CrossFoldDB** is a framework for performing and storing precomputed **FoldSeek protein structure alignments** across related species and reference outgroups. 

---

## 🔍 Key Features

- Precomputed all-vs-all structure-based protein alignments using FoldSeek
- Forward and reverse queries to ensure completeness
- Custom annotation integration from UniProt and genome metadata
- Supports large-scale parallel searches on HPC
- JSON conversion pipeline for downstream visualization and filtering

---

## 🧪 Use Case Examples

### 🦠 *Aspergillus flavus*

Structure-based homology to *Arabidopsis* and *S. cerevisiae* enables identification of conserved domains in potential mycotoxin biosynthesis proteins. Outgroup filtering helps isolate fungal-specific innovations.

### 🌿 *Arabidopsis thaliana*

Used as a reference outgroup to identify structurally novel effectors in *Fusarium graminearum*. Matches to host immune proteins provide insight into possible host mimicry.

---

## 📁 Directory Structure


```text
<pre><code>
CrossFoldDB/
├── structures/ # Compressed AlphaFold/CIF inputs per species
│ └── <species>/
├── DB/ # FoldSeek formatted searchable databases
│ └── <species>DB/
├── html/ # Output HTML with alignment summaries
├── JSON/ # Parsed JSON results (post-filtered)
├── scripts/ # bash scripts
|   ├── species_list.txt # List of species to include in pipeline
|   ├── S1_buildFoldSeekDB.sh # Build script for FoldSeek databases
|   ├── S2_searchFoldSeek_parallel.sh # Parallel search script (forward/reverse)
|   ├── S3_extractJSON_parallel.sh # Convert FoldSeek results to legacy format
|   ├── S4_merge_JSON.sh # Combine and filter results
|   ├── S5_make_annotations.sh # Add annotations for reference proteins
|   ├── untar_directory.sh # Utility to unzip input CIFs in parallel
├── python/ # python scripts
|   ├──
└── README.md
```


---

## 🧰 Installation

Requirements:

- [FoldSeek](https://github.com/steineggerlab/foldseek)
- Python 3.8+
- SLURM-based HPC environment with `sbatch`

---

## 🚀 Quickstart

### 1. Unpack structure files

```bash
sbatch untar_directory.sh ./structures/arabidopsis
sbatch untar_directory.sh ./structures/graminearum
sbatch untar_directory.sh ./structures/cerevisiae
sbatch untar_directory.sh ./structures/sorghi
sbatch untar_directory.sh ./structures/bombycis
sbatch untar_directory.sh ./structures/candidus
sbatch untar_directory.sh ./structures/flavus
sbatch untar_directory.sh ./structures/hiratsukae
sbatch untar_directory.sh ./structures/parasiticus
sbatch untar_directory.sh ./structures/ruber
```

### 2. Create a species list
```bash
```


### 3. Build FoldSeek databases

### 4. Run FoldSeek searches (forward and reverse)
Repeat forward and reverse searches for each species. Continue until the number of output JSON files stabilizes (≈ number of reference structures).
```bash
```

### 5. Convert JSON results to legacy format
```bash
```

### 6. Merge and filter JSON outputs
```bash
```

### 7. Generate reference annotations (optional)
```bash
```


