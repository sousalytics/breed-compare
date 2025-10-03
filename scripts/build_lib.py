from pathlib import Path
from html import escape as _escape
import json
import unicodedata
import re

# ===== Paths / Carregamento =====
ROOT = Path(__file__).resolve().parents[1]

def load_all():
    """Carrega site, regras e raças."""
    site  = json.loads((ROOT/"data/site.json").read_text(encoding="utf-8"))
    rules = json.loads((ROOT/"data/rules.json").read_text(encoding="utf-8"))
    racas = json.loads((ROOT/"data/racas.json").read_text(encoding="utf-8"))
    return site, rules, racas

def load_aliases_map():
    p = ROOT / "data" / "aliases_oficiais.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

# ===== Utilitários =====
rng = re.compile(r"(\d+)\D+(\d+)")

def attr(s: str) -> str:
    return _escape(s or "", quote=True)

def slugify(s: str) -> str:
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

def join_pt(itens):
    itens = [i for i in itens if i]
    if not itens:
        return ""
    if len(itens) == 1:
        return itens[0]
    if len(itens) == 2:
        return f"{itens[0]} e {itens[1]}"
    return ", ".join(itens[:-1]) + " e " + itens[-1]

def human_pelo(p):
    return {
        "sem_pelo": "sem pelo", "curta": "curta", "media": "média",
        "longa": "longa", "encaracolada": "encaracolada",
        "dupla_curta": "dupla curta", "dupla_longa": "dupla longa"
    }.get(p, p.replace("_", " "))

def freq_escovacao_from_pelo(pelo):
    return {
        "sem_pelo": "1x/semana ou conforme necessário",
        "curta": "1–2x/semana",
        "dupla_curta": "2–3x/semana",
        "media": "2–3x/semana",
        "longa": "3–5x/semana",
        "encaracolada": "diária ou em dias alternados",
        "dupla_longa": "diária"
    }.get(pelo, "2–3x/semana")

def shedding_text(subpelo, shedding_estacao):
    base = {"nenhum": "baixa", "leve": "moderada", "denso": "alta"}.get(subpelo, "moderada")
    saz  = " com picos sazonais" if shedding_estacao in {"alto","moderado"} else ""
    under = {"nenhum":"não possui subpelo","leve":"possui subpelo leve","denso":"possui subpelo denso"}.get(subpelo, "")
    return base, saz, under

def tosa_text(need):
    return {
        "nao": "não requer tosa",
        "ocasional": "requer tosa ocasional",
        "regular_8_10": "requer tosa regular (a cada 8–10 semanas)",
        "regular_4_6": "requer tosa frequente (a cada 4–6 semanas)"
    }.get(need, "não requer tosa")

def ambiente_label(s_espaco):
    if s_espaco >= 4.5:
        return "apartamento pequeno (≤ 50 m²), com passeios diários e enriquecimento"
    if s_espaco >= 3.6:
        return "apartamento médio (50–80 m²)"
    if s_espaco >= 2.6:
        return "apartamento amplo ou casa pequena"
    if s_espaco >= 1.6:
        return "casa com quintal"
    return "área ampla (quintal grande/chácara)"

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

def breed_slug(r):
    return (r.get("slug") or slugify(r["nome"]))

def get_aliases_for_breed(r, aliases_map):
    sl = breed_slug(r)
    arr = aliases_map.get(sl) or []
    seen, out = set(), []
    for a in arr:
        a = (a or "").strip()
        if a and a.lower() not in seen:
            seen.add(a.lower())
            out.append(a)
    return out

def human_porte(p):
    m = {"mini":"Mini","pequeno":"Pequeno","medio":"Médio","grande":"Grande","gigante":"Gigante"}
    return m.get((p or "").lower(), "—")

# ===== Scores / Textos =====
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
    at = r["atributos"]
    grupo = str(at.get("fci_grupo") or "")
    fci_int = rules["fci_base_intensidade"].get(grupo, 3)
    fci_min = rules["fci_base_minutos"].get(grupo, 60)
    intensidade = clamp_0_5(fci_int)

    # === Funções/perfil + estimulação cognitiva ===
    funcoes = at.get("funcoes", []) or []
    funcao_pref = at.get("funcao_principal")

    main_func = funcao_pref if (funcao_pref and funcao_pref in funcoes) else (funcoes[0] if funcoes else None)
    funcoes_escolhidas = [f for f in [main_func] if f]
    # opcional: mostra no máx. 2 funções (principal + 1)
    if funcoes:
        for f in funcoes:
            if f and f != main_func:
                funcoes_escolhidas.append(f)
                break

    estimulo_map = rules["mental_funcoes"]
    estimulo_vals = [estimulo_map.get(f, 2) for f in funcoes] or [2]
    estimulo = clamp_0_5(max(estimulo_vals))

    # === Score final (0–5) com pesos ===
    w = rules["pesos"]["atividade_fisica"]
    val = round_int(
        clamp_0_5(
            intensidade * w["intensidade"]
            + minutes_to_scale(fci_min) * w["duracao"]
            + estimulo * w["estimulo_mental"]
        )
    )

    # === Texto base (sempre mostrado) ===
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

    mins_chunk = f" (≈{fci_min} min/dia)" if fci_min is not None else ""
    texto = (
        f"Os cães da raça {r['nome']} costumam apresentar "
        f"<strong>nível de energia física {nivel_txt(intensidade)}</strong>, "
        f"necessitando de atividades de <strong>{duracao_frase(fci_min)}</strong>{mins_chunk} "
        f"e de <strong>exigência cognitiva {nivel_txt(estimulo)}</strong>."
    )

    # === Frase final (perfil + sugestões) no estilo antigo ===
    def fun_pt(code: str) -> str:
        return FUNCOES_TXT.get(code, (code or "").replace("_", " "))

    def sug(code: str) -> str | None:
        return SUGESTOES.get(code)

    def tokenizar(s: str) -> list[str]:
        # normaliza e extrai tokens legíveis/deduplicáveis
        s = (s or "").lower()
        s = s.replace("com supervisão", "").strip()
        s = s.replace(" e ", ", ")
        parts = [p.strip() for p in s.split(",") if p.strip()]
        tokens: list[str] = []
        for p in parts:
            if "natação" in p or "água" in p:
                tokens.append("atividades aquáticas supervisionadas")
            elif "aportes" in p or "apporte" in p or "buscar e trazer" in p:
                tokens.append("aportes (buscar e trazer)")
            else:
                tokens.append(p)
        return tokens

    funcs_txt = [fun_pt(f) for f in funcoes_escolhidas if f]
    funcao_txt = " e ".join(funcs_txt) if funcs_txt else ""
    perfil_label = "Seus perfis/funções típicas são" if len(funcs_txt) > 1 else "Seu perfil/função típica é"

    # monta trailer de atividades (deduplicado)
    todos_tokens: list[str] = []
    for f in funcoes_escolhidas:
        s = sug(f)
        if s:
            todos_tokens += tokenizar(s)
    uniq: list[str] = []
    seen: set[str] = set()
    for t in todos_tokens:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    atividades_final = join_pt(uniq)

    if funcao_txt:
        if atividades_final:
            ativ_trailer = (", para as quais recomendam-se <strong>" if len(funcs_txt) > 1
                            else ", para o qual recomendam-se <strong>")
            ativ_trailer += f"{atividades_final}</strong>."
        else:
            ativ_trailer = "."
        texto += f" {perfil_label} de <strong>{funcao_txt}</strong>{ativ_trailer}"
    else:
        ativ_trailer = ""  # nada a dizer; mantém texto base

    # === Facts para UI/JSON (compatível com novo e antigo) ===
    facts = {
        # usados hoje:
        "nivel_fisico_txt": nivel_txt(intensidade),
        "minutos_dia": fci_min,
        "exigencia_cog_txt": nivel_txt(estimulo),
        "perfil_txt": funcao_txt,                   # ex: "recolhedor de caça" ou "recolhedor de caça e farejador"
        "sugestoes_txt": atividades_final,          # ex: "aportes (buscar e trazer), atividades aquáticas supervisionadas"
        # compat com template antigo:
        "perfil_label": perfil_label,               # "Seu perfil/função típica é" | "Seus perfis/funções típicas são"
        "funcao_txt": funcao_txt,                   # lista PT-BR
        "ativ_txt_trailer": ativ_trailer,           # pontuação + conjunção já pronta
    }
    return val, texto, facts

def score_grooming(r, rules):
    at = r["atributos"]
    pelo = at.get("pelagem_tipo", "curta")
    subpelo = at.get("subpelo", "nenhum")
    shed_est = at.get("shedding_estacao", "baixo")
    need_tosa = at.get("necessita_tosa", "nao")

    esc = rules["escovacao_pelo"].get(pelo, 1)
    shed = rules["shedding_subpelo"].get(subpelo, 1)
    if shed_est in {"moderado","alto"}:
        shed = clamp_0_5(shed + 1)
    tosa = rules["tosa_necessidade"].get(need_tosa, 1)

    w = rules["pesos"]["higiene_pelagem"]
    val = round_int(clamp_0_5(esc*w["escovacao"] + shed*w["shedding"] + tosa*w["tosa"]))

    esc_txt = {1:"escovação simples", 2:"escovação regular", 3:"escovação cuidadosa", 4:"escovação intensiva"}.get(esc, "escovação regular")
    freq_txt = freq_escovacao_from_pelo(pelo)
    shed_nivel, shed_saz, under_txt = shedding_text(subpelo, shed_est)
    tosa_txt = tosa_text(need_tosa)
    pelo_hum = human_pelo(pelo)

    texto = (
        f"Para os cães da raça {r['nome']}, recomenda-se <strong>{esc_txt}</strong> "
        f"(<strong>{freq_txt}</strong>), devido a sua pelagem {pelo_hum}; "
        f"eles apresentam <strong>queda de pelos {shed_nivel}</strong>{shed_saz}"
        f"{(' — ' + under_txt) if under_txt else ''}; "
        f"e <strong>{tosa_txt}</strong>."
    )

    facts = {"escovacao_txt": freq_txt, "queda_txt": f"{shed_nivel}{shed_saz}", "tosa_txt": tosa_txt}
    return val, texto, facts

def calor_score(at):
    s = 3
    if at.get("braquicefalico"):
        s -= 2
    if at.get("dobras_cutaneas"):
        s -= 1
    if at.get("pelagem_tipo") in {"longa","encaracolada","dupla_longa"}:
        s -= 1
    if at.get("subpelo") == "denso":
        s -= 1
    climas = set(at.get("origem_clima",[]))
    if "tropical" in climas:
        s += 1
    if "frio" in climas:
        s -= 1
    return clamp_0_5(s)

def umidade_score(at):
    s = 3
    if at.get("dobras_cutaneas"):
        s -= 1
    if at.get("subpelo") == "denso":
        s -= 1
    if at.get("pelagem_tipo") in {"dupla_longa","longa"}:
        s -= 1
    return clamp_0_5(s)

def espaco_need(porte, atividade_val):
    base = {"pequeno":1.5, "medio":3, "grande":4}.get(porte, 3)
    return clamp_0_5(base + (atividade_val-3)*0.5)

def score_clima(r, rules, atividade_val):
    at = r["atributos"]
    perfil = rules["perfil_ambiente"]
    w = rules["pesos"]["clima_ambiente"][perfil]
    s_calor = calor_score(at)
    s_umid = umidade_score(at)
    need = espaco_need(at.get("porte","medio"), atividade_val)
    s_espaco = clamp_0_5(5 - need)  # maior = adapta melhor a espaços menores
    val = round_int(clamp_0_5(s_calor*w["calor"] + s_umid*w["umidade"] + s_espaco*w["espaco"]))

    perfil_hum = perfil.replace("-", " ")
    ambiente = ambiente_label(s_espaco)

    texto = (
        f"No clima <strong>{perfil_hum}</strong>, os cães da raça {r['nome']} apresentam "
        f"<strong>tolerância ao calor {nivel_txt(s_calor)}</strong>, "
        f"<strong>tolerância à umidade {nivel_txt(s_umid)}</strong> e "
        f"<strong>adaptam-se melhor a {ambiente}</strong>."
    )
    facts = {
        "perfil_txt": perfil_hum,
        "tolerancia_calor_txt": nivel_txt(s_calor),
        "tolerancia_umidade_txt": nivel_txt(s_umid),
        "adaptacao_espaco_txt": ambiente
    }
    return val, texto, facts
