@echo off
REM =============================================
REM Respaldo automático de la base gestor_multas
REM =============================================

set FECHA=%date:~-4%%date:~3,2%%date:~0,2%
set HORA=%time:~0,2%%time:~3,2%
set HORA=%HORA: =0%

set ARCHIVO=C:\respaldos\gestor_multas_%FECHA%_%HORA%.sql

"C:\xampp\mysql\bin\mysqldump.exe" -u root -p"NuevaContraseñaSegura2026!" gestor_multas > "%ARCHIVO%"

echo Respaldo generado: %ARCHIVO%