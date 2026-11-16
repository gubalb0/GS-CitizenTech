import ispd.arquivo.xml.IconicoXML;

import java.io.File;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * SENSIBILIDADE (A'/B'): mesma carga (trace existente, NAO regravado) e mesmos parametros,
 * mas os workers ficam atras de UM switch compartilhado (icone "cluster" nao-mestre, CS_Switch):
 *   mestre(machine) --link_ida--> [cluster/switch, N workers] --link_volta--> mestre
 * A capacidade de comunicacao nao depende de N: 1 par de links de tronco + 1 switch (FIFO unico).
 * (Um icone cluster com master=true e rejeitado por IconicoXML.validarModelo, que so conta
 * <machine> com <master>; por isso o mestre e uma <machine>.)
 * Usa o escritor oficial IconicoXML. Nao altera os modelos A/B existentes.
 *
 * Uso: java GerarModelosCluster <pastaRaiz> [--regenerar]
 * Por padrao NAO sobrescreve modelos existentes; com --regenerar, reescreve.
 */
public class GerarModelosCluster {
    public static void main(String[] args) {
        Locale.setDefault(new Locale("en", "US"));
        File root = new File(args[0]);
        File trace = new File(root, "trace/carga_citizentech_400.trace");
        if (!trace.exists()) throw new IllegalStateException("trace ausente: " + trace);
        boolean regenerar = args.length > 1 && args[1].equals("--regenerar");
        File a = new File(root, "modelos/cenario_Ap_2_workers_switch.imsx");
        File b = new File(root, "modelos/cenario_Bp_4_workers_switch.imsx");
        if (GerarModelos.podeEscrever(a, regenerar)) build(a, 2, trace);
        if (GerarModelos.podeEscrever(b, regenerar)) build(b, 4, trace);
    }

    static void build(File out, int workers, File trace) {
        IconicoXML x = new IconicoXML(0); // GRID
        x.addUsers(List.of(GerarModelos.OWNER), Map.of(GerarModelos.OWNER, 100.0));
        // ids globais: 0 = mestre, 1 = cluster(switch + N workers), 2 = link ida, 3 = link volta
        x.addMachine(300, 100, 0, 0, "mestre", GerarModelos.MASTER_MFLOPS, 0.0,
                GerarModelos.SCHEDULER, GerarModelos.OWNER, 1, 8.0, 100.0,
                true, List.of(1), 0.0);
        x.addCluster(300, 400, 1, 1, "worker", workers,
                GerarModelos.WORKER_MFLOPS, 1, 8.0, 100.0,
                GerarModelos.BANDWIDTH_MBPS, GerarModelos.LATENCY_S,
                "---", GerarModelos.OWNER, false, 0.0);
        x.addLink(300, 100, 300, 400, 2, 2, "link_ida", GerarModelos.BANDWIDTH_MBPS, 0.0,
                GerarModelos.LATENCY_S, 0, 1);
        x.addLink(300, 400, 300, 100, 3, 3, "link_volta", GerarModelos.BANDWIDTH_MBPS, 0.0,
                GerarModelos.LATENCY_S, 1, 0);
        x.setLoadTrace(trace.getAbsolutePath(), GerarModelos.TASKS, "iSPD");
        if (!IconicoXML.escrever(x.getDescricao(), out)) throw new IllegalStateException("falha " + out);
    }
}
