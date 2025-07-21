import sys
import re

if len(sys.argv) != 3:
    print("[ERROR] Usage: python extract_wall_positions.py input_summary.txt output_vars.txt")
    sys.exit(1)

summary_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(summary_file, 'r') as f:
        content = f.read()

    wall1_match = re.search(r'Average wall1:\s*([\d\.\-+Ee]+)', content)
    wall2_match = re.search(r'Average wall2:\s*([\d\.\-+Ee]+)', content)

    if not wall1_match or not wall2_match:
        raise ValueError("Missing wall1 or wall2 line.")

    wall1_full = wall1_match.group(1)
    wall2_full = wall2_match.group(1)

    wall1_mean = wall1_full.split('+')[0]
    wall2_mean = wall2_full.split('+')[0]

    with open(output_file, 'w') as out:
        out.write(f"variable wall1 equal {wall1_mean}\n")
        out.write(f"variable wall2 equal {wall2_mean}\n")

    print(f"[INFO] Successfully extracted wall1={wall1_full}, wall2={wall2_full} → {output_file}")

except Exception as e:
    print(f"[ERROR] Failed to extract wall positions: {e}")
    sys.exit(1)
