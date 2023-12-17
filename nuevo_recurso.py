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

def crear_grupo_ad(host, usuario, contrasena, grupo):
    # Rutas de las claves SSH
    private_key_path = os.path.expanduser("~/.ssh/id_rsa")

    # Verificar si la clave privada ya existe
    if os.path.exists(private_key_path):
        print("La clave privada ya existe.")
    else:
        # Generar clave privada y pública si no existen
        os.system(f"ssh-keygen -t rsa -f {private_key_path} -N ''")
        print("Claves generadas con éxito.")

    # Comando para copiar la clave pública al servidor
    copy_key_cmd = f"sshpass -p '{contrasena}' ssh-copy-id -i {private_key_path}.pub {usuario}@{host}"

    # Verificar si la clave pública ya está en el servidor
    result = os.system(copy_key_cmd)

    if result == 0:
        print("Clave pública copiada con éxito al servidor.")
    else:
        print("Error al copiar la clave pública al servidor.")

    # Comando PowerShell para crear un grupo en Active Directory
    script_ps = f'New-ADGroup -Name "{grupo}" -GroupScope Global'       # Al no especificar GroupSecurity, se crea uno de Seguridad por defecto
    
    # Comando de ejecución
    cmd_ssh = f'sshpass -p "{contrasena}" ssh {usuario}@{host}'
    cmd = (
        f'{cmd_ssh} \'powershell -NoProfile -NonInteractive -Command "$password = ConvertTo-SecureString -String \'{contrasena}\' -AsPlainText -Force; $cred = New-Object -TypeName PSCredential -ArgumentList \'{usuario}\', $password; Invoke-Command -Credential $cred -ScriptBlock {{ {script_ps} }} -ArgumentList "\'$grupo\'"\''
    )

    #cmd = f'{cmd_ssh} \'powershell -NoProfile -NonInteractive -Command "$password = ConvertTo-SecureString -String \'{contrasena}\' -AsPlainText -Force; $cred = New-Object -TypeName PSCredential -ArgumentList \'{usuario}\', $password; Invoke-Command -Credential $cred -ScriptBlock {{ {script_ps} }}"\''

    # Ejecutar el comando
    subprocess.run(cmd, shell=True)

    print(f"Grupo '{grupo}' creado con éxito en Active Directory.")

def check_grupo(host, usuario, contrasena, grupo):
    lista_grupos = subprocess.run(['getent', 'group'], capture_output=True, text=True)
    if grupo not in lista_grupos.stdout:
        print("El grupo especificado no existe. Creando grupo...")
        crear_grupo_ad(host, usuario, contrasena, grupo)

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
