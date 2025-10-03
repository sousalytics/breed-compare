# tools/audita_css.py
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSS_GLOBS = ["styles/*.css"]
HTML_GLOBS = [
  "index.html",
  "templates/**/*.html",
  "racas/**/*.html",
  "comparar/**/*.html",
  "guia-responsavel/**/*.html",
  "sobre/**/*.html",
]
JS_GLOBS = ["scripts/**/*.js"]

# ---- Config (ajuste aqui se mudar convenções) ----
SAFELIST = {
  # utilitários/core
  "visually-hidden","sr-only-focusable","skip-link","js",
  # header/nav
  "header","header__inner","logo","nav","nav__list","footer","footer__inner",
  # comparador (injetadas por JS)
  "chip","card","cmp-card","cmp-card__title","cmp-grid","cmp-cell","cmp-cell--label",
  "cmp-colhead","cmp-colhead__box","cmp-colhead__txt","cmp-thumb","cmp-add-col","cmp-add-input","cmp-spacer", "compare-main", "page-compare"
}
SAFE_PREFIXES = ("is-","js-","cmp-")  # estados, hooks e família do comparador

# Sugerir rename (HTML ↔ CSS)
RENAME_SUGGESTIONS = {
  "breed-card__meta": "breed-card__body",
  "site-footer": "footer",
  "site-header": "header",
}

def glob(paths):
    out = []
    for pat in paths:
        out.extend(ROOT.glob(pat))
    return [p for p in out if p.exists()]

def load_files(paths) -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in paths)

def _norm(c: str) -> str:
    """Normaliza nome de classe: remove ponto, pseudo, separadores."""
    c = (c or "").strip()
    if c.startswith("."):
        c = c[1:]
    c = re.split(r"[:\s,>+~]", c)[0]
    return c

def extract_css_classes(text: str) -> set[str]:
    """Extrai classes definidas no CSS (sem pseudo)."""
    raw = re.findall(r"\.[a-zA-Z0-9_-]+", text)
    cleaned = []
    for t in raw:
        name = t[1:]
        if not name or name[0].isdigit():
            continue
        if re.match(r"^\d*(rem|em|vw|vh|ms|s|px)$", name):
            continue
        name = re.split(r"[:\s]", name)[0]
        cleaned.append(_norm(name))
    return set(cleaned)

def extract_used_from_html(text: str) -> set[str]:
    """Extrai classes usadas do HTML estático (class="a b")."""
    used = set()
    for m in re.findall(r'class=(["\'])(.*?)\1', text, flags=re.S):
        for cls in re.split(r"\s+", m[1].strip()):
            if cls:
                used.add(_norm(cls))
    return used

def extract_used_from_js(text: str) -> set[str]:
    """Extrai classes usadas em JS (classList.add, className, class='...', templates com crase)."""
    used = set()

    # 1) classList.add('a','b', "c")
    for args in re.findall(r'classList\.add\((.*?)\)', text, flags=re.S):
        for token in re.findall(r'["\']([a-zA-Z0-9_-]+)["\']', args):
            used.add(_norm(token))

    # 2) Template strings: class=`a b` (com crase)
    for content in re.findall(r'class\s*=\s*`([^`]+)`', text, flags=re.S):
        for token in re.findall(r'[a-zA-Z0-9_-]+', content):
            used.add(_norm(token))

    return used

def is_safelisted(cls: str) -> bool:
    return cls in SAFELIST or any(cls.startswith(pref) for pref in SAFE_PREFIXES)

def main():
    css_files  = glob(CSS_GLOBS)
    html_files = glob(HTML_GLOBS)
    js_files   = glob(JS_GLOBS)

    if not css_files:
        print("Nenhum CSS encontrado.")
        sys.exit(1)
    if not html_files:
        print("Nenhum HTML encontrado.")
        sys.exit(1)

    css_text  = load_files(css_files)
    html_text = load_files(html_files)
    js_text   = load_files(js_files)

    # Conjuntos normalizados
    declared = extract_css_classes(css_text)
    used = extract_used_from_html(html_text) | extract_used_from_js(js_text)

    # Classificação
    keep    = sorted([c for c in declared if (c in used) or is_safelisted(c)])
    remove  = sorted([c for c in declared if (c not in used) and not is_safelisted(c)])
    missing = sorted([u for u in used     if (u not in declared) and not is_safelisted(u)])

    # Renames sugeridos
    renames = []
    for src, dst in RENAME_SUGGESTIONS.items():
        if src in declared and (dst in used or dst in declared):
            renames.append((src, dst))

    outdir = ROOT / "styles" / "dist"
    outdir.mkdir(parents=True, exist_ok=True)
    report = outdir / "audit-css-HTML+JS.txt"

    with report.open("w", encoding="utf-8") as f:
        f.write("=== AUDITORIA DE CSS (HTML + JS) ===\n\n")
        f.write(f"Declaradas: {len(declared)} • Usadas: {len(used)} • KEEP: {len(keep)} • REMOVE: {len(remove)} • MISSING: {len(missing)}\n\n")
        if renames:
            f.write("---- RENAME SUGERIDO ----\n")
            for s,d in renames:
                f.write(f"{s}  →  {d}\n")
            f.write("\n")
        f.write("---- REMOVE (candidatas) ----\n")
        for c in remove:
            f.write(c + "\n")
        f.write("\n---- MISSING (HTML/JS usa e não tem no CSS) ----\n")
        for m in missing:
            f.write(m + "\n")
        f.write("\n---- KEEP (usadas/safelisted) ----\n")
        for k in keep:
            f.write(k + "\n")

    print(f"✔ Relatório: {report}")

if __name__ == "__main__":
    main()
