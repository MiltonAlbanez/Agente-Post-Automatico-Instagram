@echo off
REM Script de Inicialização Rápida dos Dashboards
REM Executa o script PowerShell para iniciar os dashboards

echo.
echo ========================================
echo   Trae IA - Inicializacao de Dashboards
echo ========================================
echo.

REM Verificar se PowerShell está disponível
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo ERRO: PowerShell nao encontrado!
    pause
    exit /b 1
)

REM Executar script PowerShell
echo Iniciando dashboards...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\auto_start_dashboards.ps1"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Dashboards iniciados com sucesso!
    echo ========================================
    echo.
    echo Dashboard A/B Testing: http://localhost:5000
    echo Dashboard de Automacao: http://localhost:8502
    echo.
    echo Pressione qualquer tecla para abrir os dashboards...
    pause >nul
    
    REM Abrir dashboards no navegador
    start http://localhost:5000
    start http://localhost:8502
) else (
    echo.
    echo ========================================
    echo   Erro ao iniciar dashboards!
    echo ========================================
    echo.
    echo Verifique os logs em: logs\dashboard_startup.log
    echo.
    pause
)

exit /b %errorlevel%