Param(
  [string]$Style = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Ir para a raiz do projeto
Set-Location (Split-Path $PSScriptRoot -Parent)

# Ativar venv se existir
$activatePath = Join-Path (Split-Path $PSScriptRoot -Parent) ".venv/Scripts/Activate.ps1"
if (Test-Path $activatePath) {
  . $activatePath
}

# Selecionar estilo por horário, se não foi passado diretamente
if ($Style -eq "") {
  $hour = (Get-Date).Hour
  switch ($hour) {
    6  { if ($env:STYLE_06) { $Style = $env:STYLE_06 } }
    12 { if ($env:STYLE_12) { $Style = $env:STYLE_12 } }
    19 { if ($env:STYLE_19) { $Style = $env:STYLE_19 } }
  }
}

# Fallback geral
if ($Style -eq "") { $Style = $env:STYLE }

# Montar comando de autopost com fotos reais (usar alias compatível)
$cmd = "python src/main.py autopost --no-replicate"
if ($Style -ne "" -and $null -ne $Style) { $cmd += " --style `"$Style`"" }

Write-Host "Executando: $cmd"
Invoke-Expression $cmd