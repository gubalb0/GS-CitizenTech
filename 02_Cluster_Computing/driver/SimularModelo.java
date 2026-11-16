import ispd.arquivo.xml.IconicoXML;
import ispd.motor.ProgressoSimulacao;
import ispd.motor.SimulacaoSequencial;
import ispd.motor.filas.Tarefa;
import ispd.motor.metricas.Metricas;

import java.awt.Color;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

/**
 * Executor COMPLEMENTAR. Reproduz passo a passo ispd.application.terminal.
 * TerminalApplication.runASimulation (mesmo motor, mesmas classes) apenas para
 * expor dados que o HTML nao traz: tarefas concluidas por worker.
 * Nao altera o iSPD; nao calcula nenhum resultado por conta propria:
 * apenas le o estado final das Tarefa produzidas pelo motor.
 *
 * Uso: java SimularModelo <modelo.imsx> <saida_tarefas_por_worker.csv> [saida_tarefas_detalhe.csv]
 *
 * O 3o argumento (OPCIONAL) grava uma linha por tarefa com dados lidos dos getters publicos de Tarefa
 * apos a simulacao (registro da atribuicao do RoundRobin). Sem ele, o comportamento e o original.
 * NAO FOI EXECUTADO ate a data desta alteracao (somente compilado); ver README, secao RoundRobin.
 */
public class SimularModelo {
    public static void main(String[] args) throws Exception {
        Locale.setDefault(new Locale("en", "US"));
        var progress = new ProgressoSimulacao() {
            @Override public void incProgresso(int n) { }
            @Override public void print(String text, Color cor) { }
        };

        var model = IconicoXML.ler(new File(args[0]));
        progress.validarInicioSimulacao(model);

        var qn = IconicoXML.newRedeDeFilas(model);
        List<Tarefa> jobs = IconicoXML.newGerarCarga(model).makeTaskList(qn);
        var sim = new SimulacaoSequencial(progress, qn, jobs);
        sim.createRouting();
        sim.simulate();
        Metricas m = sim.getMetrics();

        Map<String, Integer> done = new TreeMap<>();
        Map<String, Integer> notDone = new TreeMap<>();
        for (Tarefa t : jobs) {
            String w = t.getLocalProcessamento() == null ? "(nenhum)"
                    : t.getLocalProcessamento().getId();
            if (t.getEstado() == Tarefa.CONCLUIDO) done.merge(w, 1, Integer::sum);
            else notDone.merge(w, 1, Integer::sum);
        }

        try (PrintWriter out = new PrintWriter(args[1], StandardCharsets.UTF_8)) {
            out.println("recurso;tarefas_concluidas;tarefas_nao_concluidas");
            for (String k : done.keySet())
                out.println(k + ";" + done.get(k) + ";" + notDone.getOrDefault(k, 0));
            for (String k : notDone.keySet())
                if (!done.containsKey(k)) out.println(k + ";0;" + notDone.get(k));
        }
        if (args.length > 2) {
            try (PrintWriter out = new PrintWriter(args[2], StandardCharsets.UTF_8)) {
                out.println("indice_na_lista;id;estado;worker_id;worker_num;"
                        + "criacao_s;espera_comunicacao_s;comunicacao_s;inicio_processamento_s;fim_processamento_s");
                int idx = 0;
                for (Tarefa t : jobs) {
                    idx++;
                    var loc = (ispd.motor.filas.servidores.CS_Processamento) t.getLocalProcessamento();
                    String wid = loc == null ? "" : loc.getId();
                    String wnum = loc == null ? "" : String.valueOf(loc.getMetrica().getnumeroMaquina());
                    String ini = t.getTempoInicial().isEmpty() ? "" : String.valueOf(t.getTempoInicial().get(0));
                    String fim = t.getTempoFinal().isEmpty() ? "" : String.valueOf(t.getTempoFinal().get(t.getTempoFinal().size() - 1));
                    out.println(idx + ";" + t.getIdentificador() + ";" + t.getEstado() + ";" + wid + ";" + wnum + ";"
                            + t.getTimeCriacao() + ";" + t.getMetricas().getTempoEsperaComu() + ";"
                            + t.getMetricas().getTempoComunicacao() + ";" + ini + ";" + fim);
                }
            }
        }
        System.out.println("tarefas_total=" + jobs.size());
        System.out.println("tempo_simulado_s=" + m.getMetricasGlobais().getTempoSimulacao());
        done.forEach((k, v) -> System.out.println("concluidas[" + k + "]=" + v));
        notDone.forEach((k, v) -> System.out.println("nao_concluidas[" + k + "]=" + v));
    }
}
