from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "docs/wallHeatFlux_compressionExpansionVariableProperties_allTimes.txt"

OUTPUT = (
    ROOT
    / "docs/results/wall_heat_flux_compression_expansion_variable_properties.csv"
)

time_pattern = re.compile(r"Time = ([^C]+)CAD")
patch_pattern = re.compile(
    r"for patch (\w+) = .*?, .*?, ([+-]?[0-9.eE+-]+),"
)

results = {}
current_time = None

for line in INPUT_FILE.read_text().splitlines():
    time_match = time_pattern.search(line)

    if time_match:
        value = float(time_match.group(1).strip())
        current_time = 0.0 if abs(value) < 1e-8 else value
        results.setdefault(current_time, {})
        continue

    patch_match = patch_pattern.search(line)

    if patch_match and current_time is not None:
        patch = patch_match.group(1)
        heat_rate = float(patch_match.group(2))
        results[current_time][patch] = heat_rate

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(
        [
            "CAD",
            "Q_piston_W",
            "Q_cylinderHead_W",
            "Q_cylinderWall_W",
            "Q_total_W",
        ]
    )

    for cad in sorted(results):
        values = results[cad]

        piston = values["piston"]
        head = values["cylinderHead"]
        wall = values["cylinderWall"]
        total = piston + head + wall

        writer.writerow(
            [
                round(cad, 1),
                round(piston, 6),
                round(head, 6),
                round(wall, 6),
                round(total, 6),
            ]
        )

print(f"CSV generado: {OUTPUT}")