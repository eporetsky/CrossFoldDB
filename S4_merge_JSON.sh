#!/bin/bash

# Print timestamp
date

species_list_path="species_list.txt"
reference="flavus"
top_x="10"
cutoff="0.0001"

mkdir ./alignments/

# Execute the Python script
python ./python/merge_JSON_alignments.py $species_list_path $reference $top_x $cutoff

# Print completion timestamp
date
