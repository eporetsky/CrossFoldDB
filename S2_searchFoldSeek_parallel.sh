#!/bin/bash
#SBATCH --account=your_account_name
#SBATCH --partition=your_partition_name
#SBATCH --job-name="S2"         #name of this job
#SBATCH -N1                             #number of nodes
#SBATCH -n1                             #number of cores
#SBATCH --mem=200GB             #number of memory
#SBATCH --ntasks=1              #number of nodes
#SBATCH --cpus-per-task=48      #number of cores
#SBATCH -t 2-00:00:00                   #maximum runtime
#SBATCH -o "./log/stdout.%j.%N"         # standard output
#SBATCH -e "./log/stderr.%j.%N"         #standard error

date                          #optional, prints out timestamp at the start of the job in stdout file

echo "Started at: $(date)"

#export PATH=$(pwd)/foldseek/bin/:$PATH

species=$2
REVERSE=$3     #forward\reverse
input="species_list.txt"
REFERENCE=$1
HOME="$(pwd)/"

mkdir ./html/${species}
python ./python/foldseek_search_parallel.py $input $species $REFERENCE $HOME $REVERSE

# Optional: print timestamp when the script ends
echo "Finished at: $(date)"
