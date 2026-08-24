from pathlib import Path
import argparse
import csv
import re


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CASE = ROOT / "cases/06_compressionExpansion"
DEFAULT_OUTPUT = (
    ROOT
    / "docs/results/temperature_extrema_compression_expansion.csv"
)

parser = argparse.ArgumentParser(
    description=(
        "Extrae los extremos locales de temperatura "
        "de un caso de OpenFOAM."
    )
)

parser.add_argument(
    "--case",
    type=Path,
    default=DEFAULT_CASE,
    help="Ruta del caso de OpenFOAM que se analizará.",
)

parser.add_argument(
    "--output",
    type=Path,
    default=DEFAULT_OUTPUT,
    help="Archivo CSV en el que se guardarán los resultados.",
)

args = parser.parse_args()

CASE = args.case.expanduser().resolve()
OUTPUT = args.output.expanduser().resolve()

UNIFORM_PATTERN = re.compile(
    r"internalField\s+uniform\s+([+-]?[0-9.eE+-]+)\s*;"
)


def time_value(path: Path) -> float:
    value = float(path.name)
    return 0.0 if abs(value) < 1e-8 else value


def read_internal_temperature(
    file_path: Path,
) -> tuple[str, list[float]]:
    lines = file_path.read_text().splitlines()

    for index, line in enumerate(lines):
        uniform_match = UNIFORM_PATTERN.search(line)

        if uniform_match:
            value = float(uniform_match.group(1))
            return "uniform", [value]

        if (
            "internalField" in line
            and "nonuniform List<scalar>" in line
        ):
            cursor = index + 1

            while not lines[cursor].strip():
                cursor += 1

            declared_values = int(lines[cursor].strip())
            cursor += 1

            while lines[cursor].strip() != "(":
                cursor += 1

            cursor += 1
            values = []

            while not lines[cursor].strip().startswith(")"):
                value = lines[cursor].strip()

                if value:
                    values.append(float(value))

                cursor += 1

            if len(values) != declared_values:
                raise ValueError(
                    f"{file_path}: se esperaban {declared_values} "
                    f"valores y se han leído {len(values)}"
                )

            return "nonuniform", values

    raise ValueError(
        f"No se ha encontrado internalField en {file_path}"
    )


time_directories = []

for path in CASE.iterdir():
    if not path.is_dir() or not (path / "T").is_file():
        continue

    try:
        time_value(path)
    except ValueError:
        continue

    time_directories.append(path)

time_directories.sort(key=time_value)

raw_results = []

for time_directory in time_directories:
    cad = time_value(time_directory)
    field_type, values = read_internal_temperature(
        time_directory / "T"
    )

    raw_results.append(
        {
            "CAD": cad,
            "field_type": field_type,
            "values": values,
        }
    )

nonuniform_sizes = {
    len(result["values"])
    for result in raw_results
    if result["field_type"] == "nonuniform"
}

if len(nonuniform_sizes) != 1:
    raise ValueError(
        "Los campos no uniformes no tienen el mismo número de celdas: "
        f"{sorted(nonuniform_sizes)}"
    )

cell_count = nonuniform_sizes.pop()

results = []

for raw_result in raw_results:
    cad = raw_result["CAD"]
    values = raw_result["values"]

    if raw_result["field_type"] == "uniform":
        values = values * cell_count

    if len(values) != cell_count:
        raise ValueError(
            f"En {cad} CAD se esperaban {cell_count} celdas "
            f"y se han encontrado {len(values)}"
        )

    cells_below_200 = sum(value < 200 for value in values)
    cells_below_250 = sum(value < 250 for value in values)
    cells_above_900 = sum(value > 900 for value in values)
    cells_above_1000 = sum(value > 1000 for value in values)

    extreme_cells = cells_below_250 + cells_above_900

    results.append(
        {
            "CAD": round(cad, 1),
            "T_min_K": round(min(values), 6),
            "T_max_K": round(max(values), 6),
            "cells_below_200K": cells_below_200,
            "pct_below_200K": round(
                100 * cells_below_200 / cell_count,
                6,
            ),
            "cells_below_250K": cells_below_250,
            "pct_below_250K": round(
                100 * cells_below_250 / cell_count,
                6,
            ),
            "cells_above_900K": cells_above_900,
            "pct_above_900K": round(
                100 * cells_above_900 / cell_count,
                6,
            ),
            "cells_above_1000K": cells_above_1000,
            "pct_above_1000K": round(
                100 * cells_above_1000 / cell_count,
                6,
            ),
            "extreme_cells": extreme_cells,
            "extreme_pct": round(
                100 * extreme_cells / cell_count,
                6,
            ),
        }
    )

fieldnames = [
    "CAD",
    "T_min_K",
    "T_max_K",
    "cells_below_200K",
    "pct_below_200K",
    "cells_below_250K",
    "pct_below_250K",
    "cells_above_900K",
    "pct_above_900K",
    "cells_above_1000K",
    "pct_above_1000K",
    "extreme_cells",
    "extreme_pct",
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(results)

global_minimum = min(
    results,
    key=lambda result: result["T_min_K"],
)

global_maximum = max(
    results,
    key=lambda result: result["T_max_K"],
)

print(f"CSV generado: {OUTPUT}")
print(f"Tiempos analizados: {len(results)}")
print(f"Celdas por instante: {cell_count}")

print(
    "Mínimo global: "
    f"{global_minimum['T_min_K']:.6f} K "
    f"en {global_minimum['CAD']:.1f} CAD"
)

print(
    "Máximo global: "
    f"{global_maximum['T_max_K']:.6f} K "
    f"en {global_maximum['CAD']:.1f} CAD"
)

print("\nInstantes con T < 250 K o T > 900 K:")

for result in results:
    if result["extreme_cells"] == 0:
        continue

    print(
        f"{result['CAD']:+.1f} CAD: "
        f"<250 K = {result['cells_below_250K']}, "
        f">900 K = {result['cells_above_900K']}, "
        f"total = {result['extreme_cells']} "
        f"({result['extreme_pct']:.4f} %)"
    )