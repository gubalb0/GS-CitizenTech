// Gera o relatório da GBA em .docx (ABNT/FIAP).
// Uso: node gerar_relatorio.js <saida.docx> [paginas.json]
// paginas.json (opcional) traz o número de página de cada título, figura e quadro,
// calculado a partir de uma primeira renderização, para preencher sumário e listas.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, HeadingLevel, PageBreak, Header, PageNumber, ShadingType, BorderStyle,
  LevelFormat, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
  VerticalAlign, SectionType, TabStopType, LeaderType,
} = require("docx");

const SAIDA = process.argv[2] || "relatorio.docx";
const PAGINAS = process.argv[3] && fs.existsSync(process.argv[3]) ? JSON.parse(fs.readFileSync(process.argv[3])) : {};
const RAIZ = path.resolve(__dirname, "..", "..");
const FONTE = "Arial";
const CM = 567; // DXA por centímetro
const LARGURA_UTIL = 21 * CM - 3 * CM - 2 * CM; // A4 menos margens esquerda (3) e direita (2)

// ---------------------------------------------------------------- helpers de texto
function runs(texto, base = {}) {
  // **negrito** dentro do texto
  return texto.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((p) =>
    p.startsWith("**") ? new TextRun({ ...base, text: p.slice(2, -2), bold: true }) : new TextRun({ ...base, text: p }));
}
const P = (texto, opts = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, indent: { firstLine: Math.round(1.25 * CM) },
  spacing: { line: 360, before: 0, after: 0 }, ...opts, children: runs(texto),
});
const centro = (texto, opts = {}, run = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { line: 360, before: 0, after: 0 }, ...opts,
  children: runs(texto, run),
});
const vazio = (n = 1) => Array.from({ length: n }, () => new Paragraph({ spacing: { line: 360 }, children: [] }));
const quebra = () => new Paragraph({ children: [new PageBreak()] });
const item = (texto) => new Paragraph({
  numbering: { reference: "marcadores", level: 0 }, alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 360 }, children: runs(texto),
});

// ---------------------------------------------------------------- títulos (ABNT)
const titulos = []; // para o sumário
function H1(numero, texto) {
  const rotulo = numero ? `${numero} ${texto.toUpperCase()}` : texto.toUpperCase();
  titulos.push({ nivel: 1, rotulo, chave: rotulo });
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, alignment: numero ? AlignmentType.LEFT : AlignmentType.CENTER,
    spacing: { before: 0, after: 360, line: 360 }, children: [new TextRun(rotulo)],
  });
}
function H2(numero, texto) {
  const rotulo = `${numero} ${texto}`;
  titulos.push({ nivel: 2, rotulo, chave: rotulo });
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 360, after: 240, line: 360 }, children: [new TextRun(rotulo)],
  });
}
function H3(numero, texto) {
  const rotulo = `${numero} ${texto}`;
  titulos.push({ nivel: 3, rotulo, chave: rotulo });
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, spacing: { before: 240, after: 120, line: 360 }, children: [new TextRun(rotulo)],
  });
}

// ---------------------------------------------------------------- figuras e quadros
const figuras = [];
const quadros = [];
const legenda = (texto) => new Paragraph({
  alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 240, after: 60, line: 240 },
  children: [new TextRun({ text: texto, size: 20 })],
});
const fonteDe = (texto) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 240, line: 240 },
  children: [new TextRun({ text: `Fonte: ${texto}`, size: 20 })],
});
function figura(arquivo, titulo, fonte, larguraCm) {
  const n = figuras.length + 1;
  const rotulo = `Figura ${n} – ${titulo}`;
  figuras.push({ rotulo, chave: rotulo });
  const buf = fs.readFileSync(path.join(RAIZ, arquivo));
  const { w, h } = tamanhoPng(buf);
  const largura = Math.round(larguraCm * 37.8); // px a 96 dpi
  return [
    legenda(rotulo),
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 0, after: 0 },
      children: [new ImageRun({ type: "png", data: buf, transformation: { width: largura, height: Math.round(largura * h / w) } })],
    }),
    fonteDe(fonte),
  ];
}
function tamanhoPng(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }

const borda = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
function quadro(titulo, fonte, cabecalho, linhas, larguras) {
  const n = quadros.length + 1;
  const rotulo = `Quadro ${n} – ${titulo}`;
  quadros.push({ rotulo, chave: rotulo });
  const total = larguras.reduce((a, b) => a + b, 0);
  const cols = larguras.map((l) => Math.round(l / total * LARGURA_UTIL));
  cols[cols.length - 1] += LARGURA_UTIL - cols.reduce((a, b) => a + b, 0);
  const celula = (texto, i, cab) => new TableCell({
    width: { size: cols[i], type: WidthType.DXA }, borders: bordas, verticalAlign: VerticalAlign.CENTER,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    shading: cab ? { type: ShadingType.CLEAR, color: "auto", fill: "E7E6E6" } : undefined,
    children: [new Paragraph({ spacing: { line: 240 }, children: runs(texto, { size: 20, bold: cab || undefined }) })],
  });
  return [
    legenda(rotulo),
    new Table({
      width: { size: LARGURA_UTIL, type: WidthType.DXA }, columnWidths: cols,
      rows: [
        new TableRow({ tableHeader: true, children: cabecalho.map((t, i) => celula(t, i, true)) }),
        ...linhas.map((l) => new TableRow({ cantSplit: true, children: l.map((t, i) => celula(t, i, false)) })),
      ],
    }),
    fonteDe(fonte),
  ];
}

// ---------------------------------------------------------------- listas e sumário (2ª passagem)
function linhaIndice(texto, chave, recuoCm = 0, negrito = false) {
  const pag = PAGINAS[chave] !== undefined ? String(PAGINAS[chave]) : "0";
  return new Paragraph({
    spacing: { line: 360 }, indent: { left: Math.round(recuoCm * CM) },
    tabStops: [{ type: TabStopType.RIGHT, position: LARGURA_UTIL, leader: LeaderType.DOT }],
    children: [new TextRun({ text: texto, bold: negrito }), new TextRun({ text: `\t${pag}`, bold: negrito })],
  });
}

// =================================================================== CONTEÚDO
const integrantes = [
  "GUSTAVO BALBO SARAIVA – RM 561711",
  "HENRY GIMENEZ – RM 563217",
  "VINICIUS ARAUJO – RM 564504",
];
const TITULO = "CITIZENTECH: INTEGRAÇÃO E GOVERNANÇA DOS MÓDULOS DA GLOBAL SOLUTION 2026/2";

const capa = [
  centro("**FACULDADE DE INFORMÁTICA E ADMINISTRAÇÃO PAULISTA – FIAP**"),
  centro("TECNÓLOGO EM INTELIGÊNCIA ARTIFICIAL"),
  ...vazio(4),
  ...integrantes.map((n) => centro(n)),
  ...vazio(6),
  centro(`**${TITULO}**`),
  ...vazio(10),
  centro("SÃO PAULO"),
  centro("2026"),
];

const folhaRosto = [
  quebra(),
  ...integrantes.map((n) => centro(n)),
  ...vazio(6),
  centro(`**${TITULO}**`),
  ...vazio(3),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, indent: { left: 8 * CM }, spacing: { line: 240 },
    children: [new TextRun({
      text: "Relatório apresentado à disciplina Governança em IA e Business Analytics do curso de Tecnólogo em " +
        "Inteligência Artificial da Faculdade de Informática e Administração Paulista (FIAP), como entrega de " +
        "integração da Global Solution 2026/2, tema CitizenTech.", size: 20,
    })],
  }),
  ...vazio(9),
  centro("SÃO PAULO"),
  centro("2026"),
];

// --------------------------------------------------------------- 1 INTRODUÇÃO
const introducao = [
  H1("1", "Introdução"),
  P("A Global Solution 2026/2 da FIAP tem como tema o CitizenTech: tecnologias criadas a partir de necessidades reais " +
    "de cidadãos. Cada uma das nove disciplinas do semestre pediu um módulo próprio, e a disciplina de Governança em " +
    "IA e Business Analytics pede este relatório, que reúne os módulos, mostra como se relacionam e indica o que foi " +
    "ou não integrado."),
  P("O grupo desenvolveu oito módulos. Eles atendem a três frentes de problema: manutenção da cidade (Zelo e Visão " +
    "Computacional), atendimento em saúde pública (RPA, Cluster Computing e Generative AI) e acesso do cidadão a " +
    "serviços e direitos (IoT, PLN e Computação Quântica). O Zelo, aplicação de zeladoria urbana com front-end, API e " +
    "modelo de linguagem, é o único módulo publicado e em uso por pessoas de fora do grupo, por isso serve de eixo da " +
    "integração e é por ele que o cidadão acessa o Generative AI."),
  P("A seção 2 traz um tópico por disciplina, com o problema atacado, o funcionamento, os resultados medidos e a " +
    "relação com os demais módulos. O último tópico, de Governança, classifica a integração de cada módulo, reúne os " +
    "indicadores e discute riscos, ética e proteção de dados. A seção 3 traz a conclusão do grupo e a seção 4, os links " +
    "do vídeo e do repositório."),
];

// --------------------------------------------------------------- 2 DESENVOLVIMENTO
const aberturaDesenvolvimento = [
  H1("2", "Desenvolvimento"),
  P("Os tópicos seguem a ordem das disciplinas no portal. Os números vêm dos relatórios e repositórios de cada módulo, " +
    "reunidos nas pastas do repositório indicado na seção 4."),
];
const rpa = [
  H2("2.1", "AI for Robotic Process Automation"),
  P("O módulo de RPA é um robô que faz a triagem de pedidos enviados a Unidades Básicas de Saúde (UBS). Hoje esses " +
    "pedidos chegam por telefone, formulário e aplicativo e são lidos um a um, o que atrasa o atendimento e pode deixar " +
    "um caso grave parado na fila. O robô lê arquivos CSV e TXT de uma caixa de entrada, valida cada registro, " +
    "classifica o texto em oito categorias com TF-IDF e regressão logística, aplica regras de prioridade, consulta o " +
    "endereço na API pública ViaCEP e gera protocolo e resposta ao cidadão."),
  P("Casos com termos de urgência ou com confiança abaixo de 0,45 vão para revisão humana. CPF, telefone e e-mail são " +
    "mascarados antes de qualquer saída, e só o CEP é enviado à API externa. Em dois conjuntos de teste escritos pelo " +
    "grupo (120 frases), a acurácia foi de 85,8%, 14 de 15 urgências foram protegidas e 9 de 84 encaminhamentos " +
    "automáticos estavam errados. A execução de ponta a ponta tratou arquivos corrompidos, duplicados e a queda da API " +
    "sem interromper o lote, e há 21 testes automatizados."),
  P("O próprio módulo registra que não está apto para uso real: um caso de trauma na cabeça foi encaminhado como " +
    "vacinação, e infarto e crise de saúde mental não disparam prioridade alta. Esses pontos voltam na seção 2.9."),
];

const cluster = [
  H2("2.2", "Cluster Computing, Computação Neuromórfica e Supercomputadores"),
  P("Este módulo usa o simulador iSPD 3.1 para estimar quanto o tempo de esvaziar a fila de classificação do RPA cai " +
    "quando o processamento passa de 2 para 4 workers. A carga são 400 tarefas de 500 MFLOP, todas na fila no início, " +
    "distribuídas por um mestre com escalonador RoundRobin."),
  P("O tempo total simulado caiu de 100,04 s para 50,04 s, um speedup de 1,9992×. Como cada worker tinha enlaces " +
    "próprios, a capacidade de rede também dobrava; para separar esse efeito, o grupo repetiu o teste com um switch " +
    "compartilhado e obteve speedup de 1,9942×. Os valores são de simulação, com carga homogênea e chegada simultânea, " +
    "e não medem o classificador real."),
  ...figura("02_Cluster_Computing/docs/relatorio_final/figuras/fig1b_cenarioB_diagrama.png",
    "Modelo do cenário com mestre e 4 workers no iSPD", "elaborada pelos autores no iSPD 3.1 (2026).", 5.5),
];

const quantica = [
  H2("2.3", "Computação Quântica & IA"),
  P("O trabalho de Computação Quântica é conceitual e não implementa algoritmo. Ele analisa uma carteira de identidade " +
    "digital do cidadão, com documentos, biometria e assinatura digital. O gargalo apontado não é desempenho, e sim " +
    "segurança: assinaturas e troca de chaves usam RSA e curvas elípticas, que um computador quântico de porte " +
    "suficiente quebraria com o algoritmo de Shor. Dados capturados hoje poderiam ser decifrados no futuro, e biometria " +
    "não pode ser trocada como uma senha."),
  P("A capacidade escolhida é a criptografia pós-quântica, com os padrões publicados pelo NIST em 2024 (FIPS 203, 204 e " +
    "205). O roadmap tem quatro horizontes: inventário criptográfico, uso híbrido de algoritmos clássicos e pós-quânticos, " +
    "migração completa e operação nativa a partir de 2032, cada um ligado à LGPD e aos ODS 9, 10 e 16."),
  ...figura("03_Computacao_Quantica/roadmap.png", "Roadmap de migração para criptografia pós-quântica",
    "elaborada pelos autores (2026).", 11),
];

const front = [
  H2("2.4", "Front End & Mobile Development"),
  P("O Zelo é a aplicação de zeladoria urbana do grupo. O morador descreve um problema na rua, como buraco, poste " +
    "apagado, lixo ou alagamento. A API em FastAPI remove dados pessoais do texto, consulta o endereço (ViaCEP) e a " +
    "previsão de chuva (Open-Meteo) e chama um modelo de linguagem (Groq, gpt-oss-120b), que devolve categoria, urgência, " +
    "órgão responsável e orientações em um formato validado por Pydantic. O front-end em Streamlit mostra o resultado, e " +
    "o cidadão confere e corrige antes de registrar o pedido. Regras no código elevam a urgência de alagamentos quando " +
    "há chuva forte prevista e garantem os números de emergência em casos graves."),
  P("A aplicação está publicada no Render. Nos casos de teste da IA, o modelo acertou 6 de 6 na rodada final, inclusive " +
    "uma tentativa de prompt injection. Na validação com três moradores de 19 e 20 anos, todos concluíram as tarefas " +
    "sem ajuda e deram nota 4 de 5. O teste revelou que o modelo inventou um telefone (\"0800-xxxx\") mesmo com o prompt " +
    "proibindo; o grupo passou a apagar telefones no código e a mostrar o canal oficial da prefeitura a partir de uma " +
    "tabela com fonte verificada. Uma aba do Zelo também dá acesso ao módulo de Generative AI (seção 2.5)."),
  ...figura("04_Front_End_Zelo/docs/validacao/depois_protocolo.png",
    "Tela de protocolo do Zelo com o canal oficial da prefeitura", "elaborada pelos autores (2026).", 11.5),
];

const genai = [
  H2("2.5", "Generative AI & Advanced Nets"),
  P("O módulo de Generative AI é um assistente que responde perguntas sobre publicações de saúde do Diário Oficial do " +
    "Distrito Federal, citando a fonte ou se abstendo quando não há evidência. Ele usa o conjunto público " +
    "dodf-saude-qa (FREIRE et al., 2026), recuperação lexical BM25 e o modelo local Qwen3-8B. Depois da geração, o código " +
    "confere se o trecho citado existe, se os nomes e números da resposta estão na evidência e se outra publicação " +
    "semelhante poderia ser a correta."),
  P("Na rodada de avaliação mais recente (150 perguntas), o sistema respondeu 31 (20,7%) e se absteve em 119. Na " +
    "auditoria feita por modelo de linguagem, sem revisão humana, 8 das 31 respostas estavam incorretas apesar de citarem " +
    "trechos literais. Cada resposta leva de 12 a 21 s (medianas) e o servidor do modelo chega a 8 GB de memória. O módulo " +
    "tem 337 testes e está integrado ao Zelo por uma camada separada, descrita na seção 2.9, sem alteração dos arquivos " +
    "congelados do assistente."),
];

const iot = [
  H2("2.6", "Physical Computing, Embedded AI, Robotics & Cognitive IoT"),
  P("O OuviAí ajuda pessoas surdas ou com deficiência auditiva a perceber sons da casa. O microfone do celular capta o " +
    "som, o modelo treinado no Edge Impulse transforma cada janela de 1 s em espectrograma (MFE) e uma rede convolucional " +
    "1D classifica o evento como campainha, batida na porta ou ambiente. O modelo roda no navegador do celular, sem " +
    "aplicativo próprio e sem enviar o áudio para a nuvem."),
  P("O grupo gravou 60 áudios de 5 s (45 para treino e 15 para teste). A acurácia foi de 98,8% na validação, 97,78% nos " +
    "áudios inéditos e 15 de 15 nas tentativas ao vivo. O único tipo de erro foi um falso positivo de campainha em um " +
    "áudio com ruído de elevador. O modelo ocupa 14,7 KB de RAM e caberia em um microcontrolador. Os ODS ligados são o 10 " +
    "e o 11."),
  ...figura("07_IoT_OuviAi/figura_arquitetura.png", "Arquitetura do OuviAí, do treino ao uso no celular",
    "elaborada pelos autores (2026).", 10.5),
];

const pln = [
  H2("2.7", "Processamento de Linguagem Natural, Chatbots & Virtual Agents"),
  P("O assistente de voz de PLN orienta sobre direitos do consumidor pessoas que têm dificuldade com texto, como idosos " +
    "e pessoas com baixa alfabetização ou deficiência visual. A fala é transcrita pelo Whisper, o sistema busca trechos " +
    "do Código de Defesa do Consumidor, um modelo local (Qwen2.5-3B) escreve a resposta, o texto é adaptado para fala e " +
    "uma voz sintética responde."),
  P("O modelo Whisper small reduziu o erro de transcrição (WER) de 33,4% para 18,9% em relação ao base, ao custo de " +
    "2,7 s. O assistente acertou 22 de 25 perguntas e recusou 5 de 5 perguntas fora do escopo. O tempo entre a pergunta e o " +
    "início da fala foi de 10,7 s em média. O áudio é apagado depois da transcrição, há consentimento antes do uso e " +
    "a análise mostrou erro maior com ruído de fundo (23,1% contra 17,5%) e diferenças entre vozes."),
  ...figura("08_PLN_Assistente_de_Voz/relatorio/arquitetura.png", "Arquitetura do assistente de voz",
    "elaborada pelos autores (2026).", 11),
];

const visao = [
  H2("2.8", "Visão Computacional"),
  P("O módulo de Visão Computacional classifica imagens de concreto com e sem fissura para indicar locais que precisam " +
    "de inspeção. Usa transfer learning com MobileNetV2, treinada com uma amostra de 2.000 imagens da base Concrete Crack Images for " +
    "Classification (ÖZGENEL, 2019), com interface em Gradio para imagem, vídeo e lote de fotos."),
  P("No conjunto de teste de 300 imagens, a acurácia foi de 0,997, com precisão de 1,000 e recall de 0,993. O único erro " +
    "foi uma fissura fina classificada como íntegra, com confiança de 0,55, perto do limiar. A inferência levou 53,2 ms " +
    "por imagem em CPU. O módulo serve para triagem e não avalia segurança estrutural. A base usada tem imagens " +
    "recortadas e limpas, então o desempenho em fotos de rua tende a ser menor."),
  ...figura("09_Visao_Computacional/resultados/matriz_confusao.png",
    "Matriz de confusão da detecção de fissuras no conjunto de teste", "elaborada pelos autores (2026).", 5.5),
];

// --------------------------------------------------------------- 2.9 GOVERNANÇA
const governanca = [
  H2("2.9", "Governança em IA e Business Analytics"),
  H3("2.9.1", "Critérios de integração"),
  P("Para cada módulo, o grupo verificou se ele troca dados ou chamadas com outro módulo. Foram usados quatro níveis: " +
    "**integrado (técnico)**, quando um componente chama outro em execução; **integrado por dados**, quando um módulo usa " +
    "os dados ou a carga de outro, mesmo rodando separado; **integrado por tema**, quando ataca o mesmo problema, mas " +
    "ainda sem troca de dados; e **não integrado**, quando trata de outro problema ou não está pronto. O Quadro 1 mostra " +
    "o resultado."),
  ...quadro("Nível de integração de cada módulo", "elaborado pelos autores (2026).",
    ["Módulo", "Nível", "Justificativa"],
    [
      ["Front-end (Zelo)", "Integrado (técnico)", "Front, API, modelo de linguagem e duas APIs públicas funcionam juntos no Render; consulta o Generative AI."],
      ["RPA", "Integrado por dados", "A carga simulada no Cluster representa a classificação feita pelo robô."],
      ["Cluster Computing", "Integrado por dados", "Simula a fila de classificação do RPA com 2 e 4 workers."],
      ["Visão Computacional", "Integrado por tema", "Mesmo problema do Zelo (manutenção urbana); a foto do problema poderia entrar no relato."],
      ["Generative AI", "Integrado (técnico)", "Aba do Zelo chama um serviço separado que importa o assistente; só roda no computador com o modelo local."],
      ["IoT (OuviAí)", "Não integrado", "Outro problema (acessibilidade em casa); roda no celular, sem servidor."],
      ["PLN", "Não integrado", "Outro problema (direitos do consumidor); a voz poderia ser um canal de entrada do Zelo."],
      ["Computação Quântica", "Conceitual", "Sem implementação; o roadmap de criptografia se aplica aos dados de todos os módulos."],
    ], [3.2, 2.8, 8]),
  P("A integração do Generative AI usa um serviço local que carrega o índice uma vez, atende uma pergunta por vez e " +
    "devolve status, publicação e trecho citado; o Zelo apaga dados pessoais antes de enviar a pergunta. Como o modelo " +
    "precisa de cerca de 8 GB de memória, a aba fica desligada no Zelo publicado e funciona só na demonstração local. O " +
    "IoT e o PLN foram feitos para problemas diferentes; os caminhos mais curtos seriam usar a voz do PLN como entrada do " +
    "Zelo e enviar a foto classificada pela Visão Computacional junto do relato."),
  H3("2.9.2", "Indicadores"),
  P("O Quadro 2 reúne os principais indicadores medidos em cada módulo. Eles vieram de conjuntos de teste diferentes, " +
    "então servem para acompanhar cada módulo, e não para comparar um com outro."),
  ...quadro("Indicadores de qualidade e desempenho por módulo", "elaborado pelos autores (2026).",
    ["Módulo", "Qualidade", "Desempenho", "Base da medida"],
    [
      ["RPA", "85,8% de acurácia; 14/15 urgências protegidas", "10 a 22 s por lote de 25 registros", "120 frases escritas pelo grupo"],
      ["Cluster", "Speedup de 1,9992× (1,9942× com switch)", "100,04 s → 50,04 s simulados", "400 tarefas simuladas"],
      ["Zelo", "6/6 casos de teste; nota 4/5 dos usuários", "Até 1 min para o servidor gratuito ligar", "6 casos e 3 moradores"],
      ["Generative AI", "31 de 150 com resposta; 8 incorretas", "12 a 21 s por pergunta", "150 perguntas de validação"],
      ["IoT", "98,8% / 97,78% / 15 de 15", "7 ms por inferência", "60 áudios e 15 tentativas ao vivo"],
      ["PLN", "WER 18,9%; 22/25 respostas corretas", "10,7 s até o início da fala", "20 áudios e 30 perguntas"],
      ["Visão", "Acurácia 0,997; recall 0,993", "53,2 ms por imagem", "300 imagens de teste"],
    ], [2.3, 4.6, 3.6, 3.5]),
  H3("2.9.3", "Riscos, ética e proteção de dados"),
  P("Todos os módulos que decidem algo sobre o cidadão mantêm uma pessoa no circuito. No Zelo, o cidadão confere a " +
    "classificação antes de registrar; no RPA, urgência e baixa confiança vão para revisão humana; na Visão " +
    "Computacional, o resultado indica inspeção, mas a decisão fica com o técnico; no Generative AI, o sistema prefere " +
    "abster-se a responder sem fonte. O Quadro 3 resume os riscos que continuam abertos."),
  ...quadro("Riscos abertos e controles adotados", "elaborado pelos autores (2026).",
    ["Módulo", "Risco aberto", "Controle atual"],
    [
      ["RPA", "Trauma, infarto e crise de saúde mental não recebem prioridade alta", "Declarado inapto para uso real; não foi corrigido"],
      ["Zelo", "Modelo de linguagem inventou um telefone", "Filtro de telefones no código e canal oficial vindo de tabela verificada"],
      ["Generative AI", "Resposta incorreta com citação literal (8 de 31)", "Status, publicação e trecho sempre visíveis; aviso de protótipo não validado"],
      ["Visão", "Fissura fina passa como íntegra", "Uso só para triagem; limiar pode ser reduzido"],
      ["PLN", "Erro maior com ruído e com certas vozes", "Filtro de voz e orientação de uso em local silencioso"],
      ["IoT", "Falso positivo com ruídos da casa", "Não substitui alarme; regra de confirmação proposta"],
    ], [2.3, 6, 5.7]),
  P("Sobre dados pessoais, o grupo seguiu o princípio de minimização da LGPD (BRASIL, 2018). O Zelo e o RPA mascaram " +
    "CPF, telefone e e-mail antes do processamento; o painel público do Zelo não mostra texto nem endereço; o assistente " +
    "de voz apaga o áudio depois da transcrição; e o OuviAí processa o som no próprio celular. Nenhum módulo usou dados " +
    "reais de pacientes ou cidadãos: os testes do RPA e do Generative AI usam dados sintéticos ou públicos. O roadmap de " +
    "Computação Quântica complementa esses controles ao tratar a proteção de longo prazo dos dados guardados."),
  P("O principal aprendizado de governança foi que regra escrita no prompt não garante o comportamento do modelo. Os " +
    "casos do telefone inventado no Zelo e das respostas com a publicação errada no Generative AI só foram contidos " +
    "quando a verificação passou para o código, e mesmo assim o Generative AI ainda entrega respostas incorretas. Os riscos do RPA mostram o limite oposto: uma regra de urgência por " +
    "palavras-chave não cobre casos clínicos sem a participação de profissionais de saúde."),
];

const conclusao = [
  H1("3", "Conclusão"),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 360 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFF2CC" },
    children: [new TextRun({
      text: "[Seção a ser redigida pelos integrantes do grupo, conforme o barema da disciplina. Apagar este aviso " +
        "depois de escrever o texto.]", italics: true,
    })],
  }),
];

const links = [
  H1("4", "Links"),
  P("**Vídeo de demonstração da integração (YouTube, não listado):** [inserir link]"),
  P("**Repositório GitHub com todos os módulos:** https://github.com/gubalb0/GS-CitizenTech"),
  P("**Repositório do Zelo:** https://github.com/gubalb0/GS-FRONT"),
  P("**Zelo publicado:** https://zelo-web.onrender.com"),
];

const ref = (t) => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 240, after: 240 }, children: runs(t) });
const referencias = [
  H1(null, "Referências"),
  ref("AGÊNCIA BRASIL. São Paulo ainda registra alagamentos e trânsito intenso após temporal. Brasília, 25 jan. 2025. " +
    "Disponível em: https://agenciabrasil.ebc.com.br/geral/noticia/2025-01/sao-paulo-ainda-registra-alagamentos-e-transito-intenso-apos-temporal. " +
    "Acesso em: 16 nov. 2026."),
  ref("BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). " +
    "**Diário Oficial da União**, Brasília, DF, 15 ago. 2018."),
  ref("FREIRE, A. S. M. et al. Evaluating location-aware RAG approaches for question answering over public " +
    "health-related content in Brazilian official gazettes. In: BRAZILIAN CONFERENCE ON INTELLIGENT SYSTEMS (BRACIS), " +
    "2026. No prelo."),
  ref("GSPD-UNESP. **iSPD**: iconic Simulator of Parallel and Distributed Systems. Versão 3.1. São José do Rio Preto: UNESP, [s.d.]."),
  ref("NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. **FIPS 203**: Module-Lattice-Based Key-Encapsulation Mechanism " +
    "Standard. Gaithersburg: NIST, 2024."),
  ref("ÖZGENEL, Ç. F. **Concrete Crack Images for Classification**. Mendeley Data, v. 2, 2019. DOI: 10.17632/5y9wdsg2zt.2."),
  ref("OPEN-METEO. **Free Weather API**. Disponível em: https://open-meteo.com. Acesso em: 16 nov. 2026."),
  ref("VIACEP. **Webservice CEP**. Disponível em: https://viacep.com.br. Acesso em: 16 nov. 2026."),
];

// --------------------------------------------------------------- montagem
const corpo = [
  ...introducao,
  quebra(),
  ...aberturaDesenvolvimento,
  ...rpa, ...cluster, ...quantica, ...front, ...genai, ...iot, ...pln, ...visao, ...governanca,
  quebra(), ...conclusao,
  ...vazio(1), ...links,
  quebra(), ...referencias,
];

// listas e sumário dependem de figuras/quadros/títulos, que já foram coletados acima
const listaFiguras = [quebra(), H1(null, "Lista de figuras"),
  ...figuras.map((f) => linhaIndice(f.rotulo, f.chave))];
const listaQuadros = [...vazio(2), H1(null, "Lista de quadros"),
  ...quadros.map((q) => linhaIndice(q.rotulo, q.chave))];
// os três títulos acima não entram no sumário (elementos pré-textuais)
const titulosSumario = titulos.filter((t) => !["LISTA DE FIGURAS", "LISTA DE QUADROS", "SUMÁRIO"].includes(t.rotulo));
const sumario = [quebra(), new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 360, line: 360 },
  children: [new TextRun({ text: "SUMÁRIO", bold: true })],
}), ...titulosSumario.map((t) => linhaIndice(t.rotulo, t.chave, 0, t.nivel === 1))];

const paginasPre = 4; // capa, folha de rosto, listas de figuras e de quadros, sumário
const doc = new Document({
  creator: "Gustavo Balbo Saraiva, Henry Gimenez, Vinicius Araujo",
  title: "CitizenTech: integração e governança dos módulos da Global Solution 2026/2",
  styles: {
    default: { document: { run: { font: FONTE, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: 24, bold: true }, paragraph: { spacing: { before: 0, after: 360 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: 24, bold: true }, paragraph: { spacing: { before: 360, after: 240 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: 24, bold: false }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "marcadores", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [
    {
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 3 * CM, left: 3 * CM, bottom: 2 * CM, right: 2 * CM } } },
      children: [...capa, ...folhaRosto, ...listaFiguras, ...listaQuadros, ...sumario],
    },
    {
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: { width: 11906, height: 16838 }, margin: { top: 3 * CM, left: 3 * CM, bottom: 2 * CM, right: 2 * CM, header: 2 * CM },
          pageNumbers: { start: paginasPre } }, // contagem a partir da folha de rosto (capa não conta)
      },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
      children: corpo,
    },
  ],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(SAIDA, b);
  fs.writeFileSync(SAIDA.replace(/\.docx$/, ".chaves.json"),
    JSON.stringify({ titulos: titulosSumario.map((t) => t.chave), figuras: figuras.map((f) => f.chave), quadros: quadros.map((q) => q.chave) }, null, 1));
  console.log("ok", SAIDA);
});
