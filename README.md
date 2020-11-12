# Proyecto Digitalizacion FH 2020

Proyecto Digitalizacion FH 2020 recoge:
- (prepare.py) el script de preparacion 
- (/inputs) los ficheros de entrada (METS) 
- (/outputs) las salidas (MARCXML) para cargar a Zaguan.

## Instalación

Crear el virtualenv para python 2.7 y activarlo:

```
cd _uz-digitalizacion-arte-digital
virtualenv -p /usr/bin/python2.7 venv
source venv/bin/activate
```

Instalar los prerequisitos:
```
pip install -r requirements.txt
```

## Ejecución

```
python src/prepare.py
```
El script comprueba que los ficheros necesarios, que se cargarán a Zaguan vía FFT, estén accesibles en la ubicación esperada (biblos.unizar.es). Si no están disponibles, producirá un error.
Producirá un nuevo fichero en la carpeta outputs/ con la fecha de generación.

## Licencia
[MIT](https://choosealicense.com/licenses/mit/)

