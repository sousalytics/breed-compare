# Gera templates padronizados (head-base, header, footer)
# A partir de data/site.json

from pathlib import Path
from html import escape as _e
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "site.json"
TPL_DIR = ROOT / "templates"
TPL_DIR.mkdir(parents=True, exist_ok=True)

def load_site():
    site = {}
    if DATA.exists():
        site = json.loads(DATA.read_text(encoding="utf-8"))
    # defaults
    site.setdefault("name", "Guia Raças")
    site.setdefault("base_url", "")
    site.setdefault("noindex", True)
    site.setdefault("nav", [
        {"label": "Raças", "href": "/racas/"},
        {"label": "Comparar", "href": "/comparar/"},
        {"label": "Sobre", "href": "/sobre/"},
        {"label": "Guia Responsável", "href": "/guia-responsavel/"}
    ])
    site.setdefault("footer_links", [
        {"label": "Mapa do site", "href": "/sitemap.html"},
        {"label": "Acessibilidade", "href": "/acessibilidade/"},
        {"label": "Privacidade", "href": "/privacidade/"}
    ])
    return site

def absolutize(base, href):
    href = href or "#"
    if href.startswith("http"):
        return href
    base = base.rstrip("/")
    if href.startswith("/"):
        return f"{base}{href}" or "/"
    return f"{base}/{href}".replace("//", "/") or "/"

def render_head_base(site):
    base = site["base_url"].rstrip("/")
    theme = "#127a72"  # teal brand-700
    robots = "noindex, nofollow" if site.get("noindex") else "index, follow"
    return f"""<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="{theme}" />
<meta name="robots" content="{robots}" />

<script>document.documentElement.classList.add("js");</script>

<link rel="icon" href="{absolutize(base, '/public/favicon.svg')}" />
<link rel="apple-touch-icon" href="{absolutize(base, '/public/apple-touch-180.png')}" />

<link rel="stylesheet" href="{absolutize(base, '/styles/tokens.css')}" />
<link rel="stylesheet" href="{absolutize(base, '/styles/base.css')}" />
<link rel="stylesheet" href="{absolutize(base, '/styles/ui.css')}" />

<link rel="preload" as="image" href="{absolutize(base, '/assets/icons/sprite.svg')}" />
""".rstrip() + "\n"

def render_header(site):
    base = site["base_url"].rstrip("/")
    name = _e(site["name"])
    items = []
    for it in site["nav"]:
        items.append(f'<li><a class="nav__link" href="{absolutize(base, it.get("href") or "#")}">{_e(it.get("label") or "")}</a></li>')
    return f"""<a class="visually-hidden" href="#conteudo">Pular para o conteúdo</a>
<header class="header" role="banner">
  <div class="header__inner container">
    <a href="{absolutize(base, '/')}" class="logo" aria-label="{name} — Página inicial">{name}</a>
    <nav class="nav" aria-label="Principal">
      <ul class="nav__list">
        {' '.join(items)}
      </ul>
    </nav>
  </div>
</header>
"""

def render_footer(site):
    base = site["base_url"].rstrip("/")
    year = datetime.now().year
    links = []
    for it in site["footer_links"]:
        links.append(f'<a class="footer__link" href="{absolutize(base, it.get("href") or "#")}">{_e(it.get("label") or "")}</a>')
    name = _e(site["name"])
    return f"""<footer class="footer site-footer" role="contentinfo">
  <nav class="footer__nav" aria-label="Links institucionais">
    {' '.join(links)}
  </nav>
  <p>&copy; {year} {name} — Conteúdo educativo. Consulte um veterinário para decisões de saúde.</p>
</footer>
"""

def main():
    site = load_site()
    (TPL_DIR / "head-base.html").write_text(render_head_base(site), encoding="utf-8")
    (TPL_DIR / "header.html").write_text(render_header(site), encoding="utf-8")
    (TPL_DIR / "footer.html").write_text(render_footer(site), encoding="utf-8")
    print("[ok] templates/head-base.html, header.html, footer.html atualizados")

if __name__ == "__main__":
    main()
