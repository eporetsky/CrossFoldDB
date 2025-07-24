#!/bin/bash
#SBATCH --account=your_account_name
#SBATCH --partition=your_partition_name
#SBATCH --job-name="S5"         #name of this job
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

reference=$1
species=$2

reference="${reference//\"/}"
reference="${reference//“/}"
reference="${reference//”/}"

species="${species//\"/}"
species="${species//“/}"
species="${species//”/}"



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
