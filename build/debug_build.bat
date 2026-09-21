@echo off
title Alien Unlock 2 - Debug Builder
cd /d "%~dp0"

set "NAME=Alien Unlock 2"
set "PYTHON=C:\users\xuser\AppData\Local\Programs\Python\Python314\python.exe"
set "HERE=%~dp0"
set "ROOT=%HERE%..\"
set "ICON=%HERE%icons\au2_icon.ico"
set "SPEC=%HERE%spec"
set "ENTRY=%ROOT%server.py"

set "TS=0000-00-00 00:00:00"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
if defined DT set "TS=%DT:~0,4%-%DT:~4,2%-%DT:~6,2% %DT:~8,2%:%DT:~10,2%:%DT:~12,2%"

echo ==========================================
echo [INFO] [%TS%] [^>] [INICIADO] Inicializando entorno de compilacion.
echo ==========================================

if not exist "%ENTRY%" (
    echo [ERROR] [%TS%] [X!] [FALLIDO] No se encontro el entry point: "%ENTRY%"
    pause
    exit /b 1
) else (
    echo [INFO] [%TS%] [=] [ENCONTRADO] Entry point detectado: %ENTRY%
)

if not exist "%ROOT%web" (
    echo [ERROR] [%TS%] [X!] [FALLIDO] No se encontro la carpeta web: "%ROOT%web"
    pause
    exit /b 1
) else (
    echo [INFO] [%TS%] [=] [ENCONTRADO] Carpeta web detectada: %ROOT%web
)

set "ICON_FLAG="
if exist "%ICON%" (
    set "ICON_FLAG=--icon "%ICON%""
    echo [INFO] [%TS%] [=] [ENCONTRADO] Icono detectado: %ICON%
) else (
    echo [WARNING] [%TS%] [!] [ADVERTENCIA] Icono no encontrado en "%ICON%". Se compilara sin icono.
)

call :clean
if errorlevel 1 exit /b 1

call :pyInstaller
if errorlevel 1 exit /b 1

echo.
echo ==========================================
echo [INFO] [%TS%] [OK] [EXITO] Compilacion completada exitosamente.
echo ==========================================
pause
exit /b 0


:pyInstaller
echo [INFO] [%TS%] [^>] [INICIADO] Ejecutando PyInstaller (onedir)...

"%PYTHON%" -m PyInstaller ^
    --onedir ^
    --console ^
    --noupx ^
    --noconfirm ^
    --uac-admin ^
    --contents-directory "." ^
    %ICON_FLAG% ^
    --add-data "%ROOT%web;web" ^
    --distpath "%ROOT%dist" ^
    --specpath "%SPEC%" ^
    --name "%NAME%" "%ENTRY%"

if errorlevel 1 (
    echo [ERROR] [%TS%] [X!] [FALLIDO] PyInstaller fallo.
    exit /b 1
)

echo [INFO] [%TS%] [^<] [FINALIZADO] PyInstaller completado.
exit /b 0


:clean
echo [INFO] [%TS%] [~^>] [CARGANDO] Limpiando archivos de compilaciones anteriores...

if exist "%ROOT%dist" (
    rmdir /S /Q "%ROOT%dist"
    echo [INFO] [%TS%] [^^] [ELIMINADO] Carpeta 'dist' eliminada.
) else (
    echo [WARNING] [%TS%] [!] [ADVERTENCIA] Carpeta 'dist' no encontrada.
)

if exist "%SPEC%" (
    rmdir /S /Q "%SPEC%"
    echo [INFO] [%TS%] [^^] [ELIMINADO] Carpeta 'spec' eliminada.
) else (
    echo [WARNING] [%TS%] [!] [ADVERTENCIA] Carpeta 'spec' no encontrada.
)

echo [INFO] [%TS%] [^<] [FINALIZADO] Limpieza completada.
exit /b 0