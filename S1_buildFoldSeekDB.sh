#!/bin/bash
#SBATCH --account=your_account_name
#SBATCH --partition=your_partition_name
#SBATCH --job-name="S1"   	    #name of this job
#SBATCH -N1                  		#number of nodes
#SBATCH -n1                  		#number of cores
#SBATCH --mem=200GB           	#number of memory
#SBATCH --ntasks=1              #number of nodes
#SBATCH --cpus-per-task=48	    #number of cores
#SBATCH -t 2-00:00:00         		#maximum runtime
#SBATCH -o "./log/stdout.%j.%N" 	# standard output
#SBATCH -e "./log/stderr.%j.%N" 	#standard error


#!/bin/bash
date                          #optional, prints out timestamp at the start of the job in stdout file

#!/usr/bin/env bash
# 1) Setup
set -euo pipefail

# 2) Make sure the input file is really there
input="species_list.txt"
if [[ ! -f "$input" ]]; then
  echo "ERROR: '$input' not found in $(pwd)" >&2
  exit 1
fi

# 3) Now add foldseek to your PATH
#export PATH="$(pwd)/foldseek/bin/:$PATH"

# 4) Extract Structure & DB columns and loop
awk -F $'\t' '
  NR==1 {
    for (i=1; i<=NF; i++) {
      if ($i=="Structure") s=i
      if ($i=="DB")        d=i
    }
    if (!s || !d) {
      print "ERROR: header must contain Structure and DB" > "/dev/stderr"
      exit 1
    }
    next
  }
  { print $s, $d }
' "$input" | while IFS=$'\t' read -r structure_name DB_name; do
  echo "foldseek createdb ${structure_name} ${DB_name}"
  foldseek createdb $structure_name $DB_name
done

# 5) Timestamp
date
