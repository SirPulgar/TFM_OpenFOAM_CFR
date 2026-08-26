import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"

CASE07_FILE = DOCS / "results_07_variableProperties_thermodynamics.csv"
CASE08_FILE = DOCS / "results_08_combustion_thermodynamics.csv"
HEAT08_FILE = DOCS / "results_08_combustion_wallHeatFlux.csv"


def read_csv_columns(path):
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError(f"El archivo no contiene datos: {path}")

    return {
        column: [float(row[column]) for row in rows]
        for column in rows[0]
    }


def maximum_point(x_values, y_values):
    index = max(range(len(y_values)), key=y_values.__getitem__)
    return x_values[index], y_values[index]


def add_cycle_references(axis):
    axis.axvspan(
        -13,
        27,
        color="#f4a261",
        alpha=0.12,
        label="Combustión Wiebe",
        zorder=0,
    )
    axis.axvline(
        0,
        color="#555555",
        linestyle="--",
        linewidth=1.1,
        label="PMS",
    )
    axis.axvline(
        9.5,
        color="#8e44ad",
        linestyle=":",
        linewidth=1.3,
        label="CA50",
    )


def save_figure(figure, filename):
    output = FIGURES / filename
    figure.tight_layout()
    figure.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(figure)
    print(f"Generada: {output.relative_to(ROOT)}")


def plot_pressure(case07, case08):
    cad07 = case07["CAD"]
    cad08 = case08["CAD"]
    pressure07 = case07["p_mean_bar"]
    pressure08 = case08["p_mean_bar"]

    max_cad, max_pressure = maximum_point(cad08, pressure08)

    figure, axis = plt.subplots(figsize=(9.2, 5.2))

    add_cycle_references(axis)

    axis.plot(
        cad07,
        pressure07,
        color="#2a6fbb",
        linewidth=1.8,
        linestyle="--",
        marker="o",
        markersize=3.2,
        label="Caso 07: sin combustión",
    )
    axis.plot(
        cad08,
        pressure08,
        color="#d62828",
        linewidth=2.1,
        label="Caso 08: combustión Wiebe",
    )

    axis.scatter(
        [max_cad],
        [max_pressure],
        color="#d62828",
        s=30,
        zorder=5,
    )
    axis.annotate(
        f"$p_{{max}}$ = {max_pressure:.2f} bar\n{max_cad:.0f} CAD",
        xy=(max_cad, max_pressure),
        xytext=(48, 78),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        fontsize=9,
        ha="left",
    )

    axis.set(
        title="Evolución de la presión media en el cilindro",
        xlabel="Ángulo de cigüeñal [CAD]",
        ylabel="Presión media [bar]",
        xlim=(-180, 180),
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left", frameon=True)

    save_figure(
        figure,
        "comparacion_presion_casos_07_08.png",
    )


def plot_temperature(case07, case08):
    cad07 = case07["CAD"]
    cad08 = case08["CAD"]

    temperature_mean07 = case07["T_mean_K"]
    temperature_mean08 = case08["T_mean_K"]
    temperature_max08 = case08["T_max_K"]

    max_mean_cad, max_mean = maximum_point(
        cad08,
        temperature_mean08,
    )
    max_local_cad, max_local = maximum_point(
        cad08,
        temperature_max08,
    )

    figure, axis = plt.subplots(figsize=(9.2, 5.2))

    add_cycle_references(axis)

    axis.plot(
        cad07,
        temperature_mean07,
        color="#2a6fbb",
        linewidth=1.8,
        linestyle="--",
        marker="o",
        markersize=3.2,
        label="Caso 07: temperatura media",
    )
    axis.plot(
        cad08,
        temperature_mean08,
        color="#d62828",
        linewidth=2.1,
        label="Caso 08: temperatura media",
    )
    axis.plot(
        cad08,
        temperature_max08,
        color="#f77f00",
        linewidth=1.7,
        linestyle=":",
        label="Caso 08: temperatura máxima local",
    )

    axis.scatter(
        [max_mean_cad, max_local_cad],
        [max_mean, max_local],
        color=["#d62828", "#f77f00"],
        s=28,
        zorder=5,
    )
    axis.annotate(
        f"$\\overline{{T}}_{{max}}$ = {max_mean:.1f} K",
        xy=(max_mean_cad, max_mean),
        xytext=(47, 3020),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        fontsize=9,
    )
    axis.annotate(
        f"$T_{{max}}$ = {max_local:.1f} K\n{max_local_cad:.0f} CAD",
        xy=(max_local_cad, max_local),
        xytext=(57, 3620),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        fontsize=9,
    )

    axis.set(
        title="Evolución de la temperatura en el cilindro",
        xlabel="Ángulo de cigüeñal [CAD]",
        ylabel="Temperatura [K]",
        xlim=(-180, 180),
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left", frameon=True)

    save_figure(
        figure,
        "comparacion_temperatura_casos_07_08.png",
    )


def plot_wall_heat_loss(heat08):
    cad = heat08["CAD"]

    piston = heat08["Qloss_piston_W"]
    head = heat08["Qloss_cylinderHead_W"]
    wall = heat08["Qloss_cylinderWall_W"]
    total = heat08["Qloss_total_W"]

    max_cad, max_total = maximum_point(cad, total)

    figure, axis = plt.subplots(figsize=(9.2, 5.2))

    add_cycle_references(axis)

    axis.axhline(
        0,
        color="#666666",
        linewidth=0.9,
    )
    axis.plot(
        cad,
        piston,
        color="#e76f51",
        linewidth=1.6,
        label="Pistón",
    )
    axis.plot(
        cad,
        head,
        color="#2a9d8f",
        linewidth=1.6,
        label="Culata",
    )
    axis.plot(
        cad,
        wall,
        color="#457b9d",
        linewidth=1.6,
        label="Pared del cilindro",
    )
    axis.plot(
        cad,
        total,
        color="#111111",
        linewidth=2.2,
        label="Total",
    )

    axis.scatter(
        [max_cad],
        [max_total],
        color="#111111",
        s=30,
        zorder=5,
    )
    axis.annotate(
        f"$Q_{{max}}$ = {max_total:.2f} W\n{max_cad:.0f} CAD",
        xy=(max_cad, max_total),
        xytext=(50, 150),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        fontsize=9,
    )

    axis.set(
        title="Potencia térmica transferida a las paredes — caso 08",
        xlabel="Ángulo de cigüeñal [CAD]",
        ylabel="Potencia térmica del wedge de 5° [W]",
        xlim=(-180, 180),
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left", frameon=True)

    save_figure(
        figure,
        "perdidas_termicas_caso_08.png",
    )


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)

    case07 = read_csv_columns(CASE07_FILE)
    case08 = read_csv_columns(CASE08_FILE)
    heat08 = read_csv_columns(HEAT08_FILE)

    plot_pressure(case07, case08)
    plot_temperature(case07, case08)
    plot_wall_heat_loss(heat08)


if __name__ == "__main__":
    main()
