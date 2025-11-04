<#
  Railway Quick Commands (Windows)
  - Funções para executar comandos comuns com o Railway, usando python explícito
  - Estilo padrão: "isometric, minimalista"

  Uso:
    1) No PowerShell, rode: .\scripts\railway_quick_commands.ps1
    2) Chame as funções, por exemplo:
       Invoke-RailwayAutopost -DisableReplicate -Style "isometric, minimalista" -Tags "empreendedorismo,coaching,pnl"
       Invoke-RailwayUnposted -Limit 10
       Invoke-RailwayCollectUsers -Users "milton_albanez"
       Invoke-RailwayGenerate -ImageUrl "https://exemplo.com/img.jpg" -Style "isometric, minimalista"
       Invoke-RailwayClearCache -Older 3600
       Set-RailwayHelperVariables -AccountName "Milton_Albanez" -Limit 1 -Style "isometric, minimalista"

  Observações:
    - Requer Railway CLI instalado e linkado ao projeto (railway link)
    - As funções mudam o diretório de trabalho para a raiz do projeto durante a execução
#>

$ErrorActionPreference = 'Stop'
$DefaultStyle = 'isometric, minimalista'
$ProjectRoot = Split-Path $PSScriptRoot -Parent

function Assert-RailwayAvailable {
  $cmd = Get-Command railway -ErrorAction SilentlyContinue
  if (-not $cmd) {
    Write-Error 'Railway CLI não encontrado. Instale via: npm i -g railway'
  }
}

function Invoke-InProjectRoot {
  param(
    [Parameter(Mandatory=$true)] [ScriptBlock] $Script
  )
  Push-Location $ProjectRoot
  try { & $Script } finally { Pop-Location }
}

function Invoke-RailwayUnposted {
  param([int] $Limit = 10)
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    & railway run python src/main.py unposted --limit $Limit
  }
}

function Invoke-RailwayAutopost {
  param(
    [string] $Style = $DefaultStyle,
    [switch] $DisableReplicate,
    [string] $Tags
  )
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    $argsList = @('python','src/main.py','autopost')
    if ($DisableReplicate) { $argsList += '--no-replicate' }
    $argsList += @('--style', $Style)
    if ($Tags) { $argsList += @('--tags', $Tags) }
    & railway run @argsList
  }
}

function Invoke-RailwayCollectUsers {
  param([Parameter(Mandatory=$true)] [string] $Users)
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    & railway run python src/main.py collect_users --users $Users
  }
}

function Invoke-RailwayGenerate {
  param(
    [Parameter(Mandatory=$true)] [string] $ImageUrl,
    [string] $Style = $DefaultStyle
  )
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    & railway run python src/main.py generate --image_url $ImageUrl --style $Style
  }
}

function Invoke-RailwayClearCache {
  param(
    [int] $Older = 3600,
    [string] $UrlContains,
    [string] $Path
  )
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    $argsList = @('python','src/main.py','clear_cache','--older',$Older)
    if ($UrlContains) { $argsList += @('--url-contains', $UrlContains) }
    if ($Path) { $argsList += @('--path', $Path) }
    & railway run @argsList
  }
}

function Set-RailwayHelperVariables {
  param(
    [string] $AccountName = 'Milton_Albanez',
    [int] $Limit = 1,
    [string] $Style = $DefaultStyle
  )
  Assert-RailwayAvailable
  Invoke-InProjectRoot {
    & railway variables --set "ACCOUNT_NAME=$AccountName" --set "LIMIT=$Limit" --set "STYLE=$Style" --skip-deploys
  }
}

# Aliases práticos
Set-Alias rUnposted Invoke-RailwayUnposted
Set-Alias rAutopost Invoke-RailwayAutopost
Set-Alias rCollectUsers Invoke-RailwayCollectUsers
Set-Alias rGenerate Invoke-RailwayGenerate
Set-Alias rClearCache Invoke-RailwayClearCache
Set-Alias rSetVars Set-RailwayHelperVariables

Write-Host 'Railway Quick Commands carregado. Exemplos:' -ForegroundColor Cyan
Write-Host '  rUnposted -Limit 10' -ForegroundColor Cyan
Write-Host '  rAutopost -DisableReplicate -Style "isometric, minimalista" -Tags "empreendedorismo,coaching,pnl"' -ForegroundColor Cyan
Write-Host '  rCollectUsers -Users "milton_albanez"' -ForegroundColor Cyan
Write-Host '  rGenerate -ImageUrl "https://exemplo.com/img.jpg" -Style "isometric, minimalista"' -ForegroundColor Cyan
Write-Host '  rClearCache -Older 3600' -ForegroundColor Cyan
Write-Host '  rSetVars -AccountName "Milton_Albanez" -Limit 1 -Style "isometric, minimalista"' -ForegroundColor Cyan