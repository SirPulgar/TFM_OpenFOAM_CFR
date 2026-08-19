from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "docs/results/compression_expansion_CFR_walls.csv"
FIGURES_DIR = ROOT / "docs/figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

cad = []
temperature = []
pressure_bar = []

with CSV_FILE.open(encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cad.append(float(row["CAD"]))
        temperature.append(float(row["T_mean_K"]))
        pressure_bar.append(float(row["p_mean_Pa"]) / 100000)


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    temperature,
    marker="o",
    markersize=4,
    linewidth=1.8,
    label="Temperaturas de pared CFR",
)

plt.axvline(
    0,
    color="gray",
    linestyle=":",
    linewidth=1.2,
    label="PMS",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Temperatura media (K)")
plt.xticks(range(-180, 181, 30))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "evolucion_temperatura_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    pressure_bar,
    marker="o",
    markersize=4,
    linewidth=1.8,
    label="Temperaturas de pared CFR",
)

plt.axvline(
    0,
    color="gray",
    linestyle=":",
    linewidth=1.2,
    label="PMS",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Presión media (bar)")
plt.xticks(range(-180, 181, 30))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "evolucion_presion_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("Figuras generadas en:", FIGURES_DIR)