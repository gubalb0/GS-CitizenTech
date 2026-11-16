<#
.SYNOPSIS
  EXECUTA as simulacoes A (2 workers) e B (4 workers) no motor oficial do iSPD (modo terminal) usando os modelos JA EXISTENTES.
.DESCRIPTION
  Nao gera nem sobrescreve modelos/trace (use scripts\gerar_modelos.ps1). Recusa-se a rodar se resultados\A_2_workers ou
  resultados\B_4_workers ja existirem, salvo -SobrescreverResultados. -Verificar so checa pre-requisitos (nao compila nem simula).
  Pre-requisitos: JDK 17; iSPD compilado (build\classes\java\main, via .\gradlew build com JDK 17) e dependencias no cache do Gradle
  (ou -IspdJar). Veja o README.
.EXAMPLE
  .\scripts\executar.ps1 -IspdDir C:\ispd -JdkHome 'C:\Program Files\Eclipse Adoptium\jdk-17...' -Verificar
  .\scripts\executar.ps1 -IspdDir C:\ispd -JdkHome '...' -DetalheTarefas
#>
param(
    [string]$IspdDir, [string]$JdkHome, [string]$GradleCache, [string]$IspdJar,
    [string]$Raiz = (Split-Path -Parent $PSScriptRoot),
    [switch]$SobrescreverResultados, [switch]$Verificar, [switch]$DetalheTarefas
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_comum.ps1')

$amb = Resolve-Ambiente -IspdDir $IspdDir -JdkHome $JdkHome -GradleCache $GradleCache -IspdJar $IspdJar
$lista = @(@{ n = 'A_2_workers'; m = 'cenario_A_2_workers.imsx' }, @{ n = 'B_4_workers'; m = 'cenario_B_4_workers.imsx' })
if ($Verificar) {
    Testar-Cenarios -Raiz $Raiz -Lista $lista -Sobrescrever:$SobrescreverResultados
    Write-Host "VERIFICACAO OK (Java $($amb.JavaMajor)). Nada foi compilado nem executado."
    Write-Host "Classpath do iSPD: $($amb.IspdCp)"
    return
}
Invoke-Cenarios -Amb $amb -Raiz $Raiz -Lista $lista -Sobrescrever:$SobrescreverResultados -Detalhe:$DetalheTarefas
