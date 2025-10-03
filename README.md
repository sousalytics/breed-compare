[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-blue.svg)](./LICENSE-CONTENT)

# 🐶 Guia Raças — Site Acessível e Rápido Sobre Cães

> Disponível também em [English](./README.en.md) _(em breve)_.

**Status**

- ✅ Sprint 1 — Diretrizes Visuais (paleta, tipos, ícones)
- ✅ Sprint 2 — IA & Navegação (mapa do site, rótulos, headings, breadcrumbs)
- ✅ Sprint 3 — HTML semântico (esqueleto, metodologias e conteúdo base)
- ⏭️ Sprint 4 — Insghts & blog (análises, páginas de conteúdo)

**Objetivo**

Construir um site acessível, rápido e didático para obter informações de raças de cães, sem incentivar eugenia e com foco em adoção responsável.

---

## ✨ O que o site oferece

- **Página da raça** com medidas, grupo FCI, origem, pelagem e textos explicativos.
- **Comparador de raças** (até 3 colunas) com:
  - chips para remover raças;
  - drag & drop para reordenar colunas;
  - setas e teclado (←/→, Delete/Backspace);
  - seleção persistente (URL compartilhável + LocalStorage);
  - HTML semântico e atributos ARIA (tabela "like" acessível);
- **Metodologia aberta** (regras e pesos) e **JSON-LD** para **SEO**.
- **Front-end leve**: HTML + CSS moderno + JavaScript vanilla (progressive enhancement).
- **Acessibilidade**: WCAG 2.2 + WAI-ARIA APG.
- **Qualidade**: RAIL + Core Web Vitals + Lighthouse.
- **SEO**: Google Search Central.
- **Segurança**: CSP + OWASP.

## 🧱 Stack & Padrões

- **Front-end:** HTML(WHATWG) + CSS(W3C) + JS(ES2023+).
- **CSS:** BEM/SMACSS + tokens via CSS Custom Properties.
- **Gerador estático**: Scripts Python que leem JSON e geram páginas.
- **Formatação:** EditorConfig + Prettier.

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
│  │  ├─ avatar-512.png
│  │  └─ og-1200x630.png
|  ├─ breeds/_placeholder.png
|  ├─ icons/sprite.svg
|  ├─ js/details-toggle.js
│  ├─ logos/
│  │  ├─ paw-solid.svg
│  │  └─ paw-stroke.svg
├─ comparar/index.html            # página do comparador (gerado) 
├─ data/
|  ├─ aliases_oficiais.json       # dados de aliases das raças
|  ├─ breeds-client.json          # dados para o comparador (gerado)
|  ├─ racas.json                  # dados canônicos das raças
|  ├─ rules.json                  # regras da metodologia
|  └─ site.json                   # config do site
├─ docs/brand-notes.md            
├─ guia-responsavel/index.html    
├─ public/
│  ├─ apple-touch-180.png
│  ├─ favicon-16.png
│  ├─ favicon-32.png
│  ├─ favicon.svg
│  └─ robots.txt
├─ racas/
|  ├─ index.html                 # lista de raças (gerado)
|  └─ <slug>.html                # página da raça (gerado)
├─ scripts/
|  ├─ build_lib.py               # carrega as funções para os scripts py
|  ├─ compare.js                 # lógica do comparador
|  ├─ gerar_breeds_cliente.py    # gera data/breeds-client.json
|  ├─ gerar_paginas.py           # gera páginas HTML estáticas
|  └─ main.js                    # melhorias gerais
├─ sobre/index.html
├─ styles/
│  ├─ base.css
│  ├─ tokens.css
│  └─ ui.css
├─ templates/
|  ├─ comparar.html
|  ├─ detalhe-raca.html
|  ├─ footer.html
|  ├─ head-base.html
│  ├─ header.html
|  └─ lista-racas.html
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
2. Gerar o dataset para o comparador:
   ```bash
   python scripts/gerar_breeds_cliente.py
   # Escreve data/breeds-client.json
   ```
3. Gerar as páginas HTML (raças, lista e comparar):
   ```bash
   python scripts/gerar_paginas.py
   # Escreve racas/*.html, racas/index.html e comparar/index.html
   ```
4. Abrir `index.html` → _Open with Live Server_
5. Alternativa:
   ```bash
   python -m http.server 5500
   # Acesse http://localhost:5500
   ```

## 🤝 Contribuindo

- Issues e PRs são bem-vindos.
- Siga Conventional Commits.
- Mantenha o HTML semântico, o CSS modular e o JS progressivo.

## 📬 Autor

@sousalytics

> Dúvidas ou sugestões? Abra uma issue!
