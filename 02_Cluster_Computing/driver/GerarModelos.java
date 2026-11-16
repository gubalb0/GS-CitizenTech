import ispd.arquivo.xml.IconicoXML;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Gera o trace compartilhado e os dois modelos (.imsx) usando o ESCRITOR OFICIAL
 * do iSPD (ispd.arquivo.xml.IconicoXML), o mesmo usado pela interface grafica.
 * Unico parametro que varia entre os cenarios: numero de workers.
 *
 * Uso: java GerarModelos <pastaRaiz> [--regenerar]
 * Por padrao NAO sobrescreve trace/modelos existentes (mantem e informa). Com --regenerar, reescreve.
 * ATENCAO: o .imsx grava o caminho ABSOLUTO do trace (file_path), logo o hash do .imsx depende da
 * pasta onde foi gerado; o hash do trace nao depende.
 */
public class GerarModelos {
    // ===== HIPOTESES DE SIMULACAO (nao sao medicoes) =====
    static final int TASKS = 400;
    static final double TASK_MFLOP = 500.0;          // cpsz (MFlops)
    static final double TASK_INPUT_MB = 0.5;         // entrada por tarefa
    static final double TASK_INPUT_MBIT = TASK_INPUT_MB * 8.0; // cmsz (MBits) = 4.0
    static final double WORKER_MFLOPS = 1000.0;
    static final double MASTER_MFLOPS = 1000.0;
    static final double BANDWIDTH_MBPS = 100.0;
    static final double LATENCY_S = 0.001;           // 1 ms (iSPD usa segundos)
    static final String SCHEDULER = "RoundRobin";
    static final String OWNER = "user1";

    public static void main(String[] args) throws Exception {
        Locale.setDefault(new Locale("en", "US"));
        File root = new File(args[0]);
        boolean regenerar = args.length > 1 && args[1].equals("--regenerar");
        File traceFile = new File(root, "trace/carga_citizentech_400.trace");
        File modelsDir = new File(root, "modelos");
        traceFile.getParentFile().mkdirs();
        modelsDir.mkdirs();

        if (podeEscrever(traceFile, regenerar)) writeTrace(traceFile);
        File a = new File(modelsDir, "cenario_A_2_workers.imsx");
        File b = new File(modelsDir, "cenario_B_4_workers.imsx");
        if (podeEscrever(a, regenerar)) buildModel(a, 2, traceFile);
        if (podeEscrever(b, regenerar)) buildModel(b, 4, traceFile);
    }

    /** true se o arquivo nao existe ou se --regenerar foi pedido; caso contrario mantem o existente. */
    static boolean podeEscrever(File f, boolean regenerar) {
        if (f.exists() && !regenerar) {
            System.out.println("MANTIDO (ja existe; use --regenerar para reescrever): " + f);
            return false;
        }
        System.out.println((f.exists() ? "REESCRITO: " : "CRIADO: ") + f);
        return true;
    }

    /** Mesmo formato escrito por ispd.arquivo.interpretador.cargas.Interpretador. */
    static void writeTrace(File f) throws IOException {
        try (PrintWriter out = new PrintWriter(f, StandardCharsets.UTF_8)) {
            out.print("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" standalone=\"no\"?>\n");
            out.print("<!DOCTYPE system SYSTEM \"iSPDcarga.dtd\">\n");
            out.print("<system>\n");
            out.print("<trace>\n");
            out.print("<format kind=\"iSPD\" />\n");
            for (int i = 1; i <= TASKS; i++) {
                out.print(String.format(
                        "<task id=\"%d\" arr=\"0.0\" sts=\"1\" cpsz =\"%s\" cmsz=\"%s\" usr=\"%s\" />\n",
                        i, TASK_MFLOP, TASK_INPUT_MBIT, OWNER));
            }
            // NOTA: sem as linhas finais </trace></system>. TraceFileWorkloadGenerator
            // trata TODA linha apos as 5 de cabecalho como tarefa e o parse de
            // TraceTaskInfo.user() falharia (ArrayIndexOutOfBounds) em linhas sem aspas.
        }
    }

    static void buildModel(File out, int workers, File trace) {
        IconicoXML x = new IconicoXML(0); // 0 = GRID (versao 2.1)
        x.addUsers(List.of(OWNER), Map.of(OWNER, 100.0));

        // icones: global id 0 = mestre, 1..N = workers, N+1..2N = links
        List<Integer> slaveIds = new ArrayList<>();
        for (int i = 1; i <= workers; i++) slaveIds.add(i);

        x.addMachine(300, 100, 0, 0, "mestre", MASTER_MFLOPS, 0.0, SCHEDULER,
                OWNER, 1, 8.0, 100.0, true, slaveIds, 0.0);

        for (int i = 1; i <= workers; i++) {
            x.addMachine(100 + 150 * (i - 1), 400, i, i, "worker" + i,
                    WORKER_MFLOPS, 0.0, "---", OWNER, 1, 8.0, 100.0,
                    false, List.of(), 0.0);
        }
        // O motor exige um link DIRECIONADO por sentido: CS_Processamento.getMenorCaminho
        // percorre apenas conexoesSaida. Sem o link worker->mestre ocorre LinkageError/NPE
        // em CS_Maquina.determinarCaminhos. Por isso, 2 links por worker (ida e volta),
        // ambos 100 Mbps / 1 ms.
        for (int i = 1; i <= workers; i++) {
            int linkId = workers + i;
            x.addLink(300, 100, 100 + 150 * (i - 1), 400, linkId, linkId,
                    "link_ida_w" + i, BANDWIDTH_MBPS, 0.0, LATENCY_S, 0, i);
        }
        for (int i = 1; i <= workers; i++) {
            int linkId = 2 * workers + i;
            x.addLink(100 + 150 * (i - 1), 400, 300, 100, linkId, linkId,
                    "link_volta_w" + i, BANDWIDTH_MBPS, 0.0, LATENCY_S, i, 0);
        }
        x.setLoadTrace(trace.getAbsolutePath(), TASKS, "iSPD");

        if (!IconicoXML.escrever(x.getDescricao(), out)) {
            throw new IllegalStateException("Falha ao escrever " + out);
        }
    }
}
