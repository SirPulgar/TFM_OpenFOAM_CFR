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

## RESUMEN DE COMANDOS ÚTILES — TFM OPENFOAM CFR

ACCEDER AL PROYECTO

Abrir Ubuntu/WSL y ejecutar:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR

Comprobar ruta:

pwd

Ruta esperada:

/home/javier/OpenFOAM/TFM_OpenFOAM_CFR

Comprobar estado de Git:

git status

Si OpenFOAM no estuviera activado:

source /opt/openfoam13/etc/bashrc

Comprobar versión:

echo $WM_PROJECT_VERSION

Resultado esperado:

13

RUTAS IMPORTANTES

Raíz del proyecto:

~/OpenFOAM/TFM_OpenFOAM_CFR

Malla estática:

cases/01_staticMesh

Malla dinámica:

cases/02_dynamicMesh

Compresión con aire:

cases/03_compressionFlow

Figuras:

docs/figures

Validaciones y postprocesos:

docs

Condiciones iniciales del caso compresible:

cases/03_compressionFlow/-180/U
cases/03_compressionFlow/-180/p
cases/03_compressionFlow/-180/T

CASO 01 — MALLA ESTÁTICA

Entrar en el caso:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR/cases/01_staticMesh

Generar malla:

blockMesh

Comprobar malla:

checkMesh

Guardar validación:

checkMesh > ../../docs/checkMesh_staticMesh.txt 2>&1

Abrir en ParaView:

paraFoam

Archivo principal:

cases/01_staticMesh/system/blockMeshDict

Evidencia:

docs/checkMesh_staticMesh.txt

Imagen:

docs/figures/malla_estatica_PMI.png

CASO 02 — MALLA DINÁMICA

Entrar en el caso:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR/cases/02_dynamicMesh

Limpiar malla generada:

rm -rf constant/polyMesh

Generar malla inicial:

blockMesh

Comprobar malla:

checkMesh

Ejecutar movimiento de malla:

foamRun

Comprobar malla en el último tiempo:

checkMesh -latestTime

Guardar validación en PMS:

checkMesh -latestTime > ../../docs/checkMesh_dynamicMesh_PMS.txt 2>&1

Abrir en ParaView:

paraFoam

Archivos principales:

cases/02_dynamicMesh/constant/dynamicMeshDict
cases/02_dynamicMesh/system/controlDict

Evidencias:

docs/checkMesh_dynamicMesh_-90CAD.txt
docs/checkMesh_dynamicMesh_PMS.txt

Imagen:

docs/figures/malla_dinamica_-90CAD.png

CASO 03 — COMPRESIÓN CON AIRE

Entrar en el caso:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR/cases/03_compressionFlow

Comprobar condiciones iniciales:

ls ./-180

Debe aparecer:

T U p

Comprobar valores iniciales:

foamDictionary ./-180/U -entry internalField
foamDictionary ./-180/p -entry internalField
foamDictionary ./-180/T -entry internalField

Valores esperados:

U = uniform (0 0 0)
p = uniform 101325
T = uniform 300

Archivos principales:

cases/03_compressionFlow/constant/dynamicMeshDict
cases/03_compressionFlow/constant/physicalProperties
cases/03_compressionFlow/constant/momentumTransport
cases/03_compressionFlow/system/controlDict
cases/03_compressionFlow/system/fvSchemes
cases/03_compressionFlow/system/fvSolution

CAMBIAR TIEMPO FINAL DE SIMULACIÓN

Entrar en el caso:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR/cases/03_compressionFlow

Editar:

nano system/controlDict

Para simular hasta -90 CAD:

endTime -90;

Para simular hasta PMS:

endTime 0;

Configuración habitual:

startTime -180;
deltaT 0.1;
writeInterval 10;

Comprobar configuración:

foamDictionary system/controlDict -entry startTime
foamDictionary system/controlDict -entry endTime
foamDictionary system/controlDict -entry deltaT
foamDictionary system/controlDict -entry writeInterval

EJECUTAR COMPRESIÓN CON AIRE

Entrar en el caso:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR/cases/03_compressionFlow

Limpiar resultados anteriores sin borrar -180:

find . -maxdepth 1 -type d -name '-*' ! -name '-180' -exec rm -rf -- {} +

Borrar posible carpeta 0:

rm -rf 0

Borrar malla generada:

rm -rf constant/polyMesh

Borrar logs y archivos auxiliares:

rm -f log.*
rm -f *.foam

Generar malla:

blockMesh

Comprobar malla:

checkMesh

Ejecutar simulación y guardar log:

foamRun | tee log.compression

Ver últimas líneas del log:

tail -40 log.compression

La simulación correcta debe terminar con:

End

GUARDAR VALIDACIÓN DE MALLA

Para -90 CAD:

checkMesh -latestTime > ../../docs/checkMesh_compression_-90CAD.txt 2>&1

Para PMS:

checkMesh -latestTime > ../../docs/checkMesh_compression_PMS.txt 2>&1

Comprobar final del archivo:

tail -20 ../../docs/checkMesh_compression_PMS.txt

Debe aparecer:

Mesh OK.
End

GUARDAR RESULTADOS FÍSICOS DE POSTPROCESO

Para guardar presión, temperatura y velocidad máxima del último tiempo calculado:

{
echo "Resultados de postproceso"
echo "Caso: 03_compressionFlow"
echo ""

foamPostProcess -latestTime -func 'volAverage(p)'
foamPostProcess -latestTime -func 'cellMin(p)'
foamPostProcess -latestTime -func 'cellMax(p)'

foamPostProcess -latestTime -func 'volAverage(T)'
foamPostProcess -latestTime -func 'cellMin(T)'
foamPostProcess -latestTime -func 'cellMax(T)'

foamPostProcess -latestTime -func 'cellMaxMag(U)'
} > ../../docs/postProcess_compression_PMS.txt 2>&1

Ver resultados resumidos:

grep -E "volAverageall|minall|maxall|maxMagall" ../../docs/postProcess_compression_PMS.txt

Para guardar resultados en -90 CAD, usar el mismo bloque, pero cambiando el archivo final a:

../../docs/postProcess_compression_-90CAD.txt

RESULTADOS PRINCIPALES OBTENIDOS

Compresión hasta -90 CAD:

Archivo:

docs/postProcess_compression_-90CAD.txt

Resultados:

Presión media: 206993.36 Pa
Presión mínima: 206992 Pa
Presión máxima: 206997.1 Pa

Temperatura media: 368.50178 K
Temperatura mínima: 368.50097 K
Temperatura máxima: 368.50492 K

Velocidad máxima: 3.7500777 m/s

Compresión hasta PMS / 0 CAD:

Archivo:

docs/postProcess_compression_PMS.txt

Resultados:

Presión media: 2572289.1 Pa
Presión mínima: 2572272.8 Pa
Presión máxima: 2572296.6 Pa

Temperatura media: 761.59559 K
Temperatura mínima: 761.56959 K
Temperatura máxima: 761.60133 K

Velocidad máxima: 1.3158225 m/s

COMPARACIÓN TEÓRICA USADA EN EL INFORME

Referencia: compresión adiabática ideal de gas perfecto.

Fórmulas:

p2 = p1 · (V1/V2)^gamma

T2 = T1 · (V1/V2)^(gamma - 1)

Datos usados:

p1 = 101325 Pa
T1 = 300 K
V1/V2 = 10
Cv = 712 J/(kg·K)
molWeight = 28.9 kg/kmol
R = 8314 / 28.9 ≈ 287.68 J/(kg·K)
gamma = (Cv + R) / Cv ≈ 1.404

Valores teóricos aproximados en PMS:

p_teórica ≈ 2568999 Pa
T_teórica ≈ 760.621 K

Valores OpenFOAM en PMS:

p_CFD = 2572289.1 Pa
T_CFD = 761.59559 K

Errores relativos:

Error presión ≈ 0.128 %
Error temperatura ≈ 0.128 %

Interpretación:

La simulación reproduce de forma muy cercana la compresión adiabática ideal. La desviación es pequeña y puede atribuirse a discretización temporal, discretización espacial, movimiento de malla, formulación numérica y redondeos acumulados.

LIMPIAR ANTES DE SUBIR A GITHUB

Desde la raíz del proyecto:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR

Eliminar resultados temporales conservando -180:

find cases/03_compressionFlow -maxdepth 1 -type d -name '-*' ! -name '-180' -exec rm -rf -- {} +

Borrar carpeta 0 si existe:

rm -rf cases/03_compressionFlow/0

Borrar malla generada:

rm -rf cases/03_compressionFlow/constant/polyMesh

Borrar logs:

rm -f cases/03_compressionFlow/log.*

Borrar archivos ParaView:

rm -f cases/03_compressionFlow/*.foam

Si aparece una carpeta de tiempo en notación científica, por ejemplo:

cases/03_compressionFlow/6.67793e-12/

borrarla con:

rm -rf cases/03_compressionFlow/6.67793e-12/

SUBIR CAMBIOS A GITHUB

Ir a la raíz del repositorio:

cd ~/OpenFOAM/TFM_OpenFOAM_CFR

Comprobar estado:

git status --short

Añadir archivos:

git add .

Crear commit:

git commit -m "mensaje del cambio"

Ejemplo:

git commit -m "feat: validar compresion completa hasta PMS"

Subir a GitHub:

git push

Comprobar que todo está limpio:

git status

Resultado esperado:

nothing to commit, working tree clean

QUÉ NO SUBIR A GITHUB

No subir:

constant/polyMesh/
postProcessing/
carpetas de tiempos generados: -170, -160, -90, 0, etc.
logs temporales
archivos .foam
carpetas de tiempo en notación científica

Sí subir:

system/blockMeshDict
system/controlDict
system/fvSchemes
system/fvSolution
constant/dynamicMeshDict
constant/physicalProperties
constant/momentumTransport
-180/U
-180/p
-180/T
docs/checkMesh_.txt
docs/postProcess_.txt
docs/figures/*.png

ESTADO TÉCNICO ACTUAL

Se ha conseguido:

Malla estática validada.
Malla dinámica validada desde -180 CAD hasta 0 CAD.
Movimiento del pistón mediante cinemática biela-manivela.
Compresión con aire hasta -90 CAD.
Compresión completa hasta PMS.
Comparación con compresión adiabática ideal.
Error aproximado en PMS: 0.128 % en presión y temperatura.

El modelo preliminar es válido para la entrega parcial como base CFD funcional con geometría simplificada, malla dinámica y compresión de aire en cilindro cerrado.
