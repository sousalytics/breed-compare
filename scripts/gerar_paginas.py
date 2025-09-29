from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parents[1]

def read_text(p:Path) -> str:
  return p.read_text(encoding="utf-8")

def write_text(p:Path, s: str):
  p.parent.mkdir(parents=True, exist_ok=True)
  p.write_text(s, encoding="utf-8")

def clamp(v, lo=0, hi=5):
  return max(lo, min(hi, v))

def roundi(v):
  return int(round(v))

def bucket_minutos(m):
  if m <= 20:
    return 1
  if m <= 40:
    return 2
  if m <= 60:
    return 3
  if m <= 90:
    return 4
  return 5

SITE = json.loads(read_text(ROOT / "data" / "site.json"))
RULES = json.loads(read_text(ROOT / "data" / "rules.json"))
BREEDS = json.loads(read_text(ROOT / "data" / "racas.json"))

BASE_URL = SITE.get("base_url","").rstrip("/")
ROBOTS = SITE.get("robots","noindex, nofollow")

def render_head(title: str, description: str, canonical: str) -> str:
  head_tpl = read_text(ROOT / "templates" / "head-base.html")
  return (head_tpl
          .replace("{{TITLE}}", html.escape(title))
          .replace("{{DESCRIPTION}}", html.escape(description))
          .replace("{{CANONICAL}}", canonical)
          .replace("{{ROBOTS}}", ROBOTS)
          .replace("{{BASE_URL}}", BASE_URL))

def render_chrome(active: str) -> tuple[str,str]:
  def arcur(h):
    return ' aria-current="page"' if h == active else ""
  def href(path):
    return f"{BASE_URL}{path}"
  header = f"""
<header class="header">
  <div class="header__inner">
    <a class="logo" href="{href('/')}">Guia Raças<span class="visually-hidden"> — Página inicial</span></a>
    <nav class=".nav" aria-label="Navegação principal">
      <ul class="nav__list">
        <li class="nav__item"><a class="nav__link" href="{href('/racas/')}"{arcur('/racas/')}>Raças</a></li>
        <li class="nav__item"><a class="nav__link" href="{href('/comparar/')}">Comparar</a></li>
        <li class="nav__item"><a class="nav__link" href="{href('/guia-responsavel/')}">Guia responsável</a></li>
        <li class="nav__item"><a class="nav__link" href="{href('/sobre/')}">Sobre</a></li>
      </ul>
    </nav>
  </div>
</header>""".strip()

  footer = f"""
<footer class="footer" role="contentinfo">
  <nav class="footer__nav" aria-label="Links institucionais">
    <a class="footer__link" href="{href('/sitemap.html')}">Mapa do site</a>
    <a class="footer__link" href="{href('/acessibilidade/')}">Acessibilidade</a>
    <a class="footer__link" href="{href('/privacidade/')}">Privacidade</a>
  </nav>
  <p>&copy; 2025 Guia Raças</p>
</footer>""".strip()
  return header, footer


def wrap_html(head: str, body: str, active: str) -> str:
  header, footer = render_chrome(active)
  skip = '<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>'
  return f"<!doctype html><html lang='pt-BR'><head>{head}</head><body>{skip}{header}{body}{footer}</body></html>"

def calc_subescalas(a: dict, r: dict) -> dict:
  fci = a.get("fci_grupo")
  porte = a.get("porte")
  braq = bool(a.get("braquicefalico"))
  pelo = a.get("pelagem_tipo")
  subp = a.get("subpelo")
  shed = a.get("shedding_estacao")
  tosa = a.get("necessita_tosa")
  dobras = bool(a.get("dobras_cutaneas"))
  fun = a.get("funcoes",[]) or []
  origem = a.get("origem_clima",[]) or []

  base_int   = r["fci_base_intensidade"]
  base_min   = r["fci_base_minutos"]
  mental_map = r["mental_funcoes"]
  escov_map  = r["escovacao_pelo"]
  shed_map   = r["shedding_subpelo"]
  tosa_map   = r["tosa_necessidade"]

  intensidade = int(base_int.get(str(fci),3))
  if braq:
    intensidade -= 2
  if any(x in {"resgate","assistencia","trabalho_forca"} for x in fun):
    intensidade += 1
  if porte == "gigante":
    intensidade -= 1
  intensidade = clamp(intensidade)

  mins = int(base_min.get(str(fci),60))
  if braq:
    mins -= 20
  if porte == "gigante":
    mins -= 15
  if any(x in {"resgate","trabalho_forca"} for x in fun):
    mins += 15
  mins = max(15, min(120, mins))
  duracao = bucket_minutos(mins)

  base_mental = max([mental_map.get(x,0) for x in fun] + [0])
  mental = base_mental + (1 if any(x in {"resgate","assistencia"} for x in fun) else 0) - (1 if braq else 0)
  mental = clamp(mental)

  escov = int(escov_map.get(pelo,2))
  if subp == "denso":
    escov += 1
  if pelo in {"encaracolada","dupla_longa"}:
    escov += 1
  escov = clamp(escov,1,5)

  shedding = int(shed_map.get(subp,3))
  if shed in {"alto","explosivo"}:
    shedding += 1
  if pelo == "sem_pelo":
    shedding -= 1
  shedding = clamp(shedding)

  tosa_n = int(tosa_map.get(tosa,2)) + (1 if dobras else 0)
  tosa_n = clamp(tosa_n,1,5)

  calor = 3
  if braq:
    calor -= 2
  if subp == "denso":
    calor -= 1
  if pelo in {"sem_pelo","curta"}:
    calor += 1
  if porte == "gigante":
    calor -= 1
  if any(x in {"tropical","deserto"} for x in origem):
    calor += 1
  calor = clamp(calor)

  umidade = 3
  if subp == "denso":
    umidade -= 1
  if dobras:
    umidade -= 1
  if pelo in {"sem_pelo","curta"}:
    umidade += 1
  if "tropical" in origem:
    umidade += 1
  umidade = clamp(umidade)

  demanda = (intensidade + duracao) / 2.0
  base = 6 - roundi(demanda)
  pen = {"mini":0,"pequeno":0,"medio":1,"grande":2,"gigante":3}.get(porte,1)
  espaco = clamp(base - pen, 1, 5)

  return {
      "atividade_fisica": {"intensidade":intensidade, "duracao":duracao, "estimulo_mental":mental},
      "higiene_pelagem": {"escovacao":escov, "shedding":shedding, "tosa":tosa_n},
      "clima_ambiente": {"calor":calor, "umidade":umidade, "espaco":espaco}
    }

def media_ponderada(sub: dict, pesos: dict) -> int:
  s = w = 0.0
  for k, p in pesos.items():
    v = sub.get(k)
    if v is not None:
      s += float(v) * float(p)
      w += float(p)
  return clamp(roundi(s / (w or 1.0)), 1, 5)

def build_citation_index(fontes, citacoes):
  by_id = {f["id"]: f for f in (fontes or []) if "id" in f}
  ordered_ids, id_to_num = [], {}
  for _, ids in (citacoes or {}).items():
      for fid in ids:
          if fid in by_id and fid not in id_to_num:
              id_to_num[fid] = len(ordered_ids) + 1
              ordered_ids.append(fid)
  return id_to_num, ordered_ids, by_id

def render_references_list(ordered_ids, by_id):
  items = []
  for n, fid in enumerate(ordered_ids, start=1):
      f = by_id.get(fid, {})
      nome = html.escape(f.get("nome",""))
      tipo = html.escape(f.get("tipo",""))
      url  = html.escape(f.get("url",""))
      lic  = html.escape(f.get("licenca","—"))
      acc  = html.escape(f.get("acessado_em",""))
      a = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{nome}</a>' if url else nome
      small = f' <small>({lic}; acessado em {acc})</small>' if (lic or acc) else ""
      items.append(f'<li id="ref-{n}"><span class="ref-tipo">{tipo}</span>: {a}{small}</li>')
  return "\n      ".join(items)

def nivel_15(n):
  return {1:"muito baixa", 2:"baixa", 3:"moderada", 4:"alta", 5:"muito alta"}[clamp(int(n),1,5)]

def label_duracao_bucket(n):
  n = clamp(int(n),1,5)
  return ["até 20 min", "21–40 min", "41–60 min", "61–90 min", "90+ min"][n-1]

def label_escovacao(n):
  return {1:"nunca/mensalmente", 2:"quinzenal", 3:"semanal", 4:"2–3×/sem", 5:"diária"}[clamp(int(n),1,5)]

def label_shedding(n):
  return f"queda {nivel_15(n)}"

def label_tosa(n):
  return {1:"nunca", 2:"ocasional", 3:"regular", 4:"frequente", 5:"muito frequente"}[clamp(int(n),1,5)]

def label_tolerancia(n):
  return f"tolerância {nivel_15(n)}"

def label_espaco(n):
  return {1:"apto pequeno", 2:"apto OK", 3:"casa pequena", 4:"casa com quintal", 5:"área ampla/sítio"}[clamp(int(n),1,5)]

def fci_nome(grupo, rules):
  if grupo is None:
    return "—"
  return rules.get("fci_grupos", {}).get(str(grupo), f"Grupo {grupo}")

def compor_texto_indicadores(nome, labels, nums):
  af = f"Os cães da raça {nome} pedem atividade física {labels['AF_INT_TX']} (intensidade {nums['AF_INT']}/5), " \
       f"com duração {labels['AF_DUR_TX']} (nível {nums['AF_DUR']}/5) e " \
       f"estímulo mental {labels['AF_MEN_TX']} (nível {nums['AF_MEN']}/5)."

  hi = f"Em cuidados, a escovação é {labels['HI_ESC_TX']} (nível {nums['HI_ESC']}/5), " \
       f"a queda de pelos é {labels['HI_SHD_TX']} (nível {nums['HI_SHD']}/5) e " \
       f"a tosa é {labels['HI_TOS_TX']} (nível {nums['HI_TOS']}/5)."

  cl = f"Quanto ao ambiente: {labels['CL_CAL_TX']} ao calor (nível {nums['CL_CAL']}/5), " \
       f"{labels['CL_UMI_TX']} à umidade (nível {nums['CL_UMI']}/5) e " \
       f"espaço ideal: {labels['CL_ESP_TX']} (nível {nums['CL_ESP']}/5)."
  return af, hi, cl

def sparkline_svg(data):
  if not data:
    return ""
  w, h, pad = 120, 32, 4
  vs = [max(0, min(100, float(d.get("valor", 0)))) for d in data]
  mx = max(vs) or 1.0
  pts = []
  for i, v in enumerate(vs):
      x = pad + (w - 2*pad) * (i / max(1, (len(vs) - 1)))
      y = h - pad - (h - 2*pad) * (v / mx)
      pts.append(f"{x:.1f},{y:.1f}")
  anos = ", ".join(str(d["ano"]) for d in data)
  return f'''<svg class="pop-spark" viewBox="0 0 {w} {h}" role="img" aria-label="Popularidade por ano">
  <title>Popularidade por ano</title>
  <desc>Anos: {anos}. Valores relativos 0–100.</desc>
  <polyline fill="none" stroke="currentColor" stroke-width="2" points="{' '.join(pts)}" />
</svg>'''

def render_detalhe(b: dict):
  nome = b["nome"]
  slug = b["slug"]
  notas = b.get("notas", {})
  m = b.get("medidas", {})
  attrs = b.get("atributos", {})
  fontes = b.get("fontes", [])
  citacoes = b.get("citacoes", {})
  fci_nome_txt = fci_nome(attrs.get("fci_grupo"), RULES)

  sub = calc_subescalas(attrs, RULES)
  AF = media_ponderada(sub["atividade_fisica"], RULES["pesos"]["atividade_fisica"])
  HI = media_ponderada(sub["higiene_pelagem"], RULES["pesos"]["higiene_pelagem"])
  perfil = RULES["perfil_ambiente"]
  CL = media_ponderada(sub["clima_ambiente"], RULES["pesos"]["clima_ambiente"][perfil])

  af_i, af_d, af_m = sub["atividade_fisica"]["intensidade"], sub["atividade_fisica"]["duracao"], sub["atividade_fisica"]["estimulo_mental"]
  hi_e, hi_s, hi_t = sub["higiene_pelagem"]["escovacao"], sub["higiene_pelagem"]["shedding"], sub["higiene_pelagem"]["tosa"]
  cl_c, cl_u, cl_e = sub["clima_ambiente"]["calor"], sub["clima_ambiente"]["umidade"], sub["clima_ambiente"]["espaco"]
  labels = {
    "AF_INT_TX": nivel_15(af_i), "AF_DUR_TX": label_duracao_bucket(af_d), "AF_MEN_TX": nivel_15(af_m),
    "HI_ESC_TX": label_escovacao(hi_e), "HI_SHD_TX": label_shedding(hi_s), "HI_TOS_TX": label_tosa(hi_t),
    "CL_CAL_TX": label_tolerancia(cl_c), "CL_UMI_TX": label_tolerancia(cl_u), "CL_ESP_TX": label_espaco(cl_e),
  }

  nums = {"AF_INT":af_i,"AF_DUR":af_d,"AF_MEN":af_m,"HI_ESC":hi_e,"HI_SHD":hi_s,"HI_TOS":hi_t,"CL_CAL":cl_c,"CL_UMI":cl_u,"CL_ESP":cl_e}

  txt_af, txt_hi, txt_cl = compor_texto_indicadores(nome, labels, nums)

  pop_svg = ""
  pop = b.get("popularidade", {})
  series = pop.get("series", [])
  if series:
    pop_svg = sparkline_svg(series)

  id_to_num, ordered_ids, by_id = build_citation_index(fontes, citacoes)
  refs_ol  = render_references_list(ordered_ids, by_id)
  fontes_count = len(ordered_ids)
  metodo_url = f"{BASE_URL}/sobre/#metodologia"

  title = f"{nome} — características, medidas e ambiente | Guia Raças"
  desc  = f"{nome}: resumo, medidas e notas (atividade física, higiene/pelagem, clima/ambiente)."
  canonical = f"{BASE_URL}/racas/{slug}/"
  head = render_head(title, desc, canonical)

  tpl = read_text(ROOT / "templates" / "detalhe-raca.html")
  main = (tpl
    .replace("{{HOME_URL}}", f"{BASE_URL}/")
    .replace("{{RACAS_URL}}", f"{BASE_URL}/racas/")
    .replace("{{SLUG}}", slug)
    .replace("{{BASE_URL}}", BASE_URL)
    .replace("{{NOME}}", html.escape(nome))
    .replace("{{RESUMO}}", html.escape(notas.get("resumo","")))
    .replace("{{FCI_NOME}}", html.escape(fci_nome_txt))
    .replace("{{POP_SVG}}", pop_svg)
    .replace("{{DET_TXT_AF}}", html.escape(txt_af))
    .replace("{{DET_TXT_HI}}", html.escape(txt_hi))
    .replace("{{DET_TXT_CL}}", html.escape(txt_cl))
    .replace("{{OBSERVACOES}}", html.escape(notas.get("observacoes","")))
    .replace("{{ALTURA_M}}", html.escape(m.get("altura_cm",{}).get("macho","—")))
    .replace("{{ALTURA_F}}", html.escape(m.get("altura_cm",{}).get("femea","—")))
    .replace("{{PESO_M}}", html.escape(m.get("peso_kg",{}).get("macho","—")))
    .replace("{{PESO_F}}", html.escape(m.get("peso_kg",{}).get("femea","—")))
    .replace("{{EXPECTATIVA}}", html.escape(m.get("expectativa_anos","—")))

    .replace("{{AF_TOTAL}}", str(AF)).replace("{{HI_TOTAL}}", str(HI)).replace("{{CL_TOTAL}}", str(CL))

    .replace("{{AF_INTENSIDADE}}", str(sub["atividade_fisica"]["intensidade"]))
    .replace("{{AF_DURACAO}}", str(sub["atividade_fisica"]["duracao"]))
    .replace("{{AF_MENTAL}}", str(sub["atividade_fisica"]["estimulo_mental"]))
    .replace("{{HI_ESCOVACAO}}", str(sub["higiene_pelagem"]["escovacao"]))
    .replace("{{HI_SHEDDING}}", str(sub["higiene_pelagem"]["shedding"]))
    .replace("{{HI_TOSA}}", str(sub["higiene_pelagem"]["tosa"]))
    .replace("{{CL_CALOR}}", str(sub["clima_ambiente"]["calor"]))
    .replace("{{CL_UMIDADE}}", str(sub["clima_ambiente"]["umidade"]))
    .replace("{{CL_ESPACO}}", str(sub["clima_ambiente"]["espaco"]))

    .replace("{{AF_INTENSIDADE_TX}}", labels["AF_INT_TX"])
    .replace("{{AF_DURACAO_TX}}", labels["AF_DUR_TX"])
    .replace("{{AF_MENTAL_TX}}", labels["AF_MEN_TX"])
    .replace("{{HI_ESCOVACAO_TX}}", labels["HI_ESC_TX"])
    .replace("{{HI_SHEDDING_TX}}", labels["HI_SHD_TX"])
    .replace("{{HI_TOSA_TX}}", labels["HI_TOS_TX"])
    .replace("{{CL_CALOR_TX}}", labels["CL_CAL_TX"])
    .replace("{{CL_UMIDADE_TX}}", labels["CL_UMI_TX"])
    .replace("{{CL_ESPACO_TX}}", labels["CL_ESP_TX"])

    .replace("{{SOBRE_METODO_URL}}", metodo_url)
    .replace("{{FONTES_COUNT}}", str(fontes_count))
    .replace("{{REFERENCIAS}}", refs_ol or "<li>Sem fontes cadastradas para esta página.</li>")
  )

  page = wrap_html(head, main, active="/racas/")
  out = ROOT / "racas" / slug / "index.html"
  write_text(out, page)

def main():
  ordered = sorted(BREEDS, key=lambda b: b["slug"])
  for b in ordered:
      render_detalhe(b)
  print(f"Gerei {len(ordered)} páginas de raça em /racas/{{slug}}/")

if __name__ == "__main__":
  main()
