
import json
import os
import sys

# How to use
# out/fct should contain either ns3 .out output or simbricks json output
# $ python3 parse.py out/fct
fct = []
def check_for_files(directory):
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return

    files = os.listdir(directory)
    out_files = [f for f in files if f.endswith('.out')]
    json_files = [f for f in files if f.endswith('.json')]

    if out_files or json_files:
        # print("Matching files found:")
        for f in out_files:
            # print(f"- .out file: {f}")
            scan_out_file(os.path.join(directory, f))
        for f in json_files:
            # print(f"- .json file: {f}")
            scan_json_file(os.path.join(directory, f))
    else:
        print("No .out or .json files found in the directory.")

def scan_out_file(filepath):
    try:
        with open(filepath, 'r') as file:
            for line in file:
                if "FCT: " in line:
                    parts = line.split("FCT: ", 1)[1].split()
                    # print(parts[0])
                    fct.append(float(parts[0]))
            file.close()
    except Exception as e:
        print(f"Could not open file {filepath}: {e}")

def scan_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            sims =  data['sims']
            for key, value in sims.items():
                if 'host.client' in key:
                    for line in value['stdout']:
                        if "FCT: " in line:
                            parts = line.split("FCT: ", 1)[1].split()
                            # print(parts[0])
                            fct.append(float(parts[0]))
                            
            file.close()
    except Exception as e:
        print(f"Could not open file {filepath}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_files.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    check_for_files(directory_path)
    sort_fct = sorted(fct)

    cdf = [ i / len(fct) for i in range(1, len(fct) + 1) ]
    # print(cdf)

    for i in range(len(sort_fct)):
        print(f"{sort_fct[i]} {cdf[i]}")