<#
.SYNOPSIS
  GERA (nao executa) o trace compartilhado e os modelos .imsx, usando o escritor oficial IconicoXML do iSPD.
.DESCRIPTION
  Por padrao NAO sobrescreve arquivos existentes (informa "MANTIDO"). Use -Regenerar para reescrever trace e modelos.
  Atencao: o .imsx guarda o caminho ABSOLUTO do trace; ao gerar em outra pasta/maquina o hash do .imsx muda
  (o hash do trace nao). Gerar nao roda simulacao alguma.
  O script so termina com sucesso se o Java retornar 0, se os arquivos esperados existirem e, quando -Regenerar for pedido,
  se nenhum arquivo tiver sido "MANTIDO".
.PARAMETER Conjunto  AB (A e B: links dedicados + trace) | ApBp (A' e B': switch compartilhado) | Todos (padrao)
.PARAMETER IspdDir / JdkHome / GradleCache / IspdJar  Ou variaveis ISPD_DIR, ISPD_JDK_HOME (ou JAVA_HOME), GRADLE_USER_HOME, ISPD_JAR.
.EXAMPLE
  .\scripts\gerar_modelos.ps1 -IspdDir C:\ispd -JdkHome 'C:\Program Files\Eclipse Adoptium\jdk-17...'
#>
param(
    [ValidateSet('AB', 'ApBp', 'Todos')] [string]$Conjunto = 'Todos',
    [switch]$Regenerar,
    [string]$IspdDir, [string]$JdkHome, [string]$GradleCache, [string]$IspdJar,
    [string]$Raiz = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_comum.ps1')

$amb = Resolve-Ambiente -IspdDir $IspdDir -JdkHome $JdkHome -GradleCache $GradleCache -IspdJar $IspdJar
$out = Compilar-Drivers -Amb $amb -Raiz $Raiz
$cp = "$out$($amb.Sep)$($amb.IspdCp)"

function Invoke-Gerador {
    param([string]$Classe)
    # Lista de argumentos montada elemento a elemento (cada item vira UM argumento do Java). Nao usar
    # "$x = if (...) { @('a') }": no PowerShell 5.1 o array de 1 elemento vira string e o splat a separa em caracteres.
    $argumentos = @('-cp', $cp, $Classe, $Raiz)
    if ($Regenerar) { $argumentos += '--regenerar' }
    $saida = & $amb.Java @argumentos
    $codigo = $LASTEXITCODE
    $saida | ForEach-Object { Write-Host $_ }
    if ($codigo -ne 0) { throw "$Classe falhou (java retornou $codigo). A geracao NAO foi concluida." }
    if ($Regenerar -and (($saida | Out-String) -match 'MANTIDO')) {
        throw "-Regenerar foi solicitado, mas $Classe informou MANTIDO para algum arquivo: o argumento --regenerar nao foi aplicado. A geracao NAO foi concluida."
    }
}

$esperados = @()
if ($Conjunto -in 'AB', 'Todos') { Invoke-Gerador 'GerarModelos'; $esperados += 'trace\carga_citizentech_400.trace', 'modelos\cenario_A_2_workers.imsx', 'modelos\cenario_B_4_workers.imsx' }
if ($Conjunto -in 'ApBp', 'Todos') { Invoke-Gerador 'GerarModelosCluster'; $esperados += 'trace\carga_citizentech_400.trace', 'modelos\cenario_Ap_2_workers_switch.imsx', 'modelos\cenario_Bp_4_workers_switch.imsx' }
foreach ($e in ($esperados | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath (Join-Path $Raiz $e))) { throw "Arquivo esperado ausente apos a geracao: $e. A geracao NAO foi concluida." }
}
Write-Host "Concluido. Nenhuma simulacao foi executada. Para simular: scripts\executar.ps1 e scripts\executar_sensibilidade.ps1."
