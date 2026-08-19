from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

CASE = ROOT / "cases/06_compressionExpansion/postProcessing"

OUTPUT = ROOT / "docs/results/compression_expansion_CFR_walls.csv"


def time_value(path: Path) -> float:
    value = float(path.name)
    return 0.0 if abs(value) < 1e-8 else value


def read_value(field: str, time_name: str) -> float:
    file_path = CASE / field / time_name / "volFieldValue.dat"

    for line in file_path.read_text().splitlines():
        line = line.strip()

        if line and not line.startswith("#"):
            return float(line.split()[1])

    raise ValueError(f"No se encontró ningún valor en {file_path}")


times = sorted(
    (CASE / "volAverage(T)").iterdir(),
    key=time_value,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(
        [
            "CAD",
            "T_mean_K",
            "p_mean_Pa",
        ]
    )

    for time_dir in times:
        cad = time_value(time_dir)

        temperature = read_value("volAverage(T)", time_dir.name)
        pressure = read_value("volAverage(p)", time_dir.name)

        writer.writerow(
            [
                round(cad, 1),
                round(temperature, 6),
                round(pressure, 3),
            ]
        )

print(f"CSV generado: {OUTPUT}")