# Auto Start Dashboards - Task Scheduler Setup
# Script para configurar inicializacao automatica dos dashboards

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

# Configuracoes
$TaskName = "AutoStartDashboards"
$ScriptPath = Join-Path $PSScriptRoot "auto_start_dashboards.ps1"
$WorkingDirectory = Split-Path $PSScriptRoot -Parent

function Show-Help {
    Write-Host ""
    Write-Host "=== CONFIGURADOR DE AUTO-INICIALIZACAO ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Uso:" -ForegroundColor White
    Write-Host "  .\setup_auto_start.ps1 -Install    # Instalar auto-inicializacao"
    Write-Host "  .\setup_auto_start.ps1 -Uninstall  # Remover auto-inicializacao"
    Write-Host "  .\setup_auto_start.ps1 -Status     # Verificar status"
    Write-Host ""
}

function Install-AutoStartTask {
    try {
        Write-Host ""
        Write-Host "Configurando auto-inicializacao dos dashboards..." -ForegroundColor Yellow
        
        # Verificar se o script existe
        if (-not (Test-Path $ScriptPath)) {
            Write-Host "ERRO: Script nao encontrado: $ScriptPath" -ForegroundColor Red
            return $false
        }
        
        # Remover tarefa existente se houver
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-Host "Removendo tarefa existente..." -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # Criar acao da tarefa
        $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`"" -WorkingDirectory $WorkingDirectory
        
        # Criar trigger para inicializacao
        $Trigger = New-ScheduledTaskTrigger -AtStartup
        
        # Configurar para executar com privilegios mais altos
        $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
        
        # Configuracoes da tarefa
        $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        # Registrar a tarefa
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Auto-inicializacao dos dashboards do sistema de automacao"
        
        Write-Host ""
        Write-Host "Configuracao concluida com sucesso!" -ForegroundColor Green
        Write-Host "Os dashboards serao iniciados automaticamente no proximo boot." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Dashboards configurados:" -ForegroundColor White
        Write-Host "  - Dashboard A/B Testing: http://localhost:5000" -ForegroundColor Gray
        Write-Host "  - Dashboard de Automacao: http://localhost:8502" -ForegroundColor Gray
        Write-Host ""
        
        return $true
    }
    catch {
        Write-Host "ERRO ao configurar auto-inicializacao: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Uninstall-AutoStartTask {
    try {
        Write-Host ""
        Write-Host "Removendo auto-inicializacao..." -ForegroundColor Yellow
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "Auto-inicializacao removida com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Nenhuma configuracao de auto-inicializacao encontrada." -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "ERRO ao remover auto-inicializacao: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-AutoStartStatus {
    Write-Host ""
    Write-Host "=== STATUS DA AUTO-INICIALIZACAO ===" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "Status: CONFIGURADO" -ForegroundColor Green
            Write-Host "Estado: $($task.State)" -ForegroundColor White
            Write-Host "Ultima execucao: $($task.LastRunTime)" -ForegroundColor White
            Write-Host "Proximo agendamento: $($task.NextRunTime)" -ForegroundColor White
            
            # Verificar se os dashboards estao rodando
            Write-Host ""
            Write-Host "Verificando dashboards..." -ForegroundColor Yellow
            
            $port5000 = Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet -WarningAction SilentlyContinue
            $port8502 = Test-NetConnection -ComputerName localhost -Port 8502 -InformationLevel Quiet -WarningAction SilentlyContinue
            
            if ($port5000) {
                Write-Host "  Dashboard A/B Testing (5000): ATIVO" -ForegroundColor Green
            } else {
                Write-Host "  Dashboard A/B Testing (5000): INATIVO" -ForegroundColor Red
            }
            
            if ($port8502) {
                Write-Host "  Dashboard de Automacao (8502): ATIVO" -ForegroundColor Green
            } else {
                Write-Host "  Dashboard de Automacao (8502): INATIVO" -ForegroundColor Red
            }
        } else {
            Write-Host "Status: NAO CONFIGURADO" -ForegroundColor Red
            Write-Host "Use -Install para configurar a auto-inicializacao" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "ERRO ao verificar status: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Execucao principal
if ($Install) {
    if (Install-AutoStartTask) {
        Write-Host ""
        Write-Host "Instalacao concluida!" -ForegroundColor Green
        Write-Host "Os dashboards serao iniciados automaticamente no proximo boot." -ForegroundColor Cyan
    }
}
elseif ($Uninstall) {
    if (Uninstall-AutoStartTask) {
        Write-Host ""
        Write-Host "Remocao concluida!" -ForegroundColor Green
        Write-Host "Os dashboards nao serao mais iniciados automaticamente" -ForegroundColor Cyan
    }
}
elseif ($Status) {
    Get-AutoStartStatus
}
else {
    Show-Help
}