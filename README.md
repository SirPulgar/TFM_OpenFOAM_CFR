# TFM OpenFOAM CFR

Desarrollo de un modelo CFD simplificado de un motor monocilíndrico CFR mediante OpenFOAM 13.

## Objetivo inicial

Construir un modelo funcional que permita estudiar la compresión y expansión del aire dentro del cilindro mediante una malla dinámica y el movimiento del pistón.

## Alcance de la primera fase

- Motor monocilíndrico CFR como referencia.
- Geometría axisimétrica mediante un sector tipo `wedge`.
- Cilindro cerrado.
- Pistón y culata planos.
- Aire compresible.
- Simulación transitoria.
- Movimiento del pistón.
- Sin válvulas.
- Sin inyección.
- Sin combustión.
- Paredes inicialmente adiabáticas.

## Parámetros iniciales

| Parámetro | Valor |
|---|---:|
| Diámetro del cilindro | 82,55 mm |
| Carrera del pistón | 114,30 mm |
| Longitud de la biela | 254 mm |
| Radio de manivela | 57,15 mm |
| Relación de compresión | 10:1 |
| Régimen inicial | 600 rpm |
| Presión inicial | 101325 Pa |
| Temperatura inicial | 300 K |

## Fases previstas

1. Construcción de la geometría y la malla estática.
2. Comprobación de la calidad de la malla.
3. Configuración de la malla dinámica.
4. Implementación del movimiento del pistón.
5. Simulación inicial de compresión.
6. Simulación de compresión y expansión.
7. Análisis de presión, temperatura y velocidad.
8. Documentación y validación del modelo.

## Entorno de trabajo

- OpenFOAM Foundation 13.
- Ubuntu 24.04 LTS mediante WSL 2.
- Git y GitHub para control de versiones.
- ParaView para visualización.
