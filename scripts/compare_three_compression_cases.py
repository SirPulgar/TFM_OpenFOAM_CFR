from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

ADIABATIC = ROOT / "cases/03_compressionFlow/postProcessing"
WALLS_300 = ROOT / "cases/04_compressionHeatTransfer/postProcessing"
CFR_WALLS = ROOT / "cases/05_compressionHeatTransferCFRWalls/postProcessing"

OUTPUT = ROOT / "docs/results/comparison_three_compression_cases.csv"


def time_value(path: Path) -> float:
    value = float(path.name)
    return 0.0 if abs(value) < 1e-8 else value


def find_time_directory(case: Path, field: str, cad: float) -> Path:
    return min(
        (case / field).iterdir(),
        key=lambda path: abs(time_value(path) - cad),
    )


def read_value(case: Path, field: str, cad: float) -> float:
    time_dir = find_time_directory(case, field, cad)
    file_path = case / field / time_dir.name / "volFieldValue.dat"

    for line in file_path.read_text().splitlines():
        line = line.strip()

        if line and not line.startswith("#"):
            return float(line.split()[1])

    raise ValueError(f"No se encontró ningún valor en {file_path}")


times = sorted(
    (CFR_WALLS / "volAverage(T)").iterdir(),
    key=time_value,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(
        [
            "CAD",
            "T_adiabatic_K",
            "T_walls_300K_K",
            "T_CFR_walls_K",
            "delta_T_300K_K",
            "delta_T_CFR_K",
            "p_adiabatic_Pa",
            "p_walls_300K_Pa",
            "p_CFR_walls_Pa",
            "delta_p_300K_Pa",
            "delta_p_CFR_Pa",
        ]
    )

    for time_dir in times:
        cad = time_value(time_dir)

        t_ad = read_value(ADIABATIC, "volAverage(T)", cad)
        t_300 = read_value(WALLS_300, "volAverage(T)", cad)
        t_cfr = read_value(CFR_WALLS, "volAverage(T)", cad)

        p_ad = read_value(ADIABATIC, "volAverage(p)", cad)
        p_300 = read_value(WALLS_300, "volAverage(p)", cad)
        p_cfr = read_value(CFR_WALLS, "volAverage(p)", cad)

        writer.writerow(
            [
                round(cad, 1),
                round(t_ad, 6),
                round(t_300, 6),
                round(t_cfr, 6),
                round(t_300 - t_ad, 6),
                round(t_cfr - t_ad, 6),
                round(p_ad, 3),
                round(p_300, 3),
                round(p_cfr, 3),
                round(p_300 - p_ad, 3),
                round(p_cfr - p_ad, 3),
            ]
        )

print(f"CSV generado: {OUTPUT}")
