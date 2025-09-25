# Guia Raças — Brand Notes

> Guia de marca para designers e contribuidores de conteúdo visual.

**Para quem?** Artistas/Designers que criam logo, ícones e imagens.
**Para quê?** Centralizar decisões visuais (cores, tipografia, glifo, ícones, assets) com exemplos, tamanhos e arquivos-fonte.
**Quando usar?** Ao criar/atualizar qualquer asset (favicon, OG image, ilustrações etc.).

**Relacionamento com README:** o README traz um resumo; **este arquivo é a referência detalhada**.

## Conteúdo

- Paleta completa (com HEX), pares de contraste e exemplos.
- Logo & glifo (regras de uso; sólida vs contornada; inclinação; respiro).
- Sprite de ícones (IDs, tamanhos, stroke/estilo).
- Assets do site (favicon, apple-touch, OG, avatar): tamanhos e mock.
- Anexos/links: arquivos-fonte, direitos/atribuições se houver.

---

## Paleta

- **Primary:** `#0033A0`
  - **-primary-contrast:** `#FFFFFF`
- **Accent (CTA):** `#B45309`
  - **-accent-contraste:** `#FFFFFF`
- **Neutros:** definidos nos tokens (`--color-bg`, `--color-surface`, `--color-text`, `--color-muted`).

## Tipografia

- **Títulos:** Poppins 700 (token `--font-title`)
- **Corpo:** Inter 400/600 (token `--font-body`)
- **Escala:** `--step-*` (tokens), `line-height` confortável.

## Logo & Glifo

- **Wordmark:** “Guia Raças” (Poppins 700).
- **Glifo (patinha):** duas versões:
  - **Sólida**: para tamanhos pequenos (favicon, apple-touch, avatar).
  - **Contornada** (`currentColor`, traço arredondado): para UI e ícones no site.
- **Inclinação:** +10° (esquerda).

## Ícones (sprite)

- Arquivo: `assets/icons/sprite.svg`
- Padrão: **stroke-only**, `stroke-width: 2`, _round caps/joins_.
- Cores por contexto: `currentColor` + utilitários `.icon--muted/.--positive/.--danger`.
- Tamanhos: `.icon--sm` (16px), `.icon--md` (20px), `.icon--lg` (24px).

## Assets (arquivos visuais)

- **Favicon:** `public/favicon.svg` (+ PNGs 32/16, opcional)
- **Apple Touch:** `public/apple-touch-180.png` (180×180, fundo sólido)
- **OG Image:** `assets/brand/og-1200x630.png` (1200×630)
- **Avatar:** `assets/brand/avatar-512.png` (512×512)

## Acessibilidade

- Ícones **decorativos**: `aria-hidden="true"`.
- Ícones **informativos**: `role="img"` + `<title>`/`aria-labelledby`.
- Contraste mínimo: **4.5:1** para textos/ícones.

## DoD (Sprint 1)

- Tokens e pares de contraste definidos.
- Styleguide com exemplos (cores, tipos, botões, inputs, tabela, ícones, logo provisória).
- CSP mínima e sem inline crítico nas áreas de produção.
- README e brand-notes atualizados.
