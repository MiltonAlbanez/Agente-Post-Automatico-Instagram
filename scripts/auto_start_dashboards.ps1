# Script PowerShell para Auto-Inicializacao dos Dashboards
# Inicia automaticamente os dashboards nas portas 5000 e 8502

param(
    [switch]$Silent,
    [switch]$CheckOnly,
    [switch]$Stop
)

# Configuracoes
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogFile = Join-Path $ProjectRoot "logs\dashboard_startup.log"
$PidFile = Join-Path $ProjectRoot "logs\dashboard_pids.txt"

# Criar diretorio de logs se nao existir
$LogDir = Split-Path -Parent $LogFile
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Funcao para log
function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    if (!$Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
            "WARN"  { Write-Host $LogMessage -ForegroundColor Yellow }
            "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
            default { Write-Host $LogMessage }
        }
    }
    
    Add-Content -Path $LogFile -Value $LogMessage
}

# Funcao para verificar se porta esta em uso
function Test-Port {
    param($Port)
    try {
        $Connection = New-Object System.Net.Sockets.TcpClient
        $Connection.Connect("localhost", $Port)
        $Connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Funcao para parar dashboards
function Stop-Dashboards {
    Write-Log "Parando dashboards..." "INFO"
    
    # Ler PIDs salvos
    if (Test-Path $PidFile) {
        $Pids = Get-Content $PidFile
        foreach ($Pid in $Pids) {
            if ($Pid -and $Pid -ne "") {
                try {
                    $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
                    if ($Process) {
                        Stop-Process -Id $Pid -Force
                        Write-Log "Processo $Pid parado" "SUCCESS"
                    }
                }
                catch {
                    Write-Log "Erro ao parar processo $Pid : $_" "WARN"
                }
            }
        }
        Remove-Item $PidFile -Force
    }
    
    # Parar processos por porta
    $Ports = @(5000, 8502)
    foreach ($Port in $Ports) {
        try {
            $Processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                         Select-Object -ExpandProperty OwningProcess | 
                         Sort-Object -Unique
            
            foreach ($ProcessId in $Processes) {
                $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
                if ($Process) {
                    Stop-Process -Id $ProcessId -Force
                    Write-Log "Processo na porta $Port parado (PID: $ProcessId)" "SUCCESS"
                }
            }
        }
        catch {
            Write-Log "Erro ao parar processos na porta $Port : $_" "WARN"
        }
    }
    
    Write-Log "Dashboards parados" "SUCCESS"
}

# Funcao para verificar status
function Get-DashboardStatus {
    $Status = @{
        Flask = @{
            Port = 5000
            Running = Test-Port 5000
            Name = "Dashboard A/B Testing"
        }
        Streamlit = @{
            Port = 8502
            Running = Test-Port 8502
            Name = "Dashboard de Automacao"
        }
    }
    
    Write-Log "Status dos Dashboards:" "INFO"
    foreach ($Dashboard in $Status.Keys) {
        $Info = $Status[$Dashboard]
        $StatusText = if ($Info.Running) { "ATIVO" } else { "INATIVO" }
        Write-Log "   $($Info.Name) (porta $($Info.Port)): $StatusText" "INFO"
    }
    
    return $Status
}

# Funcao para iniciar dashboard Flask
function Start-FlaskDashboard {
    Write-Log "Iniciando Dashboard A/B Testing (porta 5000)..." "INFO"
    
    $DashboardPath = Join-Path $ProjectRoot "dashboard\dashboard_server.py"
    
    if (!(Test-Path $DashboardPath)) {
        Write-Log "Arquivo dashboard_server.py nao encontrado!" "ERROR"
        return $null
    }
    
    try {
        $Process = Start-Process -FilePath "python" -ArgumentList $DashboardPath -WorkingDirectory $ProjectRoot -PassThru
        
        # Aguardar um pouco para verificar se iniciou
        Start-Sleep -Seconds 5
        
        if (!$Process.HasExited) {
            Write-Log "Dashboard Flask iniciado (PID: $($Process.Id))" "SUCCESS"
            return $Process.Id
        } else {
            Write-Log "Dashboard Flask falhou ao iniciar" "ERROR"
            return $null
        }
    }
    catch {
        Write-Log "Erro ao iniciar Dashboard Flask: $_" "ERROR"
        return $null
    }
}

# Funcao para iniciar dashboard Streamlit
function Start-StreamlitDashboard {
    Write-Log "Iniciando Dashboard de Automacao (porta 8502)..." "INFO"
    
    $DashboardPath = Join-Path $ProjectRoot "automation\automation_dashboard.py"
    
    if (!(Test-Path $DashboardPath)) {
        Write-Log "Arquivo automation_dashboard.py nao encontrado!" "ERROR"
        return $null
    }
    
    try {
        $Arguments = @(
            "-m", "streamlit", "run", 
            $DashboardPath,
            "--server.port", "8502",
            "--server.headless", "true"
        )
        
        $Process = Start-Process -FilePath "python" -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -PassThru
        
        # Aguardar um pouco para verificar se iniciou
        Start-Sleep -Seconds 8
        
        if (!$Process.HasExited) {
            Write-Log "Dashboard Streamlit iniciado (PID: $($Process.Id))" "SUCCESS"
            return $Process.Id
        } else {
            Write-Log "Dashboard Streamlit falhou ao iniciar" "ERROR"
            return $null
        }
    }
    catch {
        Write-Log "Erro ao iniciar Dashboard Streamlit: $_" "ERROR"
        return $null
    }
}

# Funcao para aguardar dashboards ficarem prontos
function Wait-ForDashboards {
    Write-Log "Aguardando dashboards ficarem prontos..." "INFO"
    
    $MaxAttempts = 30
    $Attempt = 0
    
    while ($Attempt -lt $MaxAttempts) {
        $FlaskReady = Test-Port 5000
        $StreamlitReady = Test-Port 8502
        
        if ($FlaskReady -and $StreamlitReady) {
            Write-Log "Ambos os dashboards estao prontos!" "SUCCESS"
            break
        }
        elseif ($FlaskReady) {
            Write-Log "Dashboard Flask pronto (porta 5000)" "SUCCESS"
        }
        elseif ($StreamlitReady) {
            Write-Log "Dashboard Streamlit pronto (porta 8502)" "SUCCESS"
        }
        
        Start-Sleep -Seconds 2
        $Attempt++
    }
    
    if ($Attempt -ge $MaxAttempts) {
        Write-Log "Timeout aguardando dashboards ficarem prontos" "WARN"
    }
}

# Funcao principal para iniciar dashboards
function Start-Dashboards {
    Write-Log "Iniciando sistema de dashboards..." "INFO"
    Write-Log "==================================================" "INFO"
    
    # Verificar se ja estao rodando
    $Status = Get-DashboardStatus
    
    $Pids = @()
    
    # Iniciar Flask se nao estiver rodando
    if (!$Status.Flask.Running) {
        $FlaskPid = Start-FlaskDashboard
        if ($FlaskPid) {
            $Pids += $FlaskPid
        }
    } else {
        Write-Log "Dashboard Flask ja esta rodando na porta 5000" "WARN"
    }
    
    # Aguardar um pouco entre inicializacoes
    Start-Sleep -Seconds 2
    
    # Iniciar Streamlit se nao estiver rodando
    if (!$Status.Streamlit.Running) {
        $StreamlitPid = Start-StreamlitDashboard
        if ($StreamlitPid) {
            $Pids += $StreamlitPid
        }
    } else {
        Write-Log "Dashboard Streamlit ja esta rodando na porta 8502" "WARN"
    }
    
    # Salvar PIDs
    if ($Pids.Count -gt 0) {
        $Pids | Out-File -FilePath $PidFile -Encoding UTF8
    }
    
    # Aguardar dashboards ficarem prontos
    Wait-ForDashboards
    
    Write-Log "==================================================" "INFO"
    Write-Log "Sistema de dashboards iniciado!" "SUCCESS"
    Write-Log "Dashboard A/B Testing: http://localhost:5000" "INFO"
    Write-Log "Dashboard de Automacao: http://localhost:8502" "INFO"
    Write-Log "==================================================" "INFO"
}

# Execucao principal
try {
    Write-Log "Script de Auto-Inicializacao dos Dashboards" "INFO"
    Write-Log "Projeto: $ProjectRoot" "INFO"
    
    if ($Stop) {
        Stop-Dashboards
    }
    elseif ($CheckOnly) {
        Get-DashboardStatus
    }
    else {
        Start-Dashboards
    }
}
catch {
    Write-Log "Erro inesperado: $_" "ERROR"
    exit 1
}

Write-Log "Script concluido" "SUCCESS"