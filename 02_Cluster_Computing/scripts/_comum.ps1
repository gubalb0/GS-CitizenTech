# Funcoes compartilhadas pelos scripts (use com dot-sourcing: . "$PSScriptRoot\_comum.ps1").
# Nenhum caminho especifico de computador e embutido: iSPD, JDK e cache do Gradle vem de parametros ou variaveis de ambiente.
# Testado apenas em Windows PowerShell 5.1 (Windows 11). Outros sistemas/versoes: NAO verificado.

function Resolve-Ambiente {
    param([string]$IspdDir, [string]$JdkHome, [string]$GradleCache, [string]$IspdJar)

    if (-not $IspdDir)     { $IspdDir = $env:ISPD_DIR }
    if (-not $JdkHome)     { $JdkHome = if ($env:ISPD_JDK_HOME) { $env:ISPD_JDK_HOME } else { $env:JAVA_HOME } }
    if (-not $GradleCache) { $GradleCache = if ($env:GRADLE_USER_HOME) { $env:GRADLE_USER_HOME } else { Join-Path $HOME '.gradle' } }
    if (-not $IspdJar)     { $IspdJar = $env:ISPD_JAR }

    if (-not $IspdDir -or -not (Test-Path $IspdDir)) {
        throw "Pasta do iSPD nao encontrada. Informe -IspdDir ou defina ISPD_DIR (pasta que contem build.gradle e src\)."
    }
    if (-not $JdkHome -or -not (Test-Path (Join-Path $JdkHome 'bin'))) {
        throw "JDK nao encontrado. Informe -JdkHome ou defina ISPD_JDK_HOME/JAVA_HOME (precisa de bin\java e bin\javac, JDK 17)."
    }
    $sufixo = if ($IsLinux -or $IsMacOS) { '' } else { '.exe' }
    $java  = Join-Path $JdkHome "bin\java$sufixo"
    $javac = Join-Path $JdkHome "bin\javac$sufixo"
    if (-not (Test-Path $java) -or -not (Test-Path $javac)) {
        throw "Nao ha java/javac em $JdkHome\bin (e necessario um JDK, nao apenas um JRE)."
    }

    # Versao do Java: o codigo do iSPD usa recursos de Java >= 16; o projeto foi compilado/executado aqui com JDK 17.
    $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $txt = (& $java -version 2>&1 | ForEach-Object { "$_" }) -join ' '
    $ErrorActionPreference = $prev
    if ($txt -notmatch 'version "(\d+)(?:\.(\d+))?') { throw "Nao foi possivel ler a versao do Java: $txt" }
    $major = if ($Matches[1] -eq '1') { [int]$Matches[2] } else { [int]$Matches[1] }
    if ($major -lt 17) { throw "Java $major encontrado em $JdkHome; use JDK 17 (testado) - o codigo do iSPD exige Java >= 16." }
    if ($major -gt 17) { Write-Warning "Java $major em uso; somente JDK 17 foi testado neste projeto." }

    $sep = [IO.Path]::PathSeparator
    if ($IspdJar) {
        if (-not (Test-Path $IspdJar)) { throw "IspdJar nao encontrado: $IspdJar" }
        $cp = $IspdJar
    } else {
        $classes = Join-Path $IspdDir 'build\classes\java\main'
        $recursos = Join-Path $IspdDir 'build\resources\main'
        if (-not (Test-Path $classes)) {
            throw "iSPD nao compilado: falta $classes. Compile antes: (cd $IspdDir ; .\gradlew build) com JDK 17. Alternativa: -IspdJar com o jar de './gradlew shadowJar'."
        }
        $nomes = 'commons-cli-1.4.jar','jfreechart-1.0.14.jar','jcommon-1.0.17.jar','itext-2.1.5.jar','bcmail-jdk14-138.jar','bcprov-jdk14-138.jar'
        $jars = @()
        foreach ($n in $nomes) {
            $achado = Get-ChildItem -Path $GradleCache -Recurse -Filter $n -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $achado) { throw "Dependencia $n nao encontrada em $GradleCache. Rode o build do iSPD nesta maquina ou use -IspdJar/-GradleCache." }
            $jars += $achado.FullName
        }
        $cp = (@($classes, $recursos) + $jars) -join $sep
    }
    return @{ Java = $java; Javac = $javac; IspdCp = $cp; IspdDir = $IspdDir; JavaMajor = $major; Sep = $sep }
}

function Compilar-Drivers {
    param($Amb, [string]$Raiz)
    $out = Join-Path $Raiz 'driver\out'
    New-Item -ItemType Directory -Force $out | Out-Null
    $fontes = 'GerarModelos.java','SimularModelo.java','GerarModelosCluster.java' | ForEach-Object { Join-Path $Raiz "driver\$_" }
    & $Amb.Javac -encoding UTF-8 -cp "$out$($Amb.Sep)$($Amb.IspdCp)" -d $out @fontes
    if ($LASTEXITCODE -ne 0) { throw "Falha ao compilar os drivers (javac retornou $LASTEXITCODE)." }
    return $out
}

function Obter-CaminhoDoTrace {
    param([string]$Modelo)
    $m = Select-String -Path $Modelo -Pattern 'file_path="([^"]*)"' | Select-Object -First 1
    if (-not $m) { return $null }
    return $m.Matches[0].Groups[1].Value
}

# Verifica pre-requisitos de uma lista de cenarios @{n=pasta_resultado; m=arquivo_modelo}. Nao executa nem altera nada.
# O trace referenciado pelo .imsx (caminho ABSOLUTO) deve ser exatamente o trace deste projeto (<Raiz>\trace\carga_citizentech_400.trace);
# um trace que existe na maquina mas pertence a outra pasta/copia e REPROVADO. Todos os problemas sao reunidos e reportados juntos.
function Testar-Cenarios {
    param([string]$Raiz, $Lista, [switch]$Sobrescrever)
    $esperado = [IO.Path]::GetFullPath((Join-Path $Raiz 'trace\carga_citizentech_400.trace'))
    $comparacao = if ($IsLinux) { [StringComparison]::Ordinal } else { [StringComparison]::OrdinalIgnoreCase }
    $erros = @()
    foreach ($c in $Lista) {
        $modelo = Join-Path $Raiz "modelos\$($c.m)"
        if (-not (Test-Path -LiteralPath $modelo)) {
            $erros += "Modelo ausente: $modelo. Gere-o com scripts\gerar_modelos.ps1 (o modelo NAO e gerado por este script)."
        } else {
            $trace = Obter-CaminhoDoTrace $modelo
            $dicaRegenerar = "Nenhum arquivo foi alterado. Para apontar o modelo para este projeto: scripts\gerar_modelos.ps1 -Regenerar (muda o hash do .imsx; o do trace permanece)."
            if (-not $trace) {
                $erros += "O modelo '$($c.m)' nao contem <trace file_path=...>. $dicaRegenerar"
            } elseif (-not [IO.Path]::IsPathRooted($trace)) {
                $erros += "O modelo '$($c.m)' usa caminho de trace RELATIVO ('$trace'); so caminhos absolutos do trace deste projeto sao aceitos. Esperado: '$esperado'. $dicaRegenerar"
            } else {
                $achado = $null
                try { $achado = [IO.Path]::GetFullPath($trace) } catch { }
                if (-not $achado) {
                    $erros += "O modelo '$($c.m)' tem caminho de trace invalido: '$trace'. Esperado: '$esperado'. $dicaRegenerar"
                } elseif (-not [string]::Equals($achado, $esperado, $comparacao)) {
                    $situacao = if (Test-Path -LiteralPath $achado) { 'o arquivo existe nesta maquina, mas NAO pertence a este projeto (outra pasta/copia)' } else { 'o arquivo tambem nao existe' }
                    $erros += "O modelo '$($c.m)' referencia um trace FORA do projeto atual. Encontrado: '$achado' ($situacao). Esperado: '$esperado'. $dicaRegenerar"
                } elseif (-not (Test-Path -LiteralPath $esperado)) {
                    $erros += "O modelo '$($c.m)' aponta para o trace deste projeto, mas o arquivo nao existe: '$esperado'. Gere-o com scripts\gerar_modelos.ps1."
                }
            }
        }
        $dir = Join-Path $Raiz "resultados\$($c.n)"
        if ((Test-Path -LiteralPath $dir) -and -not $Sobrescrever) {
            $erros += "Resultados ja existem: $dir. Nada foi executado. Use -SobrescreverResultados para substituir (ou outra -Raiz)."
        }
    }
    if ($erros.Count -gt 0) { throw ($erros -join [Environment]::NewLine) }
}

function Invoke-Cenarios {
    param($Amb, [string]$Raiz, $Lista, [switch]$Sobrescrever, [switch]$Detalhe)
    Testar-Cenarios -Raiz $Raiz -Lista $Lista -Sobrescrever:$Sobrescrever
    $out = Compilar-Drivers -Amb $Amb -Raiz $Raiz
    foreach ($c in $Lista) {
        $modelo = Join-Path $Raiz "modelos\$($c.m)"
        $dir = Join-Path $Raiz "resultados\$($c.n)"
        New-Item -ItemType Directory -Force $dir | Out-Null
        Push-Location $dir   # o motor pode gravar arquivos auxiliares no diretorio corrente; usamos a pasta do cenario
        try {
            $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'   # o iSPD escreve avisos de DTD em stderr
            # 1) Execucao oficial: ispd.Main em modo terminal (-in modelo, -o pasta do HTML)
            $r = & $Amb.Java '-Djava.awt.headless=true' -cp $Amb.IspdCp ispd.Main -in $modelo -o (Join-Path $dir 'html') 2>&1 | ForEach-Object { "$_" }
            $r | Out-File -Encoding utf8 (Join-Path $dir 'console_ispd.txt'); $r | Write-Host
            # 2) Complemento (mesmo motor): tarefas por worker (+ detalhe por tarefa, opcional)
            $args2 = @($modelo, (Join-Path $dir 'tarefas_por_worker.csv'))
            if ($Detalhe) { $args2 += (Join-Path $dir 'tarefas_detalhe.csv') }
            $r = & $Amb.Java '-Djava.awt.headless=true' -cp "$out$($Amb.Sep)$($Amb.IspdCp)" SimularModelo @args2 2>&1 | ForEach-Object { "$_" }
            $r | Out-File -Encoding utf8 (Join-Path $dir 'console_driver.txt'); $r | Write-Host
            $ErrorActionPreference = $prev
        } finally { Pop-Location }
    }
}
