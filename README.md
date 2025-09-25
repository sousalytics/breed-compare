[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-blue.svg)](./LICENSE-CONTENT)

# 🐶 Guia Raças — Site de Informações sobre Cães

> Disponível também em [English](./README.en.md) _(em breve)_.

**Status:** ✅ Sprint 1 (Diretrizes Visuais) **finalizado**  
**Autor:** @sousalytics  
**Objetivo:** Construir um site acessível, rápido e didático para obter informações de raças de cães.

---

## ✨ Visão Geral

- Informações de raças por características (tamanho, energia, treinabilidade, grooming etc.).
- HTML semântico + CSS moderno + JavaScript vanilla com **progressive enhancement**.
- Acessibilidade: **WCAG 2.2** e WAI-ARIA APG.
- Qualidade: **RAIL**, **Core Web Vitals** e **Lighthouse**.
- SEO técnico: **Google Search Central**.
- Segurança: **CSP** inicial e boas práticas (OWASP).

## 🧱 Stack & Padrões

- **Front-end:** HTML (WHATWG), CSS (W3C), JS (ECMAScript).
- **Organização CSS:** BEM/SMACSS; tokens via CSS Custom Properties.
- **Formatação:** EditorConfig + Prettier.
- **Commits:** Conventional Commits.
- **Branches:** `main` (+ `feature/<nome>` quando útil).

## 🎨 Diretrizes Visuais

- **Paleta (v1):**
  - `--color-primary: #0033a0` / `--color-primary-contrast: #ffffff`
  - `--color-accent:  #b45309` / `--color-accent-contrast: #ffffff`
- **Tipografia:** Poppins (títulos), Inter (corpo).
- **Ícones:** sprite SVG externo (`assets/icons/sprite.svg`), `currentColor`, tamanhos `.icon--sm/md/lg`.
- **Logo provisória:** wordmark “Canis” + glifo (patinha).
- **Styleguide:** `./styleguide.html` (cores, tipos, botões, inputs, tabela, ícones).

➡️ Detalhes completos (cores, logo, ícones, assets): veja **[docs/brand-notes.md](./docs/brand-notes.md)**.

## 📁 Estrutura

breed-compare/
├─ assets/
│ ├─ icons/ # sprite.svg
│ ├─ logos/ # paw-solid.svg, paw-stroke.svg
│ └─ brand/ # og-1200x630.png, avatar-512.png
├─ public/ # favicon.svg, favicon-16.png, favicon-32.png, apple-touch-180.png, robots.txt
├─ styles/ # tokens.css, base.css, ui.css
├─ docs/ # brand-notes.md
├─ index.html
└─ styleguide.html

## 📝 Licenças

- **Código:** MIT — veja [LICENSE](./LICENSE).
- **Conteúdo autoral:** CC BY 4.0 — veja [LICENSE-CONTENT](./LICENSE-CONTENT).
  > Itens de terceiros podem ter licenças distintas. Consulte `ATTRIBUTIONS.md`.

## 🚀 Rodando localmente

1. VS Code + **Live Server**
2. Abrir `index.html` → _Open with Live Server_
3. Alternativa:
   ```bash
   python -m http.server 5500
   # Acesse http://localhost:5500
   ```
