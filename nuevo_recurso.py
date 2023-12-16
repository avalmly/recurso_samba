#------------------------------------------------------------------------------------------
# Autor: Alberto Valero Mlynaricova
# Fecha: 16/12/2023
#
# Descripción:  Creará el recurso recurso1 solo permitirá conectarse a los usuarios del grupo   
#               alumnos que están disponible en directorio activo, en el caso de no existir el 
#               grupo será necesario crearlo usando powershell remoto al servidor de dominio
#------------------------------------------------------------------------------------------

import os
import sys
import subprocess
import pywinrm

recurso = sys.argv[1]
grupo = sys.argv[2]
ruta = f"/recursos/{recurso}"

with open("plantilla_recurso", 'r') as plantilla_recurso:
    lineas = plantilla_recurso.readlines()
            
# Realizar las sustituciones
lineas_modificadas = (
    lineas
    .replace('recurso', recurso)
    .replace('ruta', ruta)
    .replace('grupo', grupo)
)
            
samba_file = open("/etc/smb.conf", "a")             # modo append
samba_file.write(f'\n{lineas_modificadas}\n')       # Añade al final del fichero el recurso
samba_file.close()