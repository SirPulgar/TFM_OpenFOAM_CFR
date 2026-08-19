from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]

CSV_FILE = (
    ROOT
    / "docs/results/wall_heat_flux_compression_expansion_CFR_walls.csv"
)

OUTPUT = (
    ROOT
    / "docs/figures/evolucion_flujo_termico_compresion_expansion.png"
)

cad = []
q_piston = []
q_head = []
q_wall = []
q_total = []

with CSV_FILE.open(encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cad.append(float(row["CAD"]))
        q_piston.append(float(row["Q_piston_W"]))
        q_head.append(float(row["Q_cylinderHead_W"]))
        q_wall.append(float(row["Q_cylinderWall_W"]))
        q_total.append(float(row["Q_total_W"]))

plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    q_piston,
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="Pistón",
)

plt.plot(
    cad,
    q_head,
    marker="s",
    markersize=3.5,
    linewidth=1.5,
    label="Culata",
)

plt.plot(
    cad,
    q_wall,
    marker="^",
    markersize=3.5,
    linewidth=1.5,
    label="Pared del cilindro",
)

plt.plot(
    cad,
    q_total,
    color="black",
    marker="D",
    markersize=3.5,
    linewidth=2,
    label="Total",
)

plt.axhline(
    0,
    color="gray",
    linewidth=1,
)

plt.axvline(
    0,
    color="gray",
    linestyle=":",
    linewidth=1.2,
    label="PMS",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Potencia térmica instantánea (W)")
plt.xticks(range(-180, 181, 30))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("Figura generada:", OUTPUT)