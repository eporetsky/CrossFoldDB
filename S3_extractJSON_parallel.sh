#!/bin/bash
#SBATCH --account=your_account_name
#SBATCH --partition=your_partition_name
#SBATCH --job-name="S3"         #name of this job
#SBATCH -N1                             #number of nodes
#SBATCH -n1                             #number of cores
#SBATCH --mem=200GB             #number of memory
#SBATCH --ntasks=1              #number of nodes
#SBATCH --cpus-per-task=48      #number of cores
#SBATCH -t 2-00:00:00                   #maximum runtime
#SBATCH -o "./log/stdout.%j.%N"         # standard output
#SBATCH -e "./log/stderr.%j.%N"         #standard error


date                          #optional, prints out timestamp at the start of the job in stdout file

# ===============================================
# Script Name: submit_species_jobs.sh
# Description: Reads a TSV file and submits a Slurm job for each row.
# Usage: ./submit_species_jobs.sh
# ===============================================

# Exit immediately if a command exits with a non-zero status
set -e

module load miniconda3
eval "$(conda shell.bash hook)"
conda activate ~/.conda/envs/crossfolddb

# -------------------------------
# Configuration
# -------------------------------

# Path to the input TSV file
INPUT_FILE="species_list.txt"
#INPUT_FILE="species_list_graminearum.txt"
#INPUT_FILE="species_list_graminearum.txt"
REFERENCE="wheat"

# Path to the Slurm job script template
JOB_SCRIPT="process_species_job.sh"

# Directory to store logs
LOG_DIR="./log"

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# -------------------------------
# Function Definitions
# -------------------------------

# Function to display error messages
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Function to trim leading and trailing whitespace
trim() {
    local var="$*"
    # Remove leading whitespace
    var="${var#"${var%%[![:space:]]*}"}"
    # Remove trailing whitespace
    var="${var%"${var##*[![:space:]]}"}"
    echo -n "$var"
}

# -------------------------------
# Preliminary Checks
# -------------------------------

# Check if the input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    error_exit "Input file '$INPUT_FILE' not found."
fi

# Check if the job script exists and is executable
if [[ ! -f "$JOB_SCRIPT" ]]; then
    error_exit "Job script '$JOB_SCRIPT' not found."
fi

# Make the job script executable
chmod +x "$JOB_SCRIPT"

# -------------------------------
# Processing the TSV File
# -------------------------------

# Read the TSV file line by line, skipping the header
tail -n +2 "$INPUT_FILE" | while IFS=$'\t' read -r Species HTML DB CIF Annotation UniProtID SpeciesID; do
    # Trim whitespace from variables
    Species=$(trim "$Species")
    HTML=$(trim "$HTML")
    Annotation=$(trim "$Annotation")

    # Define the HTML directory based on the Species
    HTML_DIR="./html/${Species}"

    # Check if the HTML directory exists
    if [[ ! -d "$HTML_DIR" ]]; then
        echo "Warning: HTML directory '$HTML_DIR' does not exist. Skipping Species '$Species'."
        continue
    fi

    # Check if the Annotation file exists
    if [[ ! -f "$Annotation" ]]; then
        echo "Warning: Annotation file '$Annotation' does not exist. Skipping Species '$Species'."
        continue
    fi

    # Find all HTML files in the HTML directory
    # Assuming HTML files have a specific extension, e.g., .html; adjust as needed
    # If HTML files have different extensions, modify the pattern accordingly
    # For example, use "$HTML_DIR"/*.html
    HTML_FILES=("$HTML_DIR"/*)

    # Check if there are any HTML files
    if [[ ! -e "${HTML_FILES[0]}" ]]; then
        echo "Warning: No HTML files found in '$HTML_DIR'. Skipping Species '$Species'."
        continue
    fi

    # Iterate over each HTML file
    #for HTML_FILE in "${HTML_FILES[@]}"; do
        # Check if it's a regular file
        #if [[ -f "$HTML_FILE" ]]; then
           echo "Submitting job for file: '$HTML_DIR' for Species: '$Species' with Annotation: '$Annotation'"

            # Submit the Slurm job with environment variables
            sbatch --export=SPECIES="$Species",HTML_FILE="$HTML_DIR",ANNOTATION_FILE="$Annotation" "$JOB_SCRIPT"

            # Optional: Add a delay to prevent overwhelming the scheduler
            # sleep 0.1
    #    fi
    #done

done

echo "All jobs submitted."
