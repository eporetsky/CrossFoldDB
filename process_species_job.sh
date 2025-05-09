#!/bin/bash

# Load necessary modules or activate environments if needed
# module load python/3.8  # Example: Uncomment and modify if using modules
# source ~/myenv/bin/activate  # Example: Uncomment if using a Python virtual environment

# Print timestamp
date
echo "Starting job for Species: $SPECIES"

# Execute the Python script
python ./python/extract_json_files_annotation_parallel.py "$HTML_FILE" "$SPECIES" "$ANNOTATION_FILE"

# Print completion timestamp
echo "Completed job for Species: $SPECIES"
date
