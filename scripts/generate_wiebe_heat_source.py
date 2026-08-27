from pathlib import Path
import argparse
import csv
import math


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CASE = ROOT / "cases/08_compressionExpansionCombustion"
DEFAULT_OUTPUT = ROOT / "docs/results/wiebe_heat_release.csv"

parser = argparse.ArgumentParser(
    description=(
        "Genera la fuente termica homogenea del caso 08 "
        "a partir de una ley de Wiebe."
    )
)

parser.add_argument(
    "--case",
    type=Path,
    default=DEFAULT_CASE,
    help="Ruta del caso de OpenFOAM.",
)

parser.add_argument(
    "--output",
    type=Path,
    default=DEFAULT_OUTPUT,
    help="CSV con la ley de liberacion de calor.",
)

args = parser.parse_args()

CASE = args.case.expanduser().resolve()
OUTPUT = args.output.expanduser().resolve()
FV_MODELS = CASE / "constant/fvModels"
HEAT_SOURCE = CASE / "constant/heatSource"


# Geometria real del sector wedge de blockMeshDict
OUTER_X = 41.235715e-3
OUTER_Y = 1.800390e-3
CROSS_SECTION_AREA = OUTER_X * OUTER_Y

STROKE = 0.1143
CRANK_RADIUS = STROKE / 2
CONNECTING_ROD = 0.254
CLEARANCE_HEIGHT = 0.0127

# Estado inicial y propiedades del aire
INITIAL_PRESSURE = 101325.0
INITIAL_TEMPERATURE = 300.0
UNIVERSAL_GAS_CONSTANT = 8314.46261815324
AIR_MOLAR_MASS = 28.8504
AIR_GAS_CONSTANT = UNIVERSAL_GAS_CONSTANT / AIR_MOLAR_MASS

# Estequiometria: C8H18 + 12.5 (O2 + 3.76 N2)
ISOOCTANE_MOLAR_MASS = 114.2285
AIR_MOLES_PER_FUEL_MOLE = 12.5 * (1 + 3.76)
STOICHIOMETRIC_AFR = (
    AIR_MOLES_PER_FUEL_MOLE
    * AIR_MOLAR_MASS
    / ISOOCTANE_MOLAR_MASS
)

LOWER_HEATING_VALUE = 44.343259e6
COMBUSTION_EFFICIENCY = 1.0

# Funcion de Wiebe
START_CAD = -13.0
DURATION_CAD = 40.0
END_CAD = START_CAD + DURATION_CAD
WIEBE_A = math.log(1000.0)
WIEBE_M = 3.0

ENGINE_SPEED_RPM = 600.0
CAD_PER_SECOND = ENGINE_SPEED_RPM * 6.0
TABLE_STEP_CAD = 0.1


def chamber_height(cad: float) -> float:
    angle = math.radians(cad)

    return (
        CLEARANCE_HEIGHT
        + CRANK_RADIUS * (1 - math.cos(angle))
        + CONNECTING_ROD
        - math.sqrt(
            CONNECTING_ROD**2
            - (CRANK_RADIUS * math.sin(angle)) ** 2
        )
    )


def chamber_volume(cad: float) -> float:
    return CROSS_SECTION_AREA * chamber_height(cad)


INITIAL_VOLUME = chamber_volume(-180.0)
AIR_MASS = (
    INITIAL_PRESSURE
    * INITIAL_VOLUME
    / (AIR_GAS_CONSTANT * INITIAL_TEMPERATURE)
)
FUEL_MASS = AIR_MASS / STOICHIOMETRIC_AFR
TOTAL_ENERGY = (
    FUEL_MASS
    * LOWER_HEATING_VALUE
    * COMBUSTION_EFFICIENCY
)


def burned_fraction(cad: float) -> float:
    if cad <= START_CAD:
        return 0.0

    if cad >= END_CAD:
        return 1.0

    relative_angle = (cad - START_CAD) / DURATION_CAD
    raw_fraction = 1 - math.exp(
        -WIEBE_A * relative_angle ** (WIEBE_M + 1)
    )

    return raw_fraction / (1 - math.exp(-WIEBE_A))


def burned_fraction_derivative(cad: float) -> float:
    if cad <= START_CAD or cad >= END_CAD:
        return 0.0

    relative_angle = (cad - START_CAD) / DURATION_CAD

    return (
        WIEBE_A
        * (WIEBE_M + 1)
        / DURATION_CAD
        * relative_angle**WIEBE_M
        * math.exp(
            -WIEBE_A * relative_angle ** (WIEBE_M + 1)
        )
        / (1 - math.exp(-WIEBE_A))
    )


def cad_at_burned_fraction(fraction: float) -> float:
    raw_fraction = fraction * (1 - math.exp(-WIEBE_A))
    relative_angle = (
        -math.log(1 - raw_fraction) / WIEBE_A
    ) ** (1 / (WIEBE_M + 1))

    return START_CAD + DURATION_CAD * relative_angle


def heat_release(cad: float) -> tuple[float, float]:
    energy_per_cad = TOTAL_ENERGY * burned_fraction_derivative(cad)
    power = energy_per_cad * CAD_PER_SECOND
    volumetric_power = power / chamber_volume(cad)

    return power, volumetric_power


def integrate_table(rows: list[tuple[float, float]]) -> float:
    energy = 0.0

    for first, second in zip(rows, rows[1:]):
        first_cad, first_q = first
        second_cad, second_q = second
        middle_cad = 0.5 * (first_cad + second_cad)
        middle_q = 0.5 * (first_q + second_q)
        delta_cad = second_cad - first_cad

        energy += (
            delta_cad
            / (6 * CAD_PER_SECOND)
            * (
                first_q * chamber_volume(first_cad)
                + 4 * middle_q * chamber_volume(middle_cad)
                + second_q * chamber_volume(second_cad)
            )
        )

    return energy


def write_fv_models() -> None:
    FV_MODELS.write_text(
        """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  13
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      fvModels;
}

#includeModel heatSource

// ************************************************************************* //
""",
        encoding="utf-8",
    )


def write_heat_source(rows: list[tuple[float, float]]) -> None:
    header = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  13
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      heatSource;
}

type            heatSource;

selectionMode   cellZone;
cellZone        all;

""" + (
        f"// Inicio: {START_CAD:.1f} CAD; final: {END_CAD:.1f} CAD\n"
        f"// Wiebe: a = {WIEBE_A:.7f}; m = {WIEBE_M:.1f}\n"
        f"// Energia total normalizada: {TOTAL_ENERGY:.9f} J\n\n"
    ) + """q
{
    type                    table;

    values
    (
"""

    values = "".join(
        f"        ({cad:.1f} {volumetric_power:.12e})\n"
        for cad, volumetric_power in rows
    )

    footer = """    );

    outOfBounds             clamp;
    interpolationScheme     linear;
}

// ************************************************************************* //
"""

    HEAT_SOURCE.write_text(
        header + values + footer,
        encoding="utf-8",
    )


def write_csv(
    rows: list[tuple[float, float, float, float, float, float]],
) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(
            [
                "CAD",
                "burned_fraction",
                "dxb_dCAD",
                "Qdot_W",
                "q_W_m3",
                "volume_m3",
            ]
        )
        writer.writerows(rows)


combustion_steps = round(DURATION_CAD / TABLE_STEP_CAD)
cad_values = [-180.0]
cad_values.extend(
    START_CAD + index * TABLE_STEP_CAD
    for index in range(combustion_steps + 1)
)
cad_values.append(180.0)

raw_table_rows = []

for cad in cad_values:
    _, volumetric_power = heat_release(cad)
    raw_table_rows.append((cad, volumetric_power))

raw_integrated_energy = integrate_table(raw_table_rows)
table_normalisation = TOTAL_ENERGY / raw_integrated_energy

table_rows = [
    (cad, volumetric_power * table_normalisation)
    for cad, volumetric_power in raw_table_rows
]

csv_rows = []

for cad, volumetric_power in table_rows:
    power = volumetric_power * chamber_volume(cad)
    csv_rows.append(
        (
            round(cad, 1),
            burned_fraction(cad),
            burned_fraction_derivative(cad),
            power,
            volumetric_power,
            chamber_volume(cad),
        )
    )

integrated_energy = integrate_table(table_rows)
peak_row = max(csv_rows, key=lambda row: row[3])


write_fv_models()
write_heat_source(table_rows)
write_csv(csv_rows)

print(f"fvModels generado: {FV_MODELS}")
print(f"heatSource generado: {HEAT_SOURCE}")
print(f"CSV generado: {OUTPUT}")
print(f"Volumen inicial: {INITIAL_VOLUME:.12e} m3")
print(f"Masa de aire: {AIR_MASS:.12e} kg")
print(f"AFR estequiometrica: {STOICHIOMETRIC_AFR:.8f}")
print(f"Masa de combustible: {FUEL_MASS:.12e} kg")
print(f"Energia objetivo: {TOTAL_ENERGY:.9f} J")
print(f"Energia integrada: {integrated_energy:.9f} J")
print(f"Factor de normalizacion de la tabla: {table_normalisation:.12f}")
print(f"CA50: {cad_at_burned_fraction(0.5):.6f} CAD")
print(f"CA90: {cad_at_burned_fraction(0.9):.6f} CAD")
print(f"Pico de liberacion: {peak_row[3]:.6f} W a {peak_row[0]:.1f} CAD")
print(
    "Error relativo: "
    f"{(integrated_energy / TOTAL_ENERGY - 1) * 100:.6e} %"
)