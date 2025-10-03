from pathlib import Path
from string import Template
from html import escape as _escape
import json

from build_lib import (
    ROOT, load_all, load_aliases_map, slugify, attr, join_pt,
    parse_minmax, human_porte, score_atividade, score_grooming, score_clima,
    get_aliases_for_breed
)

# ===== JSON-LD helpers (só as páginas usam) =====
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
          {"@type":"ListItem","position":2,"name":"Raças","item":f"{BASE}/racas/"},
        ]
    }, ensure_ascii=False)

def jsonld_breadcrumb_compare():
  url = f"{BASE}/comparar/"
  return json.dumps({
    "@context":"https://schema.org","@type":"BreadcrumbList",
    "itemListElement":[
      {"@type":"ListItem","position":1,"name":"Início","item":f"{BASE}/"},
      {"@type":"ListItem","position":2,"name":"Comparar","item":url},
    ]
  }, ensure_ascii=False)

def jsonld_breed(d, url):
    alt_macho = d["medidas"]["altura_cm"].get("macho", "—")
    alt_fem   = d["medidas"]["altura_cm"].get("femea", "—")
    peso_m    = d["medidas"]["peso_kg"].get("macho", "—")
    peso_f    = d["medidas"]["peso_kg"].get("femea", "—")
    vida_txt  = d["medidas"].get("expectativa_anos", "—")

    def _pm(txt):
        from build_lib import parse_minmax
        a,b = parse_minmax(txt);
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

# ===== Carregamentos =====
site, rules, racas = load_all()
BASE = site.get("base_url", "https://www.guiaracas.com.br")

tpl = Template((ROOT/"templates/detalhe-raca.html").read_text(encoding="utf-8"))
head_base   = Template((ROOT/"templates/head-base.html").read_text(encoding="utf-8")).safe_substitute(baseUrl=BASE)
header_tpl  = Template((ROOT/"templates/header.html").read_text(encoding="utf-8"))
footer_tpl  = Template((ROOT/"templates/footer.html").read_text(encoding="utf-8"))
site_header = header_tpl.safe_substitute(baseUrl=BASE)
site_footer = footer_tpl.safe_substitute(baseUrl=BASE)


tpl_list = Template((ROOT/"templates/lista-racas.html").read_text(encoding="utf-8"))
out_dir = ROOT/"racas"; out_dir.mkdir(exist_ok=True)
tpl_compare = Template((ROOT/"templates/comparar.html").read_text(encoding="utf-8"))


aliases_map = load_aliases_map()

# ===== Cartão da listagem =====
def render_card(r):
    slug = r.get("slug") or slugify(r["nome"])
    grupo = r["atributos"].get("fci_grupo")
    fci_grupo_txt = f"Grupo {grupo}" if grupo else "—"
    fci_desc = rules["fci_grupos"].get(str(grupo), "—")

    porte = (r["atributos"].get("porte") or "").lower()
    porte_label = human_porte(porte)

    foto_src = r.get("foto","") or "/assets/breeds/_placeholder.png"
    if foto_src.startswith("/"): foto_src = f"{BASE}{foto_src}"

    aliases = get_aliases_for_breed(r, aliases_map)
    alias_attr = " | ".join(a for a in aliases if a)

    title_html = attr(r["nome"])
    fci_desc_html = attr(fci_desc)

    return (
      f"<li class='breed-card' "
      f" data-name='{attr(r['nome'].lower())}'"
      f" data-porte='{attr(porte)}'"
      f" data-grupo='{attr(str(grupo or ''))}'"
      f" data-alias='{attr(alias_attr)}'>"
      f"  <article class='breed-card__inner'>"
      f"    <figure class='breed-card__thumb'>"
      f"      <img src='{foto_src}' alt='' width='120' height='80' loading='lazy' decoding='async' />"
      f"    </figure>"
      f"    <div class='breed-card__body'>"
      f"      <h3 class='breed-card__title'><a href='{BASE}/racas/{slug}.html'>{title_html}</a></h3>"
      f"      <p class='breed-card__meta'><span class='badge'>{fci_grupo_txt}</span> {fci_desc_html}"
      f"      <span class='dot'>•</span> Porte: {porte_label}</p>"
      f"    </div>"
      f"  </article>"
      f"</li>"
    )

# ===== Páginas de raça =====
for r in racas:
    slug = slugify(r["nome"])
    url  = f"{BASE}/racas/{slug}.html"

    lead = r.get("lead") or r.get("notas", {}).get("resumo", "")
    alt = r["medidas"]["altura_cm"]
    altura_texto_html = (
      f"{alt.get('macho','—')} <span class='sex sex--m' aria-label='macho' title='macho'>♂</span> / "
      f"{alt.get('femea','—')} <span class='sex sex--f' aria-label='fêmea' title='fêmea'>♀</span> cm"
    )
    pes = r["medidas"]["peso_kg"]
    peso_texto_html = (
      f"{pes.get('macho','—')} <span class='sex sex--m' aria-label='macho' title='macho'>♂</span> / "
      f"{pes.get('femea','—')} <span class='sex sex--f' aria-label='fêmea' title='fêmea'>♀</span> kg"
    )
    vida_texto = f"{r['medidas'].get('expectativa_anos','—')} anos"

    atividade_val, detA_txt, _factsA = score_atividade(r, rules)
    grooming_val,  detG_txt, _factsG = score_grooming(r, rules)
    clima_val,     detC_txt, _factsC = score_clima(r, rules, atividade_val)

    grupo = r["atributos"].get("fci_grupo")
    fci_grupo_txt = f"Grupo {grupo}" if grupo else "—"
    fci_desc = rules["fci_grupos"].get(str(grupo), "—")
    porte_slug = (r["atributos"].get("porte") or "").lower()
    porte_label = human_porte(porte_slug)

    foto_src = r.get("foto","") or "/assets/breeds/_placeholder.png"
    if foto_src.startswith("/"): foto_src = f"{BASE}{foto_src}"

    # AKA
    aliases = get_aliases_for_breed(r, aliases_map)
    AKA_BLOCK = (f"<p class='breed__aka'><span class='aka__label'>Também conhecido como:</span> {attr(join_pt(aliases))}</p>") if aliases else ""

    page_html = tpl.safe_substitute(
      HEAD_BASE=head_base, baseUrl=BASE, url=url, slug=slug,
      SITE_HEADER=site_header, SITE_FOOTER=site_footer,
      nome=r["nome"], lead=lead,
      origem=r.get("origem","—"),
      fci_grupo=fci_grupo_txt, fci_descricao=fci_desc,
      fci_codigo=r.get("fci_codigo","—"),
      porte_label=porte_label, porte_slug=porte_slug,
      altura_texto_html=altura_texto_html, peso_texto_html=peso_texto_html, vida_texto=vida_texto,
      atividade=atividade_val, grooming=grooming_val, clima=clima_val,
      detalhe_atividade_html=detA_txt, detalhe_grooming_html=detG_txt, detalhe_clima_html=detC_txt,
      perfil_label="Seu perfil/função típica é", funcao_txt="", ativ_txt_trailer="",
      foto=foto_src, foto_w=r.get("foto_w",""), foto_h=r.get("foto_h",""),
      foto_credito=r.get("foto_credito",""),
      AKA_BLOCK=AKA_BLOCK,
      jsonld_breadcrumb=jsonld_breadcrumb(r["nome"], url, BASE),
      jsonld_breed=jsonld_breed(r, url),
    )
    (out_dir/f"{slug}.html").write_text(page_html, encoding="utf-8")

# ===== Página /racas/index.html =====
options = []
for k in sorted(rules["fci_grupos"].keys(), key=lambda x: int(x)):
    label = rules["fci_grupos"][k]
    options.append(f"<option value='{k}'>Grupo {k} — {attr(label)}</option>")
options_grupo_html = "\n".join(options)

cards_html = "\n".join(render_card(r) for r in sorted(racas, key=lambda x: x["nome"]))
datalist = "\n".join(f"<option value=\"{attr(r['nome'])}\">" for r in sorted(racas, key=lambda x: x["nome"]))

html_list = tpl_list.safe_substitute(
  HEAD_BASE=head_base, baseUrl=BASE,
  SITE_HEADER=site_header, SITE_FOOTER=site_footer,
  OPTIONS_GRUPO=options_grupo_html,
  LISTA_RACAS_ITEMS=cards_html,
  DATALIST_BREEDS=datalist,
  jsonld_breadcrumb_list=jsonld_breadcrumb_list(BASE)
)
(out_dir/"index.html").write_text(html_list, encoding="utf-8")

# ===== Página /comparar/index.html =====
cmp_out_dir = ROOT / "comparar"
cmp_out_dir.mkdir(exist_ok=True)

datalist = "\n".join(f'<option value="{r["nome"]}">' for r in sorted(racas, key=lambda x: x["nome"]))

html_cmp = tpl_compare.safe_substitute(
    HEAD_BASE=head_base, baseUrl=BASE,
    SITE_HEADER=site_header, SITE_FOOTER=site_footer,
    DATALIST_BREEDS=datalist,
    jsonld_breadcrumb_compare=jsonld_breadcrumb_compare()
)

(cmp_out_dir/"index.html").write_text(html_cmp, encoding="utf-8")
