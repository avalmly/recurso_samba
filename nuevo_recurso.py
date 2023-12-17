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
import winrm

def check_grupo(host, usuario, contrasena, grupo):
    lista_grupos = subprocess.run(['getent', 'group'], capture_output=True, text=True)
    if (grupo not in lista_grupos):
        print("El grupo especificado no existe. Creando grupo...")
        crear_grupo_ad(host, usuario, contrasena, grupo)
        
def crear_grupo_ad(host, usuario, contrasena, grupo):
    sesion = winrm.Session(
        host, 
        auth=(usuario, contrasena),
        server_cert_validation='ignore'                                 # Ignora la validación del certificado en entornos de prueba
    )

    # Comando PowerShell para crear un grupo en Active Directory
    script_ps = f'New-ADGroup -Name "{grupo}" -GroupScope Global'       # Al no especificar GroupSecurity, se crea uno de Seguridad por defecto

    # Ejecuta el script
    resultado = sesion.run_ps(script_ps)

    # Imprime el resultado
    print(resultado.std_out.decode('utf-8'))

def crea_recurso(recurso, ruta, grupo):
    with open("plantilla_recurso", 'r') as plantilla_recurso:
        lineas = plantilla_recurso.read()
            
    # Realizar las sustituciones
    lineas_modificadas = (
        lineas
        .replace('recurso', recurso)
        .replace('ruta', ruta)
        .replace('grupo', grupo)
    )
            
    samba_file = open("/etc/samba/smb.conf", "a")                       # modo append
    samba_file.write(f'\n{lineas_modificadas}\n')                       # Añade al final del fichero el recurso
    samba_file.close()


recurso = sys.argv[1]
grupo = sys.argv[2]
ruta = f"/recursos/{recurso}"
host = "serverad"
usuario = "administrador"
password = "Departamento1!"

check_grupo(host, usuario, password, grupo)
