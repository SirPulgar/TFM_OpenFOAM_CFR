from pathlib import Path
import argparse
import csv


ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(
    description=(
        "Compara el caso original con una prueba "
        "de sensibilidad de los esquemas numéricos."
    )
)

parser.add_argument(
    "--candidate-means",
    type=Path,
    required=True,
    help="CSV de valores medios del caso candidato.",
)

parser.add_argument(
    "--candidate-extrema",
    type=Path,
    required=True,
    help="CSV de extremos locales del caso candidato.",
)

parser.add_argument(
    "--baseline-means",
    type=Path,
    default=(
        ROOT
        / "docs/results/compression_expansion_CFR_walls.csv"
    ),
)

parser.add_argument(
    "--baseline-extrema",
    type=Path,
    default=(
        ROOT
        / "docs/results/"
        "temperature_extrema_compression_expansion.csv"
    ),
)

parser.add_argument(
    "--output",
    type=Path,
    default=(
        ROOT
        / "docs/results/"
        "comparison_schemes_compression_expansion.csv"
    ),
)

args = parser.parse_args()


def read_csv(file_path: Path) -> dict[float, dict[str, str]]:
    with file_path.open(encoding="utf-8") as file:
        return {
            float(row["CAD"]): row
            for row in csv.DictReader(file)
        }


baseline_means = read_csv(args.baseline_means)
candidate_means = read_csv(args.candidate_means)

baseline_extrema = read_csv(args.baseline_extrema)
candidate_extrema = read_csv(args.candidate_extrema)

common_times = sorted(
    set(baseline_means)
    & set(candidate_means)
    & set(baseline_extrema)
    & set(candidate_extrema)
)

if not common_times:
    raise ValueError(
        "No existen instantes comunes entre los CSV."
    )

results = []

for cad in common_times:
    original_mean = baseline_means[cad]
    limited_mean = candidate_means[cad]

    original_extrema = baseline_extrema[cad]
    limited_extrema = candidate_extrema[cad]

    t_original = float(original_mean["T_mean_K"])
    t_limited = float(limited_mean["T_mean_K"])

    p_original = float(original_mean["p_mean_Pa"])
    p_limited = float(limited_mean["p_mean_Pa"])

    delta_t = t_limited - t_original
    delta_p = p_limited - p_original

    results.append(
        {
            "CAD": round(cad, 1),
            "T_mean_original_K": round(t_original, 6),
            "T_mean_limitedLinear_K": round(t_limited, 6),
            "delta_T_mean_K": round(delta_t, 6),
            "delta_T_mean_pct": round(
                100 * delta_t / t_original,
                6,
            ),
            "p_mean_original_Pa": round(p_original, 3),
            "p_mean_limitedLinear_Pa": round(
                p_limited,
                3,
            ),
            "delta_p_mean_Pa": round(delta_p, 3),
            "delta_p_mean_pct": round(
                100 * delta_p / p_original,
                6,
            ),
            "T_min_original_K": float(
                original_extrema["T_min_K"]
            ),
            "T_min_limitedLinear_K": float(
                limited_extrema["T_min_K"]
            ),
            "T_max_original_K": float(
                original_extrema["T_max_K"]
            ),
            "T_max_limitedLinear_K": float(
                limited_extrema["T_max_K"]
            ),
            "extreme_cells_original": int(
                original_extrema["extreme_cells"]
            ),
            "extreme_cells_limitedLinear": int(
                limited_extrema["extreme_cells"]
            ),
        }
    )

output = args.output.expanduser().resolve()
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys(),
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(results)

largest_t_difference = max(
    results,
    key=lambda row: abs(row["delta_T_mean_pct"]),
)

largest_p_difference = max(
    results,
    key=lambda row: abs(row["delta_p_mean_pct"]),
)

maximum_original_extremes = max(
    row["extreme_cells_original"]
    for row in results
)

maximum_limited_extremes = max(
    row["extreme_cells_limitedLinear"]
    for row in results
)

print(f"CSV generado: {output}")
print(f"Instantes comparados: {len(results)}")

print(
    "Mayor diferencia relativa de temperatura media: "
    f"{largest_t_difference['delta_T_mean_pct']:+.4f} % "
    f"en {largest_t_difference['CAD']:+.1f} CAD"
)

print(
    "Mayor diferencia relativa de presión media: "
    f"{largest_p_difference['delta_p_mean_pct']:+.4f} % "
    f"en {largest_p_difference['CAD']:+.1f} CAD"
)

print(
    "Máximo número de celdas extremas: "
    f"original = {maximum_original_extremes}, "
    f"limitedLinear = {maximum_limited_extremes}"
)