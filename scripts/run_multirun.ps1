Param(
    [int]$Limit = 3
)

$ErrorActionPreference = "Stop"

# Navegar para a raiz do projeto deste script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

# Preparar pasta de logs
$logDir = Join-Path $projectRoot "logs"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logFile = Join-Path $logDir ("multirun-" + $timestamp + ".log")

# Rotação simples: manter no máximo 50 logs
$existing = Get-ChildItem -Path $logDir -Filter "multirun-*.log" | Sort-Object Name
if ($existing.Count -gt 50) {
    $toDelete = $existing | Select-Object -First ($existing.Count - 50)
    foreach ($f in $toDelete) { Remove-Item -Path $f.FullName -Force -ErrorAction SilentlyContinue }
}

# Escrever cabeçalho do log
"=== Multirun iniciado em $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $logFile -Encoding utf8
"Diretório do projeto: $projectRoot" | Out-File -FilePath $logFile -Append -Encoding utf8
"Limit: $Limit" | Out-File -FilePath $logFile -Append -Encoding utf8

# Executar via cmd com redirecionamento garantindo gravação mesmo em erros
$ErrorActionPreference = "Continue"
$venvDir = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts/python.exe"

# Garantir venv existente
if (!(Test-Path $venvPython)) {
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        & py -m venv $venvDir
    } else {
        & python -m venv $venvDir
    }
}

# Garantir dependências instaladas
$requirements = Join-Path $projectRoot "requirements.txt"
if (Test-Path $venvPython) {
    try {
        & $venvPython -m pip install --upgrade pip
        if (Test-Path $requirements) {
            & $venvPython -m pip install -r $requirements
        }
    } catch {
        "[WARN] Falha ao instalar dependências: $($_.Exception.Message)" | Out-File -FilePath $logFile -Append -Encoding UTF8
    }
}

# Selecionar executável de Python
if (Test-Path $venvPython) { $exe = $venvPython } else { $exe = "python" }
$exeQuoted = '"' + $exe + '"'
$logQuoted = '"' + $logFile + '"'
$env:PYTHONIOENCODING = "utf-8"
$cmdLine = "$exeQuoted src/main.py multirun --limit $Limit >> $logQuoted 2>&1"
& cmd /c $cmdLine
$exitCode = $LASTEXITCODE
"=== ExitCode: $exitCode ===" | Out-File -FilePath $logFile -Append -Encoding utf8
"=== Multirun finalizado em $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $logFile -Append -Encoding utf8