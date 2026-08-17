from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "docs/results/comparison_adiabatic_heat_transfer.csv"
FIGURES_DIR = ROOT / "docs/figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

cad = []
t_adiabatic = []
t_thermal = []
p_adiabatic_bar = []
p_thermal_bar = []

with CSV_FILE.open(encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cad.append(float(row["CAD"]))
        t_adiabatic.append(float(row["T_adiabatic_K"]))
        t_thermal.append(float(row["T_heat_transfer_K"]))
        p_adiabatic_bar.append(float(row["p_adiabatic_Pa"]) / 100000)
        p_thermal_bar.append(float(row["p_heat_transfer_Pa"]) / 100000)


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    t_adiabatic,
    marker="o",
    markersize=4,
    linewidth=1.8,
    label="Caso adiabático",
)

plt.plot(
    cad,
    t_thermal,
    marker="s",
    markersize=4,
    linewidth=1.8,
    label="Caso con transferencia térmica",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Temperatura media (K)")
plt.xticks(range(-180, 1, 20))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "comparacion_temperatura_adiabatico_termico.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    p_adiabatic_bar,
    marker="o",
    markersize=4,
    linewidth=1.8,
    label="Caso adiabático",
)

plt.plot(
    cad,
    p_thermal_bar,
    marker="s",
    markersize=4,
    linewidth=1.8,
    label="Caso con transferencia térmica",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Presión media (bar)")
plt.xticks(range(-180, 1, 20))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "comparacion_presion_adiabatico_termico.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("Figuras generadas en:", FIGURES_DIR)
