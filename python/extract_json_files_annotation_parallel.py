#!/usr/bin/env python3
import sys
import os
import json
import re
import csv
import argparse

# Regex to capture the UniProt ID within "AF-XXXX-F1-model_v4"
UNIPROT_PATTERN = re.compile(r"^AF-(.*?)-F1-model_v4$")

def extract_uniprot_id(value):
    """
    If 'value' matches 'AF-<UNIPROT>-F1-model_v4', return '<UNIPROT>'.
    Otherwise, return the original string unchanged.
    """
    match = UNIPROT_PATTERN.match(value)
    if match:
        return match.group(1)
    return value

def create_entry_protein_dict(tsv_filename):
    """
    Reads a TSV file with headers: "Entry", "Gene Names",
    "Gene Names (ORF)", and "Protein names".
    Returns a dictionary where keys are the "Entry" column
    and values are the "Protein names" column.
    """
    entry_protein_dict = {}
    with open(tsv_filename, mode='r', encoding='utf-8') as file:
        # Use DictReader to handle header-based indexing and tab-delimited data
        reader = csv.DictReader(file, delimiter='\t')

        for row in reader:
            # Get the required columns from the current row
            entry = row.get("Entry", "").strip()
            protein_names = row.get("Protein names", "").strip()

            if entry and protein_names:
                entry_protein_dict[entry] = protein_names

    return entry_protein_dict

def process_html_file(input_file, species_name, tsv_dict):
    """
    Processes a single HTML file to extract and modify JSON data,
    and removes any alignment where target == accession.
    """
    # Read the entire HTML file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read file '{input_file}': {e}")
        return

    # Find start of the JSON
    start_index = content.find('[{"query"')
    if start_index == -1:
        print(f"ERROR: JSON start not found in '{input_file}'.")
        return

    json_str = content[start_index:].strip().splitlines()
    if json_str and json_str[-1].strip() == "</div>":
        json_str.pop()
    json_str = "\n".join(json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failed in '{input_file}': {e}")
        return

    for record in data:
        # pull out original alignments
        raw_alignments = []
        if "results" in record and record["results"]:
            raw_alignments = record["results"][0].get("alignments", [])
        # drop the old results
        record.pop("results", None)

        # rename in query header
        if "query" in record:
            q = record["query"]
            if "qCa" in q:
                q["qca"] = q.pop("qCa")
            if "header" in q:
                q["accession"] = extract_uniprot_id(q.pop("header"))

        # store accession for filtering
        accession = record["query"].get("accession", "")

        # build new, filtered list
        new_alignments = []
        for aln in raw_alignments:
            # rename fields
            if "tCa" in aln:
                aln["tca"] = aln.pop("tCa")
            if "alnLength" in aln:
                aln["alnLen"] = aln.pop("alnLength")
            if "tSeq" in aln:
                aln["tseq"] = aln.pop("tSeq")

            # extract and fix target ID
            if "target" in aln:
                aln["target"] = extract_uniprot_id(aln["target"])

            # skip if this alignment is self-to-self
            if aln.get("target") == accession:
                continue

            # fill in species/annotation
            desc = tsv_dict.get(aln["target"], "N/A")
            aln["species"]    = species_name
            aln["annotation"] = desc

            new_alignments.append(aln)

        # replace with filtered list
        record["alignments"] = new_alignments

    # write out cleaned JSON…
    base = os.path.splitext(os.path.basename(input_file))[0]
    outdir = os.path.join(os.path.dirname(input_file), "JSON")
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, base + ".json")

    try:
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(data, out, indent=2)
        print(f"Wrote filtered JSON to: {out_path}")
    except Exception as e:
        print(f"ERROR: could not write JSON '{out_path}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Process HTML files in a directory to extract and modify JSON data.")
    parser.add_argument("input_directory", help="Path to the input directory containing .html files.")
    parser.add_argument("species_name", help="Name of the species.")
    parser.add_argument("tsv_filename", help="Path to the TSV annotation file.")

    args = parser.parse_args()

    input_directory = args.input_directory
    species_name = args.species_name
    tsv_filename = args.tsv_filename

    # Validate input directory
    if not os.path.isdir(input_directory):
        print(f"ERROR: Input directory '{input_directory}' does not exist or is not a directory.")
        sys.exit(1)

    # Validate TSV file
    if not os.path.isfile(tsv_filename):
        print(f"ERROR: TSV file '{tsv_filename}' does not exist.")
        sys.exit(1)

    # Create the annotation dictionary
    result_dict = create_entry_protein_dict(tsv_filename)

    if not result_dict:
        print(f"WARNING: No valid entries found in TSV file '{tsv_filename}'. Proceeding with empty annotations.")

    # Iterate through each .html file in the input directory
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(".html"):
                html_file_path = os.path.join(root, file)
                print(f"Processing file: {html_file_path}")
                process_html_file(html_file_path, species_name, result_dict)

    print("All HTML files have been processed.")

if __name__ == "__main__":
    main()
