#!/bin/bash

# Print timestamp
date

reference="flavus"
species="Aspergillus flavus"
tsv_file="./annotation/${reference}.tsv"
base_dir="./metadata/${reference}_json/"
output_dir="./metadata/${reference}_json/unitprot/"
gene_dir="./metadata/${reference}_json/alias/"

mkdir $base_dir
mkdir $output_dir
mkdir $gene_dir

# Execute the Python script
python ./python/create_reference_annotation_files.py $tsv_file $output_dir $gene_dir "$species"

# Print completion timestamp
date
