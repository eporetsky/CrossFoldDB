#!/bin/bash
date                          #optional, prints out timestamp at the start of the job in stdout file

echo "Started at: $(date)"

export PATH=$(pwd)/foldseek/bin/:$PATH

species=$1
REVERSE=$2     #forward\reverse
input="species_list.txt"
REFERENCE="flavus"
HOME="$(pwd)/"

mkdir ./html/${species}
python ./python/foldseek_search_parallel.py $input $species $REFERENCE $HOME $REVERSE

# Optional: print timestamp when the script ends
echo "Finished at: $(date)"
