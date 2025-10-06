# Gera paginas padronizadas a partir dos templates
# (Home/Lista/Detalhe/Comparar/Sobre/Guia Responsável/
# Acessibilidade/Privacidade/Sitemap/404)

from string import Template
from pathlib import Path
import json

from build_lib import (
    ROOT, load_all, load_aliases_map, slugify, attr, join_pt,
    parse_minmax, human_porte, score_atividade, score_grooming, score_clima,
    get_aliases_for_breed
)

# ===== JSON-LD helpers =====
def jsonld_breadcrumb(nome, url, BASE):
    return json.dumps({
        "@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[
          {"@type":"ListItem","position":1,"name":"Início","item":f"{BASE}/"},
          {"@type":"ListItem","position":2,"name":"Raças","item":f"{BASE}/racas/"},
          {"@type":"ListItem","position":3,"name":nome,"item":url}
        ]
    }, ensure_ascii=False)

def jsonld_breadcrumb_list(BASE):
    return json.dumps({
        "@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[
          {"@type":"ListItem","position":1,"name":"Início","item":f"{BASE}/"},
          {"@type":"ListItem","position":2,"name":"Raças","item":f"{BASE}/racas/"}
        ]
    }, ensure_ascii=False)

def jsonld_breadcrumb_compare(BASE):
  url = f"{BASE}/comparar/"
  return json.dumps({
    "@context":"https://schema.org","@type":"BreadcrumbList",
    "itemListElement":[
      {"@type":"ListItem","position":1,"name":"Início","item":f"{BASE}/"},
      {"@type":"ListItem","position":2,"name":"Comparar","item":url}
    ]
  }, ensure_ascii=False)

def jsonld_breed(d, url):
    alt_macho = d["medidas"]["altura_cm"].get("macho", "—")
    alt_fem   = d["medidas"]["altura_cm"].get("femea", "—")
    peso_m    = d["medidas"]["peso_kg"].get("macho", "—")
    peso_f    = d["medidas"]["peso_kg"].get("femea", "—")
    vida_txt  = d["medidas"].get("expectativa_anos", "—")

    def _pm(txt):
        a,b = parse_minmax(txt)
        return None if a is None or b is None else {"@type":"QuantitativeValue","minValue":a,"maxValue":b}
    props=[]
    qa=_pm(alt_macho) or _pm(alt_fem)
    qp=_pm(peso_m)   or _pm(peso_f)
    qv=_pm(vida_txt)
    if qa: props.append({"@type":"PropertyValue","name":"Altura","value":{**qa,"unitCode":"CMT"}})
    if qp: props.append({"@type":"PropertyValue","name":"Peso","value":{**qp,"unitCode":"KGM"}})
    if qv: props.append({"@type":"PropertyValue","name":"Expectativa de vida","value":{**qv,"unitCode":"ANN"}})

    desc = d.get("lead") or d.get("notas", {}).get("resumo", "")
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

# ===== Carregamento de dados e templates =====
site, rules, racas = load_all()
BASE = site.get("base_url", "")

tpl_head = Template((ROOT/"templates/head-base.html").read_text(encoding="utf-8"))
tpl_hdr  = Template((ROOT/"templates/header.html").read_text(encoding="utf-8"))
tpl_ftr  = Template((ROOT/"templates/footer.html").read_text(encoding="utf-8"))

HEAD_BASE   = tpl_head.safe_substitute(baseUrl=BASE)
SITE_HEADER = tpl_hdr.safe_substitute(baseUrl=BASE)
SITE_FOOTER = tpl_ftr.safe_substitute(baseUrl=BASE)

# Templates de páginas
tpl_home    = Template((ROOT/"templates/index.html").read_text(encoding="utf-8"))
tpl_list    = Template((ROOT/"templates/lista-racas.html").read_text(encoding="utf-8"))
tpl_detail  = Template((ROOT/"templates/detalhe-raca.html").read_text(encoding="utf-8"))
tpl_compare = Template((ROOT/"templates/comparar.html").read_text(encoding="utf-8"))
tpl_sobre   = Template((ROOT/"templates/sobre.html").read_text(encoding="utf-8"))
tpl_guia    = Template((ROOT/"templates/guia-responsavel.html").read_text(encoding="utf-8"))
tpl_a11y    = Template((ROOT/"templates/acessibilidade.html").read_text(encoding="utf-8"))
tpl_priv    = Template((ROOT/"templates/privacidade.html").read_text(encoding="utf-8"))
tpl_404     = Template((ROOT/"templates/404.html").read_text(encoding="utf-8"))
tpl_map     = Template((ROOT/"templates/sitemap.html").read_text(encoding="utf-8"))

# ===== Helpers de render =====
aliases_map = load_aliases_map()

def render_card(r):
    """Card da listagem — compatível com o CSS 'A2 teal' e com main.js (filtros)."""
    slug  = r.get("slug") or slugify(r["nome"])
    grupo = r["atributos"].get("fci_grupo")
    porte = (r["atributos"].get("porte") or "").lower()
    foto  = r.get("foto","") or "/assets/breeds/_placeholder.jpg"
    if foto.startswith("/"):
        foto = f"{BASE}{foto}"

    aliases = get_aliases_for_breed(r, aliases_map)
    alias_attr = " | ".join(a for a in aliases if a)

    badge = f"Grupo {grupo}" if grupo else "—"

    return (
      f"<li class='breed-card' "
      f" data-name='{attr(r['nome'])}'"
      f" data-porte='{attr(porte)}'"
      f" data-grupo='{attr(str(grupo or ''))}'"
      f" data-alias='{attr(alias_attr)}'>"
      f"  <div class='breed-card__media'>"
      f"    <img src='{foto}' alt='' loading='lazy' decoding='async' width='480' height='320' />"
      f"  </div>"
      f"  <div class='breed-card__body'>"
      f"    <h3 class='breed-card__title'><a href='{BASE}/racas/{slug}.html'>{attr(r['nome'])}</a></h3>"
      f"    <p class='breed-card__meta'>Origem: {attr(r.get('origem','—'))}</p>"
      f"    <span class='badge'>{attr(badge)}</span>"
      f"  </div>"
      f"  <div class='breed-card__actions'>"
      f"    <a class='btn btn--full js-compare-add' data-slug='{slug}' href='{BASE}/comparar/?add={slug}'>+ Comparar</a>"
      f"  </div>"
      f"</li>"
    )

def render_pop_block(r):
    pop = r.get("popularidade")
    if not isinstance(pop, dict) or not pop:
        return "<section class='pop'><div class='pop__bars'></div></section>"

    def pick(label, key):
        v = pop.get(key)
        if isinstance(v, (int, float)):
            val = max(0, min(100, int(v)))
            return (label, val)
        return None

    items = [pick("Brasil", "br"), pick("Global", "global")]
    items = [x for x in items if x]
    if not items:
        return "<section class='pop'><div class='pop__bars'></div></section>"

    rows = []
    for label, val in items[:2]:
        rows.append(
            f"<div class='pop__row'>"
            f"<span>{attr(label)}</span>"
            f"<span class='pop__track'><span class='pop__fill' style='inline-size:{val}%'></span></span>"
            f"<span>{val}%</span>"
            f"</div>"
        )
    return "<section class='pop'><h2 class='visually-hidden'>Popularidade</h2><div class='pop__bars'>" + "".join(rows) + "</div></section>"

def _top5_by(key):
    # key: "br" ou "global"
    usable = []
    for r in racas:
        v = (r.get("popularidade") or {}).get(key)
        if isinstance(v, (int, float)):
            usable.append((r, int(max(0, min(100, v)))))
    usable.sort(key=lambda t: t[1], reverse=True)
    return usable[:5]

def _rank_items_html(items):
    out = []
    for r, v in items:
        slug = r.get("slug") or slugify(r["nome"])
        out.append(
            f"<li class='rank'>"
            f"  <a href='{BASE}/racas/{slug}.html'>{attr(r['nome'])}</a>"
            f"  <span class='rank__value'>{int(v)}</span>"
            f"  <span class='rank__bar' aria-hidden='true' style='--v:{int(v)}'></span>"
            f"</li>"
        )
    return '\n'.join(out)

br_top5 = _rank_items_html(_top5_by("br"))
gl_top5 = _rank_items_html(_top5_by("global"))

def render_foto_block(r):
    src = r.get("foto","") or "/assets/breeds/_placeholder.jpg"
    if src.startswith("/"):
        src = f"{BASE}{src}"
    w = r.get("foto_w") or 640
    h = r.get("foto_h") or 426
    credito = r.get("foto_credito", "")
    cap = f"<figcaption class='photo__cap'>{attr(credito)}</figcaption>" if credito else ""
    return (
      "<section class='breed__photo' aria-labelledby='foto-title'>"
      "<h2 id='foto-title' class='visually-hidden'>Foto da raça</h2>"
      f"<img src='{src}' alt='Foto ilustrativa de {attr(r['nome'])}' loading='lazy' width='{w}' height='{h}' />"
      f"{cap}</section>"
    )

def fmt_mf(macho_txt, femea_txt, unidade):
    m = macho_txt or "—"
    f = femea_txt or "—"
    return f"{m} <span class='sex sex--m' aria-hidden='true'>♂</span> / {f} <span class='sex sex--f' aria-hidden='true'>♀</span> {unidade}"

# ===== Geração: páginas por raça =====
out_breeds = ROOT / "racas"
out_breeds.mkdir(exist_ok=True)

for r in racas:
    slug = slugify(r["nome"])
    url  = f"{BASE}/racas/{slug}.html"

    # textos e métricas
    lead = r.get("lead") or r.get("notas", {}).get("resumo", "")
    alt = r.get("medidas", {}).get("altura_cm", {}) or {}
    altura_texto_html = fmt_mf(alt.get("macho"), alt.get("femea"), "cm")
    peso = r.get("medidas", {}).get("peso_kg", {}) or {}
    peso_texto_html = fmt_mf(peso.get("macho"), peso.get("femea"), "kg")
    vida_texto = f"{r['medidas'].get('expectativa_anos','—')} anos"

    atividade_val, detA_txt, _factsA = score_atividade(r, rules)
    grooming_val,  detG_txt, _factsG = score_grooming(r, rules)
    clima_val,     detC_txt, _factsC = score_clima(r, rules, atividade_val)

    grupo = r["atributos"].get("fci_grupo")
    fci_grupo_txt = f"Grupo {grupo}" if grupo else "—"
    fci_desc = rules["fci_grupos"].get(str(grupo), "—")
    porte_slug = (r["atributos"].get("porte") or "").lower()
    porte_label = human_porte(porte_slug)

    # AKA somente texto
    aliases = get_aliases_for_breed(r, aliases_map)
    aka_html = attr(join_pt(aliases)) if aliases else ""

    page_html = tpl_detail.safe_substitute(
        HEAD_BASE=HEAD_BASE, baseUrl=BASE, url=url, slug=slug,
        SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER,
        nome=r["nome"], lead=lead,
        origem=r.get("origem","—"),
        fci_grupo=fci_grupo_txt, fci_descricao=fci_desc,
        fci_codigo=r.get("fci_codigo","—"),
        porte_label=porte_label, porte_slug=porte_slug,
        altura_texto_html=altura_texto_html, peso_texto_html=peso_texto_html, vida_texto=vida_texto,
        atividade=atividade_val, grooming=grooming_val, clima=clima_val,
        detalhe_atividade_html=detA_txt, detalhe_grooming_html=detG_txt, detalhe_clima_html=detC_txt,
        aka_html=aka_html,
        POPULARIDADE_BLOCK=render_pop_block(r),
        FOTO_BLOCK=render_foto_block(r),
        jsonld_breadcrumb=jsonld_breadcrumb(r["nome"], url, BASE),
        jsonld_breed=jsonld_breed(r, url)
    )
    (out_breeds/f"{slug}.html").write_text(page_html, encoding="utf-8")

# ===== Página: /racas/index.html =====
cards_html = "\n".join(render_card(r) for r in sorted(racas, key=lambda x: x["nome"]))
html_list = tpl_list.safe_substitute(
    HEAD_BASE=HEAD_BASE, baseUrl=BASE,
    SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER,
    LISTA_RACAS_ITEMS=cards_html,
    jsonld_breadcrumb_list=jsonld_breadcrumb_list(BASE)
)
(out_breeds/"index.html").write_text(html_list, encoding="utf-8")

# ===== Página: /comparar/index.html =====
out_cmp = ROOT / "comparar"
out_cmp.mkdir(exist_ok=True)
html_cmp = tpl_compare.safe_substitute(
    HEAD_BASE=HEAD_BASE, baseUrl=BASE,
    SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER,
    jsonld_breadcrumb_compare=jsonld_breadcrumb_compare(BASE)
)
(out_cmp/"index.html").write_text(html_cmp, encoding="utf-8")

# ===== Páginas estáticas =====
ROOT.write_text("", encoding="utf-8") if not ROOT.exists() else None  # no-op

# Home
(ROOT/"index.html").write_text(
    tpl_home.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER, BR_TOP5_ITEMS=br_top5, GLOBAL_TOP5_ITEMS=gl_top5),
    encoding="utf-8"
)
# Sobre
(out_dir:=ROOT/"sobre").mkdir(exist_ok=True)
(out_dir/"index.html").write_text(
    tpl_sobre.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)
# Guia Responsável
(out_dir:=ROOT/"guia-responsavel").mkdir(exist_ok=True)
(out_dir/"index.html").write_text(
    tpl_guia.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)
# Acessibilidade
(out_dir:=ROOT/"acessibilidade").mkdir(exist_ok=True)
(out_dir/"index.html").write_text(
    tpl_a11y.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)
# Privacidade
(out_dir:=ROOT/"privacidade").mkdir(exist_ok=True)
(out_dir/"index.html").write_text(
    tpl_priv.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)
# Sitemap (HTML)
(ROOT/"sitemap.html").write_text(
    tpl_map.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)
# 404
(ROOT/"404.html").write_text(
    tpl_404.safe_substitute(HEAD_BASE=HEAD_BASE, baseUrl=BASE, SITE_HEADER=SITE_HEADER, SITE_FOOTER=SITE_FOOTER),
    encoding="utf-8"
)

print("[ok] Páginas geradas: Home, Raças (lista+detalhes), Comparar, Sobre, Guia, Acessibilidade, Privacidade, Sitemap, 404")
