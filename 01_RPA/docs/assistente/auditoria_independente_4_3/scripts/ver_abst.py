import json,sys
F=json.load(open(r"D:/Downloads/GS/RPA/docs/assistente/auditoria_independente_4_3/fatos_por_pergunta.json",encoding="utf-8"))
A=[f for f in F if f["status"] not in("respondida","parcial")]
a,b=int(sys.argv[1]),int(sys.argv[2])
for f in A[a:b]:
    print("==",f["qid"],f["status"],"g"+f["grupo"],"M" if f["multi"] else "-","NU" if f["nao_univoca"] else "","conc_sis=",len(f["concorrentes_sistema"]),f["identificabilidade"].get("motivo",""),"nrel=",f["identificabilidade"].get("n_relevantes_janela",""))
    print("P:",f["pergunta"]); print("sis:",f["resposta"][:110].replace("\n"," "),"|",(f["justificativa_sistema"] or "")[:100])
    print("ref:",f["resposta_dataset(LLM,nao e verdade)"][:100])
    cs=sorted(f["candidatos_independentes"],key=lambda c:-len(c["valores_ref_presentes"]))
    nv=len(f["valores_ref"])
    for c in cs[:1]: print("  c",c["doc_id"],f'cob{c["cobertura"]}/{c["n_termos"]}',f'vals{len(c["valores_ref_presentes"])}/{nv}',c["ref"][:45],"|",c["trecho"][60:150])
