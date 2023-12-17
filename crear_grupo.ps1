# Contenido de crear_grupo.ps1
param (
    [string]$grupo
)

New-ADGroup -Name $grupo -GroupScope Global