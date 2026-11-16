"""Gera data/treino.csv SINTETICO (templates + variacao aleatoria com seed fixa).
Nenhum dado pessoal real. O conjunto de TESTE (data/teste_rotulado.csv) e escrito a mao,
com redacao diferente, para evitar avaliar o modelo nos mesmos templates do treino."""
import csv
import random
from pathlib import Path

random.seed(2026)
LOCAIS = ["na UBS Jardim Esperanca", "no posto de saude do bairro", "na unidade basica perto da escola",
          "na UBS central", "no posto da vila", "na unidade do conjunto habitacional", "no posto da zona leste",
          "na UBS Sao Jose", "no posto perto do mercado", "na unidade do meu bairro"]
ABERTURAS = ["", "Bom dia. ", "Gostaria de informar que ", "Pessoal, ", "Preciso de ajuda: ", "Solicito providencias. "]
FECHOS = ["", " Obrigado.", " Aguardo retorno.", " Ja tentei outras vezes.", " Moro perto daqui.", " Por favor, me orientem."]

BASE = {
    "agendamento_consulta": ["quero marcar uma consulta com clinico geral", "preciso agendar consulta com o medico da familia",
        "como faco para marcar consulta de rotina", "nao consigo agendar atendimento medico pelo telefone",
        "quero remarcar minha consulta que foi cancelada", "preciso de uma consulta com pediatra para meu filho"],
    "vacinacao": ["queria saber se tem vacina da gripe disponivel", "preciso atualizar a caderneta de vacinacao das criancas",
        "tem vacina contra febre amarela no posto", "a vacina do meu filho esta atrasada e quero tomar",
        "quando comeca a campanha de vacinacao dos idosos", "faltou vacina na unidade e preciso da dose de reforco"],
    "medicamentos": ["preciso retirar meu remedio de pressao alta", "a farmacia da unidade esta sem insulina",
        "faltam medicamentos de uso continuo no posto", "como renovar a receita do remedio controlado",
        "quero saber se tem dipirona e amoxicilina para retirar", "o remedio que tomo todo mes nao chegou"],
    "exames_resultados": ["quero saber o resultado do meu exame de sangue", "preciso agendar exame de ultrassom",
        "meu exame demorou e o resultado nao saiu", "como pego o laudo do raio x",
        "pedido de encaminhamento para exame de imagem", "quando fica pronto o resultado do preventivo"],
    "visita_domiciliar": ["preciso de visita do agente comunitario de saude", "minha mae e idosa e acamada e precisa de atendimento em casa",
        "o agente de saude nao passa na nossa casa ha meses", "solicito visita domiciliar da equipe para paciente acamado",
        "quero cadastrar minha familia na equipe de saude da familia", "preciso de curativo em casa porque ele nao consegue sair"],
    "reclamacao_atendimento": ["fui mal atendido pela recepcao do posto", "esperei cinco horas e ninguem me atendeu",
        "o posto fechou mais cedo e nao atendeu os pacientes", "a unidade esta sem medico ha dias",
        "tem muita demora e desorganizacao no atendimento", "reclamo da falta de respeito de um funcionario"],
    "informacoes_gerais": ["qual o horario de funcionamento da unidade", "quais documentos preciso levar para ser atendido",
        "como faco o cartao SUS", "qual a UBS de referencia do meu endereco",
        "o posto atende aos sabados", "quais servicos a unidade oferece"],
    "sintomas_urgentes": ["estou com dor forte no peito e falta de ar", "meu bebe esta com febre alta e muito prostrado",
        "tem uma pessoa desmaiada e com dificuldade para respirar", "estou com sangramento intenso e tontura",
        "meu pai esta confuso e com a boca torta de repente", "crianca com convulsao e febre agora"],
}

BASE["agendamento_consulta"] += ['desejo consulta com medico clinico', 'solicito marcacao de atendimento', 'existe disponibilidade de agenda para o doutor', 'preciso consultar com a equipe de saude da familia', 'queria uma data para ser examinado pelo medico', 'marcacao de consulta odontologica', 'preciso marcar para minha esposa ver o obstetra']
BASE["vacinacao"] += ['quais vacinas meu bebe precisa tomar neste mes', 'aplicam vacina de rotina para adultos', 'meu cartao de imunizacao esta incompleto', 'tem dose da vacina contra covid hoje', 'a vacina antirrabica esta disponivel', 'ate quando posso tomar a vacina da gripe', 'a enfermeira pode aplicar o reforco do meu filho']
BASE["medicamentos"] += ['como faco para receber meu medicamento de uso diario', 'falta captopril e metformina na distribuicao', 'ha estoque do remedio para epilepsia', 'preciso da receita renovada para buscar o tratamento do mes', 'dispensacao de medicamentos, qual o horario da farmacia', 'nao encontro o antialergico na unidade']
BASE["exames_resultados"] += ['pedido medico de exame de colesterol, como marco', 'a coleta do laboratorio sera em qual dia', 'quando sai o parecer do exame de imagem', 'retirar documento com o resultado dos testes', 'solicito liberacao de exame especializado', 'preciso levar o pedido para a regulacao']
BASE["visita_domiciliar"] += ['familiar com mobilidade reduzida precisa ser atendido na residencia', 'gostaria que o agente comunitario passe aqui', 'a equipe poderia ir ate a casa de um paciente restrito ao leito', 'preciso da equipe de saude da familia para visita', 'troca de curativo na residencia do paciente', 'agente de saude nao faz visitas na minha microarea']
BASE["reclamacao_atendimento"] += ['fui destratado pelo funcionario', 'a espera passou de quatro horas', 'unidade sem profissional medico hoje', 'falta de organizacao e de respeito no posto', 'quero denunciar mau atendimento', 'porta fechada em horario de funcionamento']
BASE["informacoes_gerais"] += ['qual o numero para contato da UBS', 'que dias o posto funciona', 'como cadastrar um recem nascido no sistema do posto', 'preciso de orientacao sobre documentos para abrir ficha', 'qual a unidade referencia do meu endereco', 'e preciso agendar antes ou posso ir direto']
BASE["sintomas_urgentes"] += ['paciente com dor toracica intensa e sudorese', 'recem nascido com febre e respirando com esforco', 'gestante com perda de sangue e dores', 'homem inconsciente no chao', 'crianca com crise convulsiva', 'queda com suspeita de fratura e muita dor', 'hemorragia que nao estanca', 'pessoa com fala enrolada e fraqueza de um lado do corpo']


def ruido(t):
    if random.random() < 0.25 and len(t) > 10:
        i = random.randrange(3, len(t) - 3)
        t = t[:i] + t[i + 1:]  # remove um caractere (erro de digitacao)
    return t.lower() if random.random() < 0.2 else t


linhas = []
for cat, frases in BASE.items():
    for _ in range(80):
        f = random.choice(frases)
        txt = random.choice(ABERTURAS) + f + " " + random.choice(LOCAIS) + "." + random.choice(FECHOS)
        linhas.append((ruido(txt.strip()), cat))
random.shuffle(linhas)
saida = Path(__file__).resolve().parent.parent / "data" / "treino.csv"
with saida.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["texto", "categoria"])
    w.writerows(linhas)
print(f"{len(linhas)} linhas sinteticas -> {saida}")
