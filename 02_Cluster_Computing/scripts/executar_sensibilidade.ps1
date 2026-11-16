<#
.SYNOPSIS
  EXECUTA a analise de sensibilidade A' (2 workers) e B' (4 workers), switch compartilhado, nos modelos JA EXISTENTES.
.DESCRIPTION
  Topologia DIFERENTE de A/B (ver README). Nao gera nem sobrescreve modelos/trace (use scripts\gerar_modelos.ps1 -Conjunto ApBp).
  Recusa-se a rodar se os diretorios de resultados ja existirem, salvo -SobrescreverResultados. -Verificar so checa pre-requisitos.
  Pre-requisitos iguais aos de executar.ps1. A'/B' NAO foram validados na GUI.
#>
param(
    [string]$IspdDir, [string]$JdkHome, [string]$GradleCache, [string]$IspdJar,
    [string]$Raiz = (Split-Path -Parent $PSScriptRoot),
    [switch]$SobrescreverResultados, [switch]$Verificar, [switch]$DetalheTarefas
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_comum.ps1')

$amb = Resolve-Ambiente -IspdDir $IspdDir -JdkHome $JdkHome -GradleCache $GradleCache -IspdJar $IspdJar
$lista = @(@{ n = 'Ap_2_workers_switch'; m = 'cenario_Ap_2_workers_switch.imsx' }, @{ n = 'Bp_4_workers_switch'; m = 'cenario_Bp_4_workers_switch.imsx' })
if ($Verificar) {
    Testar-Cenarios -Raiz $Raiz -Lista $lista -Sobrescrever:$SobrescreverResultados
    Write-Host "VERIFICACAO OK (Java $($amb.JavaMajor)). Nada foi compilado nem executado."
    Write-Host "Classpath do iSPD: $($amb.IspdCp)"
    return
}
Invoke-Cenarios -Amb $amb -Raiz $Raiz -Lista $lista -Sobrescrever:$SobrescreverResultados -Detalhe:$DetalheTarefas
