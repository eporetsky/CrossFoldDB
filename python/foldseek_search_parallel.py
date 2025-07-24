import os
import subprocess
import concurrent.futures
import re
import random
import sys
from datetime import datetime


def parse_uniprot_id(file_name):
    """
    Attempts to parse the UniProt ID from a Foldseek-like filename.
    Typical naming pattern might look like: AF-<UNIPROT_ID>-F1-model_v4.cif.gz
    Returns the extracted UniProt ID, or an empty string if not found.
    """
    file_stem = re.sub(r'(\.cif\.gz|\.pdb\.gz|\.json\.gz)$', '', file_name)
    match = re.match(r'^AF-(.*?)-F1-model_v4', file_stem)

    return match.group(1) if match else file_stem


def run_foldseek_job(params):
    """Function to run one foldseek job, receiving a tuple of parameters."""
    file_path, target_db, output_file, temp_path, home_path = params

    cmd = [
        "foldseek",
        "easy-search",
        f"{file_path}",
        f"{target_db}",
        f"{output_file}",
        f"{temp_path}",
        "--format-mode", "3",
        "--max-seqs", "10"
    ]

    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        return (file_path, True, "")
    except subprocess.CalledProcessError as e:
        return (file_path, False, str(e))

def main():
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <species_file> <species_input> <reference> <home_path>")
        sys.exit(1)

    species_file  = sys.argv[1]
    species_input = sys.argv[2]
    reference     = sys.argv[3]
    home_path     = sys.argv[4] #.rstrip("/")    # strip trailing slash
    reverse = (sys.argv[5].lower() == "reverse")
    outdir_base   = "./html"

    # --- 1) load all species into a dict ---
    species_map = {}
    with open(species_file, "r", encoding="utf-8") as fh:
        header = next(fh)
        for line in fh:
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue
            name = parts[0].strip()
            species_map[name] = dict(
                species    = name,
                html       = parts[1].strip(),
                target_db  = parts[2].strip(),
                cif        = parts[3].strip(),
                annotation = parts[4].strip(),
                uniprot    = parts[5].strip(),
                species_id = parts[6].strip()
            )

    # --- 2) pick off the two rows we need ---
    if species_input not in species_map:
        print(f"Error: target species '{species_input}' not found")
        sys.exit(2)
    if reference not in species_map:
        print(f"Error: reference species '{reference}' not found")
        sys.exit(3)

    target_row    = species_map[species_input]
    reference_row = species_map[reference]

    # --- 3) build the two paths (use os.path.join!) ---
    structures_path = reference_row["cif"] #os.path.join(home_path, reference_row["cif"])
    target_db_path  = target_row["target_db"] #os.path.join(home_path, target_row["target_db"])
    #outdir          = os.path.join(outdir_base, reference_row["species"])
    outdir          = os.path.join(outdir_base, species_input)
    os.makedirs(outdir, exist_ok=True)

    print(f"DEBUG: querying   → {structures_path}")
    print(f"DEBUG: against     → {target_db_path}")
    print(f"DEBUG: writing html → {outdir}")

    # --- 4) assemble jobs over *reference* structures, hitting the *target* DB ---
    jobs = []
    files = sorted(os.listdir(structures_path), reverse=reverse)

    for fname in files:
    #for fname in os.listdir(structures_path):
        fpath = os.path.join(structures_path, fname)
        if not os.path.isfile(fpath):
            continue

        uniprot_id = parse_uniprot_id(fname)
        if not uniprot_id:
            continue

        out_html = os.path.join(outdir, f"{uniprot_id}.html")
        tmp_dir  = f"./tmp/temp_{random.randint(0,9999999999):010d}"

        params = (
            fpath,           # query = reference file
            target_db_path,  # target = species_input db
            out_html,
            tmp_dir,
            home_path
        )
        jobs.append(params)

    # --- 5) run them in parallel ---
    with concurrent.futures.ProcessPoolExecutor(max_workers=48) as executor:
        for fpath, success, err in executor.map(run_foldseek_job, jobs):
            status = "Done" if success else f"FAILED: {err}"
            print(f"{status} → {fpath}")

    print(f"Finished at: {datetime.now()}")



if __name__ == "__main__":
    main()
