from pathlib import Path
from string import Template
import json
import unicodedata
import re

ROOT = Path(__file__).resolve().parents[1]

rng = re.compile(r"(\d+)\D+(\d+)")

#-----------Helpers-----------
def slugify(s):
  s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
  return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()

def clamp_0_5(x):
  return max(0, min(5, x))

def round_int(x):
  return int(round(x))

def minutes_to_scale(mins):
  if mins is None:
    return 3
  if mins >= 90:
    return 5
  if mins >= 75:
    return 4
  if mins >= 60:
    return 3
  if mins >= 45:
    return 2
  return 1

def nivel_txt(n):
  m = {1:"muito baixa",2:"baixa",3:"moderada",4:"alta",5:"muito alta"}
  return m.get(int(clamp_0_5(n)), "moderada")

def duracao_txt(mins):
  if mins is None:
    return "moderada"
  if mins >= 90:
    return "longa"
  if mins >= 75:
    return "moderada a longa"
  if mins >= 60:
    return "moderada"
  if mins >= 45:
    return "curta a moderada"
  return "curta"

def duracao_frase(mins):
  if mins is None:
    return "duração moderada"
  if mins >= 90:
    return "longa duração"
  if mins >= 75:
    return "duração moderada a longa"
  if mins >= 60:
    return "duração moderada"
  if mins >= 45:
    return "duração curta a moderada"
  return "curta duração"

def parse_minmax(txt):
  if not txt or txt == "—":
      return None, None
  m = rng.search(txt)
  if not m:
    only_num = re.findall(r"\d+", txt)
    if len(only_num) == 1:
      v = int(only_num[0])
      return v, v
    return None, None
  return int(m.group(1)), int(m.group(2))

def jsonld_breadcrumb(nome, url):
  return json.dumps({
    "@context":"https://schema.org","@type":"BreadcrumbList",
    "itemListElement":[
      {"@type":"ListItem","position":1,"name":"Início","item":f"{BASE}/"},
      {"@type":"ListItem","position":2,"name":"Raças","item":f"{BASE}/racas/"},
      {"@type":"ListItem","position":3,"name":nome,"item":url}
    ]
  }, ensure_ascii=False)

def jsonld_breed(d, url):
  desc = d.get("lead") or d.get("notas", {}).get("resumo", "")
  alt_macho = d["medidas"]["altura_cm"].get("macho", "—")
  alt_fem   = d["medidas"]["altura_cm"].get("femea", "—")
  peso_m    = d["medidas"]["peso_kg"].get("macho", "—")
  peso_f    = d["medidas"]["peso_kg"].get("femea", "—")
  vida_txt  = d["medidas"].get("expectativa_anos", "—")

  a_min, a_max = parse_minmax(alt_macho)
  if a_min is None: a_min, a_max = parse_minmax(alt_fem)
  p_min, p_max = parse_minmax(peso_m)
  if p_min is None: p_min, p_max = parse_minmax(peso_f)
  v_min, v_max = parse_minmax(vida_txt)

  def qv(min_, max_, unit):
    if min_ is None or max_ is None: return None
    return {"@type":"QuantitativeValue","minValue":min_,"maxValue":max_,"unitCode":unit}

  props = []
  q_alt = qv(a_min, a_max, "CMT")
  q_pes = qv(p_min, p_max, "KGM")
  q_vid = qv(v_min, v_max, "ANN")
  if q_alt: props.append({"@type":"PropertyValue","name":"Altura","value":q_alt})
  if q_pes: props.append({"@type":"PropertyValue","name":"Peso","value":q_pes})
  if q_vid: props.append({"@type":"PropertyValue","name":"Expectativa de vida","value":q_vid})

  return json.dumps({
    "@context":"https://schema.org",
    "@type":"Thing",
    "additionalType":"http://www.productontology.org/id/Dog_breed",
    "name": d["nome"],
    "description": desc,
    "image": d.get("foto", ""),
    "mainEntityOfPage": url,
    "additionalProperty": props
  }, ensure_ascii=False)

#-----------Scores-----------
FUNCOES_TXT = {
    "herding":"pastoreio", "retriever":"recolhedor de caça", "pointer":"cão de aponte",
    "terrier":"controle de pragas", "scent":"farejador", "guard":"guarda",
    "water":"cão d'água", "sight":"cão de caça à vista", "companhia":"companhia"
}
SUGESTOES = {
  "herding": "pastoreio simulado, obediência e truques",
  "retriever": "aportes (buscar e trazer) e natação",
  "pointer": "jogos de aponte e rastros curtos",
  "terrier": "brincadeiras de escavação controladas e caça ao brinquedo",
  "scent": "jogos de faro/caça ao tesouro em casa ou quintal",
  "guard": "obediência, autocontrole e socialização orientada",
  "water": "natação e brincadeiras com água com supervisão",
  "sight": "corridas controladas (lure) e busca visual por alvos",
  "companhia": "passeios leves e interação social diária"
}

def score_atividade(r, rules):
  at = r["atributos"]; grupo = str(at.get("fci_grupo") or "")
  fci_int = rules["fci_base_intensidade"].get(grupo, 3)
  fci_min = rules["fci_base_minutos"].get(grupo, 60)
  intensidade = clamp_0_5(fci_int)
  duracao = clamp_0_5(minutes_to_scale(fci_min))

  mental_map = rules["mental_funcoes"]
  funcoes = at.get("funcoes", []) or []
  estimulo = max((mental_map.get(f, 2) for f in funcoes), default=2)
  estimulo = clamp_0_5(estimulo)

  w = rules["pesos"]["atividade_fisica"]
  val = round_int(clamp_0_5(intensidade*w["intensidade"] + duracao*w["duracao"] + estimulo*w["estimulo_mental"]))

  funcoes_pt = [FUNCOES_TXT.get(f, f) for f in funcoes]
  sugestoes  = [SUGESTOES.get(f) for f in funcoes if SUGESTOES.get(f)]
  dicas = f" Atividades sugeridas: {', '.join(sugestoes)}." if sugestoes else ""

  funcoes = at.get("funcoes", []) or []
  main_func = funcoes[0] if funcoes else None
  func_txt = FUNCOES_TXT.get(main_func) if main_func else None
  ativ_txt = SUGESTOES.get(main_func) if main_func else None
  perfil_str = ""
  if func_txt and ativ_txt:
    perfil_str = f" Seu perfil/função típica é <strong>{func_txt}</strong>, para o qual recomendam-se <strong>{ativ_txt}</strong>."
  elif func_txt:
    perfil_str = f" Seu perfil/função típica é <strong>{func_txt}</strong>."

  texto = (
    f"Os cães da raça {r['nome']} costumam apresentar <strong>nível de energia física {nivel_txt(intensidade)} ({intensidade}/5)</strong>, "
    f"necessitando de atividades de <strong>{duracao_frase(fci_min)}</strong> (≈{fci_min} min/dia) e de "
    f"<strong>exigência cognitiva {nivel_txt(estimulo)} ({estimulo}/5)</strong>. "
    f"{perfil_str}{dicas}"
  )
  return val, texto

PELAGEM_TXT = {
  "sem_pelo": "sem pelo",
  "curta": "curta",
  "media": "média",
  "longa": "longa",
  "encaracolada": "encaracolada",
  "dupla_curta": "dupla curta",
  "dupla_longa": "dupla longa",
}

SUBPELO_TXT = {
  "nenhum": "sem subpelo",
  "leve": "subpelo leve",
  "denso": "subpelo denso",
}

TOSA_TXT = {
  "nao": "não requer tosa",
  "ocasional": "tosa ocasional",
  "regular_8_10": "tosa regular (a cada 8–10 semanas)",
  "regular_4_6": "tosa frequente (a cada 4–6 semanas)",
}

def score_grooming(r, rules):
  at = r["atributos"]
  esc = rules["escovacao_pelo"].get(at.get("pelagem_tipo","curta"), 1)
  shed = rules["shedding_subpelo"].get(at.get("subpelo","nenhum"), 1)
  if at.get("shedding_estacao") in {"moderado","alto"}:
    shed = clamp_0_5(shed + 1)
  tosa = rules["tosa_necessidade"].get(at.get("necessita_tosa","nao"), 1)

  w = rules["pesos"]["higiene_pelagem"]
  val = round_int(clamp_0_5(esc*w["escovacao"] + shed*w["shedding"] + tosa*w["tosa"]))

  pt_pelagem = PELAGEM_TXT.get(at.get("pelagem_tipo","curta"), at.get("pelagem_tipo","curta"))
  pt_subpelo = SUBPELO_TXT.get(at.get("subpelo","nenhum"), at.get("subpelo","nenhum"))
  pt_tosa   = TOSA_TXT.get(at.get("necessita_tosa","nao"), at.get("necessita_tosa","nao"))

  texto = (
    f"Para {r['nome']}, a rotina de higiene envolve <strong>escovação {nivel_txt(esc)}</strong> "
    f"(pelagem {pt_pelagem}), <strong>queda de pelos {nivel_txt(shed)}</strong> ({pt_subpelo}) "
    f"e <strong>{pt_tosa}</strong>."
  )
  return val, texto


def calor_score(at):
  s = 3
  if at.get("braquicefalico"): s -= 2
  if at.get("dobras_cutaneas"): s -= 1
  if at.get("pelagem_tipo") in {"longa","encaracolada","dupla_longa"}: s -= 1
  if at.get("subpelo") == "denso": s -= 1
  climas = set(at.get("origem_clima",[]))
  if "tropical" in climas: s += 1
  if "frio" in climas: s -= 1
  return clamp_0_5(s)

def umidade_score(at):
  s = 3
  if at.get("dobras_cutaneas"): s -= 1
  if at.get("subpelo") == "denso": s -= 1
  if at.get("pelagem_tipo") in {"dupla_longa","longa"}: s -= 1
  return clamp_0_5(s)

def espaco_need(porte, atividade_val):
  base = {"pequeno":1.5, "medio":3, "grande":4}.get(porte, 3)
  return clamp_0_5(base + (atividade_val-3)*0.5)

def score_clima(r, rules, atividade_val):
  at = r["atributos"]; perfil = rules["perfil_ambiente"]
  w = rules["pesos"]["clima_ambiente"][perfil]
  s_calor = calor_score(at)
  s_umid  = umidade_score(at)
  need = espaco_need(at.get("porte","medio"), atividade_val)
  s_espaco = 5 - need

  val = round_int(clamp_0_5(s_calor*w["calor"] + s_umid*w["umidade"] + s_espaco*w["espaco"]))
  texto = (
      f"No perfil <strong>{perfil.replace('-', ' ')}</strong>, {r['nome']} apresenta <strong>tolerância ao calor {nivel_txt(s_calor)}</strong>, "
      f"<strong>tolerância à umidade {nivel_txt(s_umid)}</strong> e <strong>compatibilidade de espaço {nivel_txt(s_espaco)}</strong>."
  )
  return val, texto

#-----------Loads-----------
site = json.loads((ROOT/"data/site.json").read_text(encoding="utf-8"))
BASE = site.get("base_url", "https://www.guiaracas.com.br")
rules = json.loads((ROOT/"data/rules.json").read_text(encoding="utf-8"))

tpl = Template((ROOT/"templates/detalhe-raca.html").read_text(encoding="utf-8"))
head_base = Template((ROOT/"templates/head-base.html").read_text(encoding="utf-8")).safe_substitute(baseUrl=BASE)

racas = json.loads((ROOT/"data/racas.json").read_text(encoding="utf-8"))
out_dir = ROOT/"racas"; out_dir.mkdir(exist_ok=True)

#-----------Gerador-----------
for r in racas:
  slug = slugify(r["nome"])
  url = f"{BASE}/racas/{slug}.html"

  lead = r.get("lead") or r.get("notas", {}).get("resumo", "")

  alt = r["medidas"]["altura_cm"]
  altura_texto = f"{alt.get('macho','—')} ♂ / {alt.get('femea','—')} ♀ cm"

  pes = r["medidas"]["peso_kg"]
  peso_texto = f"{pes.get('macho','—')} ♂ / {pes.get('femea','—')} ♀ kg"

  vida_texto = f"{r['medidas'].get('expectativa_anos','—')} anos"

  atividade, detA = score_atividade(r, rules)
  grooming, detG  = score_grooming(r, rules)
  clima, detC     = score_clima(r, rules, atividade)

  grupo = r["atributos"].get("fci_grupo")
  fci_grupo_txt = f"Grupo {grupo}" if grupo else "—"
  fci_desc = rules["fci_grupos"].get(str(grupo), "—")

  foto_src = r.get("foto","") or "/assets/breeds/_placeholder.png"
  if foto_src.startswith("/"):
    foto_src = f"{BASE}{foto_src}"


  html = tpl.safe_substitute(
    HEAD_BASE=head_base, baseUrl=BASE, url=url, slug=slug,
    SITE_HEADER="", SITE_FOOTER="",
    nome=r["nome"], lead=lead,
    origem=r.get("origem","—"),
    fci_grupo=fci_grupo_txt, fci_descricao=fci_desc,
    fci_codigo=r.get("fci_codigo","—"),
    altura_texto=altura_texto, peso_texto=peso_texto, vida_texto=vida_texto,
    atividade=atividade, grooming=grooming, clima=clima,
    detalhe_atividade_html=detA, detalhe_grooming_html=detG, detalhe_clima_html=detC,
    foto=r.get("foto",""), foto_w=r.get("foto_w",""), foto_h=r.get("foto_h",""),
    foto_credito=r.get("foto_credito",""),
    jsonld_breadcrumb=jsonld_breadcrumb(r["nome"], url),
    jsonld_breed=jsonld_breed(r, url),
  )

  (out_dir/f"{slug}.html").write_text(html, encoding="utf-8")
