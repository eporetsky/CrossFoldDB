import sys
import os
import csv
import json

def main():
    # Check for proper usage
    #if len(sys.argv) != 4:
    #    print(f"Usage: {sys.argv[0]} <tsv_file> <output_directory> <species>")
    #    sys.exit(1)

    # Parse arguments
    tsv_file = sys.argv[1]
    output_dir = sys.argv[2]
    gene_dir = sys.argv[3]
    species = sys.argv[4]

    print(tsv_file,output_dir,gene_dir,species)
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the TSV file
    with open(tsv_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')

        # Ensure the required columns exist
        required_cols = {"Entry", "Gene Names", "Protein names"}
        missing_cols = required_cols - set(reader.fieldnames)
        if missing_cols:
            print(f"Error: Missing columns {missing_cols} in the TSV file.")
            sys.exit(1)

        # Create a JSON file for each row in the TSV
        for row in reader:
            entry = row["Entry"]
            protein_names = row["Protein names"]
            gene_names = row["Gene Names"]

            data = {
                "uniprot_id": entry,
                "uniprot_desc": protein_names,
                "gene_id": gene_names,
                "species_id": species
            }

            # Build the output file path: <output_dir>/<entry>.json
            uniprot_file = os.path.join(output_dir, f"{entry}.json")

            # Write the JSON data
            with open(uniprot_file , 'w', encoding='utf-8') as uniprot_out:
                json.dump(data, uniprot_out, indent=4)

            # Split into individual gene names
            for gene in gene_names.split():

                # Build the output file path: <output_dir>/<gene>.json
                gene_file = os.path.join(gene_dir, f"{gene}.json")

                # Write the JSON data
                try:
                    with open(gene_file, 'w', encoding='utf-8') as gene_out:
                        json.dump(data, gene_out, indent=4)
                    print(f"Wrote {gene_file}")
                except:
                    print(f"Couldn't find {gene_file}")


    print(f"JSON files have been created in: {output_dir} and {gene_dir}")

if __name__ == "__main__":
    main()
