# Requires: Railway CLI installed and authenticated
# Usage examples:
#   powershell -ExecutionPolicy Bypass -File scripts/apply_cron_config.ps1 -DryRun
#   powershell -ExecutionPolicy Bypass -File scripts/apply_cron_config.ps1 -ApplyVariables

param(
    [switch]$DryRun = $true,
    [switch]$ApplyVariables = $false,
    [string]$JsonPath = "railway_cron_config.json"
)

function Ensure-FileExists($path) {
    if (-not (Test-Path $path)) {
        Write-Error "Arquivo não encontrado: $path"
        exit 1
    }
}

function Read-CronConfig($path) {
    $raw = Get-Content -Path $path -Encoding UTF8 | Out-String
    return $raw | ConvertFrom-Json
}

function Load-ProjectMap() {
    Write-Host "Carregando lista de projetos do Railway..." -ForegroundColor DarkYellow
    try {
        $jsonLines = & railway list --json
        $jsonText = ($jsonLines -join "`n")
        $obj = $jsonText | ConvertFrom-Json
        $map = @{}
        foreach ($proj in $obj) {
            if ($proj.name -and $proj.id) { $map[$proj.name] = $proj.id }
        }
        Write-Host ("Projetos carregados: " + ($map.Keys -join ", ")) -ForegroundColor DarkYellow
        return $map
    } catch {
        Write-Warning "Falha ao carregar projetos via CLI: $($_.Exception.Message)"
        return @{}
    }
}

function Show-ServicePlan($svc) {
    Write-Host "\n=== Serviço: $($svc.service_name) ===" -ForegroundColor Cyan
    Write-Host ("- Cron (UTC): {0}" -f $svc.schedule)
    Write-Host ("- Start Command: {0}" -f $svc.start_command)
    Write-Host "- Variáveis sugeridas:"
    foreach ($prop in $svc.env.PSObject.Properties) {
        Write-Host ("  • {0}={1}" -f $prop.Name, $prop.Value)
    }
}

function Apply-Variables($svc) {
    # Observação: algumas operações (cron schedule) não são suportadas via CLI
    # Este passo seta variáveis por serviço, quando possível.
    $envPairs = @()
    foreach ($prop in $svc.env.PSObject.Properties) {
        $envPairs += ("{0}={1}" -f $prop.Name, $prop.Value)
    }
    $args = @('variables')
    foreach ($pair in $envPairs) { $args += @('--set', $pair) }
    $projId = $Global:ProjectMap[$svc.service_name]
    if ($projId) {
        Write-Host ("Executando: railway link --project " + $projId) -ForegroundColor Yellow
        try { & railway link --project $projId } catch { Write-Warning "Falha ao vincular projeto por ID: $projId. $_" }
    } else {
        Write-Warning ("ID do projeto não encontrado para nome: " + $svc.service_name)
        Write-Host ("Executando: railway link --project (nome) " + $svc.service_name) -ForegroundColor Yellow
        try { & railway link --project $svc.service_name } catch { Write-Warning "Falha ao vincular projeto por nome: $($svc.service_name). $_" }
    }
    Write-Host ("Executando: railway " + ($args -join ' ')) -ForegroundColor Yellow
    try {
        & railway @args
    } catch {
        Write-Warning "Falha ao executar comando de variáveis. Ajuste manual pela UI se necessário. Detalhes: $($_.Exception.Message)"
    }
}

function Show-ManualSteps($svc) {
    Write-Host "\nAjustes manuais necessários (UI):" -ForegroundColor Magenta
    Write-Host "1) Settings → Cron: definir expressão (UTC): $($svc.schedule)"
    Write-Host "2) Deploy → Start Command:"
    Write-Host "   $($svc.start_command)"
    Write-Host "3) Settings → Variables: conferir/definir:" 
    foreach ($prop in $svc.env.PSObject.Properties) {
        Write-Host ("   - {0}={1}" -f $prop.Name, $prop.Value)
    }
}

Write-Host "Aplicando configuração dos 5 serviços usando: $JsonPath" -ForegroundColor Green
Ensure-FileExists -path $JsonPath
$cfg = Read-CronConfig -path $JsonPath
$Global:ProjectMap = Load-ProjectMap

if (-not $cfg.services) {
    Write-Error "Nenhum serviço encontrado em $JsonPath"
    exit 1
}

foreach ($svc in $cfg.services) {
    Show-ServicePlan -svc $svc
    if ($ApplyVariables) {
        Apply-Variables -svc $svc
    }
    Show-ManualSteps -svc $svc
}

Write-Host "\nConcluído. Revise os logs após os próximos horários agendados." -ForegroundColor Green
Write-Host "Dica: railway logs --timestamp | findstr /I /C:\"ERROR\" /C:\"Traceback\"" -ForegroundColor DarkGray