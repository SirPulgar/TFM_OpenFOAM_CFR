from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

ADIABATIC = ROOT / "cases/03_compressionFlow/postProcessing"
THERMAL = ROOT / "cases/04_compressionHeatTransfer/postProcessing"
OUTPUT = ROOT / "docs/results/comparison_adiabatic_heat_transfer.csv"


def read_value(case: Path, field: str, time_dir: Path) -> float:
    file_path = case / field / time_dir.name / "volFieldValue.dat"

    for line in file_path.read_text().splitlines():
        line = line.strip()

        if line and not line.startswith("#"):
            return float(line.split()[1])

    raise ValueError(f"No se encontró ningún valor en {file_path}")


def time_value(path: Path) -> float:
    value = float(path.name)
    return 0.0 if abs(value) < 1e-8 else value


thermal_times = sorted(
    (THERMAL / "volAverage(T)").iterdir(),
    key=time_value,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(
        [
            "CAD",
            "T_adiabatic_K",
            "T_heat_transfer_K",
            "delta_T_K",
            "p_adiabatic_Pa",
            "p_heat_transfer_Pa",
            "delta_p_Pa",
        ]
    )

    for thermal_time in thermal_times:
        cad = time_value(thermal_time)

        adiabatic_time = min(
            (ADIABATIC / "volAverage(T)").iterdir(),
            key=lambda path: abs(time_value(path) - cad),
        )

        t_ad = read_value(ADIABATIC, "volAverage(T)", adiabatic_time)
        t_ht = read_value(THERMAL, "volAverage(T)", thermal_time)
        p_ad = read_value(ADIABATIC, "volAverage(p)", adiabatic_time)
        p_ht = read_value(THERMAL, "volAverage(p)", thermal_time)

        writer.writerow(
            [
                round(cad, 1),
                round(t_ad, 6),
                round(t_ht,6),
                round(t_ht - t_ad, 6),
                round(p_ad, 3),
                round(p_ht, 3),
                round(p_ht - p_ad, 3)
            ]
        )

print(f"CSV generado: {OUTPUT}")
