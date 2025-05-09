#!/bin/bash

date                          #optional, prints out timestamp at the start of the job in stdout file

# 1. Check that a directory name was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# 2. Move into the specified directory
cd "$1" || {
  echo "Failed to enter directory: $1"
  exit 1
}

# 3. Loop through all .tar files and extract them
for tar_file in *.tar.gz; do
  # Skip if no .tar files are found
  [ -e "$tar_file" ] || continue

  echo "Extracting: $tar_file"
  tar -xzf "${tar_file}"
done

# 4. Remove all .json.gz files
rm -f *.json.gz

# 5. Print the directory name
echo "Directory: $1"

# 6. Print the result of ls *.cif.gz | wc
#    This will output three numbers: (lines, words, characters).
#    If you only want the number of files, you could do `ls *.cif.gz | wc -l`
echo "CIF"
ls *.cif* | wc -l
echo "PDB"
ls *.pdb* | wc -l
