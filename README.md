[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-blue.svg)](./LICENSE-CONTENT)

# 🐶 Guia Raças — Site de Informações sobre Cães

> Disponível também em [English](./README.en.md) _(em breve)_.

**Status**

- ✅ Sprint 1 — Diretrizes Visuais (paleta, tipos, ícones)
- ✅ Sprint 2 — IA & Navegação (mapa do site, rótulos, headings, breadcrumbs)
- ⏭️ Sprint 3 — HTML semântico (esqueleto, metodologias e conteúdo base)

**Autor**

@sousalytics

**Objetivo**

Construir um site acessível, rápido e didático para obter informações de raças de cães, sem incentivar eugenia e com foco em adoção responsável.

---

## ✨ Visão Geral

- Informações por características (medidas, atividade física, higiene/pelagem, clima/ambiente) + metodologia aberta.
- HTML semântico + CSS moderno + JavaScript vanilla (progressive enhancement).
- Acessibilidade: **WCAG 2.2** e **WAI-ARIA APG**.
- Qualidade: **RAIL**, **Core Web Vitals** e **Lighthouse**.
- SEO técnico: **Google Search Central**.
- Segurança: **CSP** e boas práticas **OWASP**.

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

<details>
<summary>Ver árvore</summary>
<pre><code>
breed-compare/
├─ assets/
│  ├─ brand/
│  │  ├─ og-1200x630.png
│  │  └─ avatar-512.png
|  ├─ icons/
│  |   └─ sprite.svg
│  ├─ logos/
│  │  ├─ paw-solid.svg
│  │  └─ paw-stroke.svg
├─ comparar/
|  └─ index.html
├─ data/
|  ├─ racas.json
|  ├─ rules.json
|  └─ site.json
├─ docs/
│  └─ brand-notes.md
├─ guia-responsavel/
│  └─ index.html
├─ public/
│  ├─ apple-touch-180.png
│  ├─ favicon-16.png
│  ├─ favicon-32.png
│  ├─ favicon.svg
│  └─ robots.txt
├─ racas/
|  └─ index.html
├─ scripts/
|  ├─ gerar_paginas.py
|  └─ main.js
├─ sobre/
|  └─ index.html
├─ styles/
│  ├─ base.css
│  ├─ tokens.css
│  └─ ui.css
├─ templates/
│  ├─ detalhe-raca.html
|  └─ head-base.html
├─ 404.html
├─ index.html
└─ sitemap.html
</code></pre>
</details>

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
