from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]

COMPARISON_CSV = (
    ROOT
    / "docs/results/comparison_properties_compression_expansion.csv"
)

WALL_CONSTANT_CSV = (
    ROOT
    / "docs/results/wall_heat_flux_compression_expansion_CFR_walls.csv"
)

WALL_VARIABLE_CSV = (
    ROOT
    / "docs/results/wall_heat_flux_compression_expansion_variable_properties.csv"
)

FIGURES_DIR = ROOT / "docs/figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(file_path: Path) -> list[dict[str, str]]:
    with file_path.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


comparison = read_csv(COMPARISON_CSV)

cad = [float(row["CAD"]) for row in comparison]

t_mean_constant = [
    float(row["T_mean_constant_properties_K"])
    for row in comparison
]

t_mean_variable = [
    float(row["T_mean_variable_properties_K"])
    for row in comparison
]

p_mean_constant_bar = [
    float(row["p_mean_constant_properties_Pa"]) / 100000
    for row in comparison
]

p_mean_variable_bar = [
    float(row["p_mean_variable_properties_Pa"]) / 100000
    for row in comparison
]

t_min_constant = [
    float(row["T_min_constant_properties_K"])
    for row in comparison
]

t_max_constant = [
    float(row["T_max_constant_properties_K"])
    for row in comparison
]

t_min_variable = [
    float(row["T_min_variable_properties_K"])
    for row in comparison
]

t_max_variable = [
    float(row["T_max_variable_properties_K"])
    for row in comparison
]


def configure_axes() -> None:
    plt.axvline(
        0,
        color="gray",
        linestyle=":",
        linewidth=1.5,
        label="PMS",
    )

    plt.xticks(range(-180, 181, 30))
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    t_mean_constant,
    marker="o",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades constantes (caso 6)",
)

plt.plot(
    cad,
    t_mean_variable,
    marker="s",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades variables (caso 7)",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Temperatura media (K)")

configure_axes()

plt.savefig(
    FIGURES_DIR
    / "comparacion_temperatura_media_propiedades_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


plt.figure(figsize=(8, 5))

plt.plot(
    cad,
    p_mean_constant_bar,
    marker="o",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades constantes (caso 6)",
)

plt.plot(
    cad,
    p_mean_variable_bar,
    marker="s",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades variables (caso 7)",
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Presión media (bar)")

configure_axes()

plt.savefig(
    FIGURES_DIR
    / "comparacion_presion_media_propiedades_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


fig, axes = plt.subplots(
    2,
    1,
    figsize=(8, 8),
    sharex=True,
    sharey=True,
)

axes[0].fill_between(
    cad,
    t_min_constant,
    t_max_constant,
    alpha=0.25,
    color="tab:blue",
    label="Rango espacial Tmin–Tmax",
)

axes[0].plot(
    cad,
    t_mean_constant,
    color="tab:blue",
    linewidth=1.8,
    label="Temperatura media",
)

axes[0].axvline(
    0,
    color="gray",
    linestyle=":",
    linewidth=1.5,
)

axes[0].set_title("Propiedades constantes (caso 6)")
axes[0].set_ylabel("Temperatura (K)")
axes[0].grid(True, linestyle="--", alpha=0.4)
axes[0].legend()

axes[1].fill_between(
    cad,
    t_min_variable,
    t_max_variable,
    alpha=0.25,
    color="tab:orange",
    label="Rango espacial Tmin–Tmax",
)

axes[1].plot(
    cad,
    t_mean_variable,
    color="tab:orange",
    linewidth=1.8,
    label="Temperatura media",
)

axes[1].axvline(
    0,
    color="gray",
    linestyle=":",
    linewidth=1.5,
)

axes[1].set_title("Propiedades variables (caso 7)")
axes[1].set_xlabel("Ángulo del cigüeñal (CAD)")
axes[1].set_ylabel("Temperatura (K)")
axes[1].set_xticks(range(-180, 181, 30))
axes[1].grid(True, linestyle="--", alpha=0.4)
axes[1].legend()

fig.tight_layout()

fig.savefig(
    FIGURES_DIR
    / "comparacion_extremos_temperatura_propiedades_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


wall_constant = {
    float(row["CAD"]): float(row["Q_total_W"])
    for row in read_csv(WALL_CONSTANT_CSV)
}

wall_variable = {
    float(row["CAD"]): float(row["Q_total_W"])
    for row in read_csv(WALL_VARIABLE_CSV)
}

if set(wall_constant) != set(wall_variable):
    raise ValueError(
        "Los CSV de flujo térmico no contienen los mismos instantes."
    )

wall_cad = sorted(wall_constant)

q_total_constant = [
    wall_constant[value]
    for value in wall_cad
]

q_total_variable = [
    wall_variable[value]
    for value in wall_cad
]

plt.figure(figsize=(8, 5))

plt.plot(
    wall_cad,
    q_total_constant,
    marker="o",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades constantes (caso 6)",
)

plt.plot(
    wall_cad,
    q_total_variable,
    marker="s",
    markersize=3.5,
    linewidth=1.8,
    label="Propiedades variables (caso 7)",
)

plt.axhline(
    0,
    color="gray",
    linewidth=1,
)

plt.xlabel("Ángulo del cigüeñal (CAD)")
plt.ylabel("Potencia térmica instantánea total (W)")

configure_axes()

plt.savefig(
    FIGURES_DIR
    / "comparacion_flujo_termico_propiedades_compresion_expansion.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("Figuras generadas en:", FIGURES_DIR)