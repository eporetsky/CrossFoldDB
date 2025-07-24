#!/bin/bash
#SBATCH --account=your_account_name
#SBATCH --partition=your_partition_name
#SBATCH --job-name="S4"         #name of this job
#SBATCH -N1                             #number of nodes
#SBATCH -n1                             #number of cores
#SBATCH --mem=200GB             #number of memory
#SBATCH --ntasks=1              #number of nodes
#SBATCH --cpus-per-task=48      #number of cores
#SBATCH -t 2-00:00:00                   #maximum runtime
#SBATCH -o "./log/stdout.%j.%N"         # standard output
#SBATCH -e "./log/stderr.%j.%N"         #standard error

# Print timestamp
date

species_list_path="species_list.txt"
reference="wheat"
top_x="10"
cutoff="0.0001"

mkdir ./alignments/

# Execute the Python script
python ./python/merge_JSON_alignments.py $species_list_path $reference $top_x $cutoff

# Print completion timestamp
date
