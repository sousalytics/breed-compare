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

# Classes que você sabe que devem ficar mesmo se não aparecem no HTML estático
SAFELIST = {
  "visually-hidden", "sr-only-focusable", "skip-link",
  "btn", "btn--primary", "btn--compare",
  "input", "is-error", "is-success",
  "header", "footer",
  "nav__list", "nav__item", "nav__link",
  "table--sticky", "table--num", "thead--hidden-cols", "col-breed",
}
SAFE_PREFIXES = ("is-",)  # exemplo: is-active, is-open…

def glob(paths):
  out = []
  for pat in paths:
      out.extend(ROOT.glob(pat))
  return [p for p in out if p.exists()]

def extract_css_classes(text: str) -> set[str]:
  raw = re.findall(r"\.[a-zA-Z0-9_-]+", text)
  cleaned = []
  for t in raw:
      name = t[1:]
      # ignora tokens que claramente vieram de valores decimais / unidades
      if name[0].isdigit():
          continue
      if re.match(r"^\d*(rem|em|vw|vh|ms|s|px)$", name):
          continue
      # remove pseudo e etc (.classe:hover, .classe::after)
      name = re.split(r"[:\s]", name)[0]
      cleaned.append(name)
  return set(cleaned)


def extract_used_classes_from_html(text: str) -> set[str]:
  used = set()
  # class="a b c" / class='a b c'
  for m in re.findall(r'class=(["\'])(.*?)\1', text, flags=re.S):
      for cls in re.split(r"\s+", m[1].strip()):
          if cls:
              used.add(cls)
  return used

def load_files(paths) -> str:
  return "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in paths)

def is_safelisted(cls: str) -> bool:
  return cls in SAFELIST or any(cls.startswith(pref) for pref in SAFE_PREFIXES)

def main():
  css_files = glob(CSS_GLOBS)
  html_files = glob(HTML_GLOBS)

  if not css_files:
      print("Nenhum CSS encontrado.")
      sys.exit(1)
  if not html_files:
      print("Nenhum HTML encontrado (gere as páginas antes).")
      sys.exit(1)

  css_text = load_files(css_files)
  html_text = load_files(html_files)

  declared = extract_css_classes(css_text)
  used = extract_used_classes_from_html(html_text)

  # classes que estão no CSS mas não aparecem no HTML estático (ignorando safelist)
  unused = sorted([c for c in declared if c not in used and not is_safelisted(c)])
  # classes usadas no HTML mas que não têm declaração no CSS (prováveis typos)
  missing = sorted([u for u in used if u not in declared and not is_safelisted(u)])

  outdir = ROOT / "styles" / "dist"
  outdir.mkdir(parents=True, exist_ok=True)
  report = outdir / "audit-unused-css.txt"

  with report.open("w", encoding="utf-8") as f:
      f.write("=== AUDITORIA DE CSS ===\n\n")
      f.write(f"CSS analisados: {', '.join(str(p.relative_to(ROOT)) for p in css_files)}\n")
      f.write(f"HTML analisados: {len(html_files)} arquivos\n\n")
      f.write(f"Classes declaradas: {len(declared)}\n")
      f.write(f"Classes usadas: {len(used)}\n")
      f.write(f"Não usadas (candidatas a remoção): {len(unused)}\n")
      f.write(f"Usadas mas não declaradas (verifique typos): {len(missing)}\n\n")

      f.write("---- NÃO USADAS ----\n")
      for c in unused:
          f.write(c + "\n")
      f.write("\n---- USADAS MAS NÃO DECLARADAS ----\n")
      for m in missing:
          f.write(m + "\n")

  print(f"✔ Relatório gerado: {report}")

if __name__ == "__main__":
  main()
