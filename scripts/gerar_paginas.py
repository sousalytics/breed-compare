from pathlib import Path
import json, html

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
  if m <= 20: return 1
  if m <= 40: return 2
  if m <= 60: return 3
  if m <= 90: return 4
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
    def href(path): return f"{BASE_URL}{path}"
    header = f"""
<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="{href('/')}">Guia Raças<span class="sr-only"> — Página inicial</span></a>
    <nav class="site-nav" aria-label="Navegação principal">
      <ul class="menu">
        <li class="menu__item"><a class="menu__link" href="{href('/racas/')}"{arcur('/racas/')}>Raças</a></li>
        <li class="menu__item"><a class="menu__link" href="{href('/comparar/')}">Comparar</a></li>
        <li class="menu__item"><a class="menu__link" href "{href('/guia-responsavel/')}">Guia responsável</a></li>
        <li class="menu__item"><a class="menu__link" href="{href('/sobre/')}">Sobre</a></li>
      </ul>
    </nav>
  </div>
</header>""".strip()
    footer = f"""
<footer class="site-footer" role="contentinfo">
  <nav class="footer-nav" aria-label="Links institucionais">
    <a href="{href('/sitemap.html')}">Mapa do site</a>
    <a href="{href('/acessibilidade/')}">Acessibilidade</a>
    <a href="{href('/privacidade/')}">Privacidade</a>
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
  return clamp(roundi(s / (w or 1.0)))

def build_citation_index(fontes, citacoes):
  by_id = {f["id"]: f for f in (fontes or []) if "id" in f}
  ordered_ids, id_to_num = [], {}
  for _, ids in (citacoes or {}).items():
      for fid in ids:
          if fid in by_id and fid not in id_to_num:
              id_to_num[fid] = len(ordered_ids) + 1
              ordered_ids.append(fid)
  return id_to_num, ordered_ids, by_id

def cite_badge(ids, id_to_num, by_id):
  nums = [id_to_num[i] for i in ids if i in id_to_num]
  if not nums: return ""
  nomes = "; ".join(by_id[i]["nome"] for i in ids if i in by_id)
  links = ", ".join(f'<a href="#ref-{n}">{n}</a>' for n in nums)
  return f'<sup class="ref-badge" title="{html.escape(nomes)}" aria-label="Ver fontes: {html.escape(nomes)}">[{links}]</sup>'

def render_references_list(ordered_ids, by_id):
  items = []
  for n, fid in enumerate(ordered_ids, start=1):
      f = by_id.get(fid, {})
      nome = html.escape(f.get("nome","")); tipo = html.escape(f.get("tipo",""))
      url  = html.escape(f.get("url",""));  lic  = html.escape(f.get("licenca","—"))
      acc  = html.escape(f.get("acessado_em",""))
      a = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{nome}</a>' if url else nome
      small = f' <small>({lic}; acessado em {acc})</small>' if (lic or acc) else ""
      items.append(f'<li id="ref-{n}"><span class="ref-tipo">{tipo}</span>: {a}{small}</li>')
  return "\n      ".join(items)

def format_source_links(ids, id_to_num, by_id):
    links = []
    for fid in ids or []:
        n = id_to_num.get(fid)
        f = by_id.get(fid, {})
        nome = html.escape(f.get("nome", "Fonte"))
        if n:
            links.append(f'<a href="#ref-{n}">{nome}</a>')
        else:
            links.append(nome)
    return ", ".join(links)

def render_proveniencia(citacoes, id_to_num, by_id):
    linhas = []
    def add(rotulo, chave):
        ids = (citacoes or {}).get(chave, [])
        if ids:
            linhas.append(f"<li><strong>{rotulo}:</strong> {format_source_links(ids, id_to_num, by_id)}</li>")
    add("Resumo", "resumo")
    add("Observações", "observacoes")
    add("Altura", "medidas.altura_cm")
    add("Peso", "medidas.peso_kg")
    add("Expectativa de vida", "medidas.expectativa_anos")
    return f"<ul>\n      " + "\n      ".join(linhas) + "\n    </ul>" if linhas else "<p>—</p>"

def render_detalhe(b: dict):
    nome = b["nome"]
    slug = b["slug"]
    notas = b.get("notas", {})
    m = b.get("medidas", {})
    attrs = b.get("atributos", {})
    fontes = b.get("fontes", [])
    citacoes = b.get("citacoes", {})

    sub = calc_subescalas(attrs, RULES)
    AF = media_ponderada(sub["atividade_fisica"], RULES["pesos"]["atividade_fisica"])
    HI = media_ponderada(sub["higiene_pelagem"], RULES["pesos"]["higiene_pelagem"])
    perfil = RULES["perfil_ambiente"]
    CL = media_ponderada(sub["clima_ambiente"], RULES["pesos"]["clima_ambiente"][perfil])

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
      .replace("{{NOME}}", html.escape(nome))
      .replace("{{RESUMO}}", html.escape(notas.get("resumo","")))
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
