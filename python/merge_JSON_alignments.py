#!/usr/bin/env python3

import sys
import os
import json
import re
import csv
from pathlib import Path
from collections import defaultdict

# -------------------------------
# Constants and Patterns
# -------------------------------

# Regex to remove known extensions
REMOVE_EXT_PATTERN = re.compile(r'(\.cif\.gz|\.pdb\.gz|\.json\.gz)$', re.IGNORECASE)

# Regex to extract UniProt ID from filename
UNIPROT_PATTERN = re.compile(r'^AF-(.*?)-F1-model_v4', re.IGNORECASE)

# -------------------------------
# Function Definitions
# -------------------------------

def extract_uniprot_id(filename):
    """
    Extracts the UniProt ID from a given filename using a regex pattern.

    Parameters:
        filename (str): The basename of the file.

    Returns:
        str or None: The extracted UniProt ID if pattern matches; otherwise, None.
    """
    basename_noext = REMOVE_EXT_PATTERN.sub('', filename)
    match = UNIPROT_PATTERN.match(basename_noext)
    if match:
        return match.group(1)
    return basename_noext

def extract_uniprot_id_pdb(filename):
    """
    Returns the basename (no directory, no extension) of the given filename.

    Parameters:
        filename (str): The name or path of the file (e.g. "A010FDG.pdb" or "/path/to/A010FDG.pdb").

    Returns:
        str: The filename without its extension (e.g. "A010FDG").
    """
    # strip any leading path, then split off the extension
    base = os.path.basename(filename)
    name, _ext = os.path.splitext(base)
    return name


def read_species_list(species_list_path):
    """
    Reads the species list TSV file and returns a list of species information.

    Parameters:
        species_list_path (str): Path to the species_list.txt TSV file.

    Returns:
        list of dict: Each dict contains information about a species.
    """
    species_list = []
    try:
        with open(species_list_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                # Clean and store relevant fields
                species_info = {
                    'Species': row.get('Species', '').strip(),
                    'HTML': row.get('HTML', '').strip(),
                    'DB': row.get('DB', '').strip(),
                    'CIF': row.get('CIF', '').strip(),
                    'Annotation': row.get('Annotation', '').strip(),
                    'UniProtID': row.get('UniProtID', '').strip(),
                    'SpeciesID': row.get('SpeciesID', '').strip()
                }
                species_list.append(species_info)
    except Exception as e:
        print(f"ERROR: Failed to read species list file '{species_list_path}': {e}")
        sys.exit(1)

    return species_list

def collect_uniprot_ids(reference_dir):
    """
    Collects all unique UniProt IDs from .cif.gz files in the given reference directory.

    Parameters:
        reference_dir (str): Path to the ./structures/${REFERENCE}/ directory.

    Returns:
        set: A set of unique UniProt IDs extracted from filenames.
    """
    uniprot_ids = set()
    structures_path = Path(reference_dir)

    if not structures_path.is_dir():
        print(f"ERROR: Reference directory '{reference_dir}' does not exist or is not a directory.")
        sys.exit(1)

    for cif_gz_file in structures_path.glob('*.cif.gz'):
        uniprot_id = extract_uniprot_id(cif_gz_file.name)
        if uniprot_id:
            uniprot_ids.add(uniprot_id)
        else:
            print(f"WARNING: Could not extract UniProt ID from filename '{cif_gz_file.name}'. Skipping.")

    for pdb_file in structures_path.glob('*.pdb'):
        uniprot_id = extract_uniprot_id_pdb(pdb_file.name)
        if uniprot_id:
            uniprot_ids.add(uniprot_id)
        else:
            print(f"WARNING: Could not extract UniProt ID from filename '{cif_gz_file.name}'. Skipping.")


    return uniprot_ids

def merge_alignments_for_uniprot(uniprot_id, species_list, top_x, cutoff_value):
    """
    Merges alignments from multiple JSON files corresponding to a UniProt ID across different species.

    Parameters:
        uniprot_id (str): The UniProt ID to process.
        species_list (list of dict): List of species information.
        top_x (int): Number of top alignments to keep.
        cutoff_value (float): Maximum allowable 'eval' value for alignments to be included.

    Returns:
        dict or None: Merged JSON data with 'query' and 'alignments', or None if no data found.
    """
    merged_alignments = []
    query_info = None
    species_found = 0  # Counter to check if any species has the JSON file

    for species in species_list:
        species_name = species['Species']
        html_dir = species['HTML']
        json_file_path = Path(html_dir) / 'JSON' / f"{uniprot_id}.json"

        if not json_file_path.is_file():
            json_file_path_save = json_file_path
            json_file_path = Path(html_dir) / 'JSON' / f"{uniprot_id}.pdb.json"

        if not json_file_path.is_file():
            print(f"WARNING: JSON file '{json_file_path_save }' or  '{json_file_path}' were not found for species '{species_name}'. Skipping.")
            continue

        species_found += 1

        try:
            with open(json_file_path, 'r', encoding='utf-8') as jf:
                json_data = json.load(jf)

                if not isinstance(json_data, list) or len(json_data) == 0:
                    print(f"WARNING: JSON file '{json_file_path}' is empty or not a list. Skipping.")
                    continue

                # Assuming the first entry contains the 'query' information
                if query_info is None:
                    query_info = json_data[0].get('query', {})

                # Extract 'alignments' from the JSON
                for record in json_data:
                    alignments = record.get('alignments', [])
                    if isinstance(alignments, list):
                        merged_alignments.extend(alignments)
        except json.JSONDecodeError as jde:
            print(f"ERROR: JSON decoding failed for file '{json_file_path}': {jde}")
            continue
        except Exception as e:
            print(f"ERROR: Failed to process JSON file '{json_file_path}': {e}")
            continue

    if species_found == 0:
        print(f"WARNING: No JSON files found for UniProt ID '{uniprot_id}'. Skipping.")
        return None

    if not query_info:
        print(f"WARNING: No 'query' information found for UniProt ID '{uniprot_id}'. Skipping.")
        return None

    if not merged_alignments:
        print(f"WARNING: No 'alignments' found for UniProt ID '{uniprot_id}'.")

    # Filter alignments by 'eval' <= cutoff_value
    filtered_alignments = [
        aln for aln in merged_alignments
        if isinstance(aln.get('eval', None), (int, float)) and aln['eval'] <= cutoff_value
    ]

    if not filtered_alignments:
        print(f"WARNING: No alignments passed the 'eval' cutoff for UniProt ID '{uniprot_id}'.")
        return None

    # Sort the filtered alignments by 'eval' in ascending order
    sorted_alignments = sorted(
        filtered_alignments,
        key=lambda x: x.get('eval', float('inf'))
    )

    # Keep only the top X alignments
    top_alignments = sorted_alignments[:top_x]

    merged_json = {
        'query': query_info,
        'alignments': top_alignments
    }

    return merged_json

def save_master_json(uniprot_id, merged_data, reference):
    """
    Saves the merged JSON data to the designated output directory.

    Parameters:
        uniprot_id (str): The UniProt ID being processed.
        merged_data (dict): The merged JSON data containing 'query' and 'alignments'.
        reference (str): The reference name used to determine output directory.

    Returns:
        None
    """
    output_dir = Path(f"./alignments/{reference}_alignments")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{uniprot_id}.json"

    try:
        with open(output_file, 'w', encoding='utf-8') as of:
            json.dump(merged_data, of, indent=2)
        print(f"INFO: Master JSON saved to '{output_file}'.")
    except Exception as e:
        print(f"ERROR: Failed to write master JSON to '{output_file}': {e}")

# -------------------------------
# Main Execution
# -------------------------------

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) < 5:
        print("Usage: python merge_alignments.py <species_list.txt> <REFERENCE> <top_x> <cutoff_value>")
        sys.exit(1)

    # Parse command-line arguments
    species_list_path = sys.argv[1]
    reference = sys.argv[2]

    # Convert 'top_x' to integer with error handling
    try:
        top_x = int(sys.argv[3])
        if top_x <= 0:
            raise ValueError("The 'top_x' argument must be a positive integer.")
    except ValueError as ve:
        print(f"ERROR: {ve}")
        print("Usage: python merge_alignments.py <species_list.txt> <REFERENCE> <top_x> <cutoff_value>")
        sys.exit(1)

    # Convert 'cutoff_value' to float with error handling
    try:
        cutoff_value = float(sys.argv[4])
        if cutoff_value < 0:
            raise ValueError("The 'cutoff_value' argument must be a non-negative float.")
    except ValueError as ve:
        print(f"ERROR: {ve}")
        print("Usage: python merge_alignments.py <species_list.txt> <REFERENCE> <top_x> <cutoff_value>")
        sys.exit(1)

    print(f"INFO: Reading species list from '{species_list_path}'.")
    species_list = read_species_list(species_list_path)

    print(f"INFO: Collecting UniProt IDs from './structures/{reference}/'.")
    reference_sub = f"{reference}/"
    reference_dir = os.path.join('.', 'structures', reference_sub)
    uniprot_ids = collect_uniprot_ids(reference_dir)
    print(f"INFO: Found {len(uniprot_ids)} unique UniProt IDs.")

    # Create output directory if it doesn't exist
    output_master_dir = Path(f"./JSON_{reference}")
    output_master_dir.mkdir(parents=True, exist_ok=True)

    # Process each UniProt ID
    for uniprot_id in sorted(uniprot_ids):
        print(f"\nINFO: Processing UniProt ID '{uniprot_id}'.")
        merged_data = merge_alignments_for_uniprot(uniprot_id, species_list, top_x, cutoff_value)
        if merged_data:
            save_master_json(uniprot_id, merged_data, reference)
        else:
            print(f"WARNING: No data merged for UniProt ID '{uniprot_id}'. Skipping saving.")

    print("\nINFO: All UniProt IDs have been processed.")

if __name__ == "__main__":
    main()
