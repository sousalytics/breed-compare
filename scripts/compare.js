(function () {
  const root = document.querySelector(".page-compare");
  if (!root) return;

  const MAX_COLS = 3;
  const STORAGE_KEY = "compare:selected";

  const simplify = (s) =>
    (s || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();

  const slugify = (s) =>
    simplify(s)
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");

  const main = root.querySelector(".compare-main");
  const headgrid = root.querySelector(".cmp-headgrid");
  const chips = root.querySelector(".selected-chips");
  const datalist = root.querySelector("#breeds-datalist");

  function mkSection(title) {
    const sec = document.createElement("section");
    sec.className = "cmp-card card";
    sec.innerHTML = `<h2 class="cmp-card__title">${title}</h2><div class="cmp-grid"></div>`;
    return sec;
  }
  const sections = {
    g1: mkSection("Classificação & Origem"),
    g2: mkSection("Medidas"),
    g31: mkSection("Energia Física & Mental"),
    g32: mkSection("Cuidados & Pelagem"),
    g33: mkSection("Clima & Espaço"),
  };
  Object.values(sections).forEach((s) => main.appendChild(s));

  let data = [];
  let selected = [];
  let dragIndex = -1;

  function loadSel() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch {
      return [];
    }
  }
  function saveSel() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(selected.slice(0, MAX_COLS)));
  }

  function readURLAndMerge() {
    const p = new URLSearchParams(location.search);
    const adds = p.getAll("add");
    const base = loadSel();
    selected = [...new Set([...base, ...adds])].slice(0, MAX_COLS);
    saveSel();
    history.replaceState(null, "", location.pathname);
  }

  function colTemplate(nCols) {
    return `minmax(180px, 1fr)${" minmax(200px, 1fr)".repeat(nCols)}`;
  }
  function spacer() {
    const d = document.createElement("div");
    d.className = "cmp-spacer";
    d.setAttribute("aria-hidden", "true");
    return d;
  }
  function hThumb(img, alt = "") {
    if (!img) return "";
    const altText = alt || "Foto da raça";
    return `<img src="${img}" alt="${altText}" loading="lazy" decoding="async" width="96" height="64" class="cmp-thumb">`;
  }
  function cell(text, isLabel = false) {
    const d = document.createElement("div");
    d.className = "cmp-cell" + (isLabel ? " cmp-cell--label" : "");
    d.innerHTML = text;
    return d;
  }
  function move(arr, from, to) {
    if (from === to || from < 0 || to < 0 || from >= arr.length || to >= arr.length) return arr;
    const copy = arr.slice();
    const [it] = copy.splice(from, 1);
    copy.splice(to, 0, it);
    return copy;
  }

  function renderChips() {
    chips.innerHTML = "";
    selected.forEach((slug) => {
      const b = data.find((d) => d.slug === slug);
      if (!b) return;
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.setAttribute("aria-label", `Remover ${b.nome}`);
      chip.innerHTML = `${b.nome} <span aria-hidden="true">×</span>`;
      chip.addEventListener("click", () => {
        selected = selected.filter((s) => s !== slug);
        saveSel();
        renderAll();
      });
      chips.appendChild(chip);
    });
  }

  function renderHeadgrid(breeds) {
    headgrid.innerHTML = "";
    headgrid.style.display = "grid";
    headgrid.style.gridTemplateColumns = colTemplate(MAX_COLS);

    // célula invisível para a coluna de rótulos
    headgrid.appendChild(spacer());

    // acessibilidade
    headgrid.setAttribute("role", "table");
    headgrid.setAttribute("aria-colcount", String(1 + breeds.length));

    for (let i = 0; i < MAX_COLS; i++) {
      const b = breeds[i];
      if (b) {
        const d = document.createElement("div");
        d.className = "cmp-colhead";
        d.setAttribute("role", "columnheader");
        d.id = `col-${i + 1}`;

        d.innerHTML = `
        <button type="button" class="cmp-colhead__remove" aria-label="Remover ${b.nome}">×</button>
        ${hThumb(b.foto, `Foto da raça ${b.nome}`)}
        <div class="cmp-colhead__txt"><strong>${b.nome}</strong></div>
        <div class="cmp-colhead__actions" role="group" aria-label="Reordenar coluna">
          <button type="button" class="btn btn--sm" aria-label="Mover para a esquerda">←</button>
          <button type="button" class="btn btn--sm" aria-label="Mover para a direita">→</button>
        </div>
      `;

        d.setAttribute("draggable", "true");

        d.addEventListener("dragstart", (e) => {
          dragIndex = i;
          d.classList.add("is-dragging");

          const dt = e.dataTransfer;
          if (dt) {
            dt.setData("text/plain", String(i));
            try {
              dt.setDragImage(d, 10, 10);
            } catch {}
            dt.effectAllowed = "move";
          }
        });

        d.addEventListener("dragend", () => {
          dragIndex = -1;
          d.classList.remove("is-dragging");
        });

        d.addEventListener("dragover", (e) => {
          e.preventDefault(); // permite drop
        });

        d.addEventListener("drop", (e) => {
          e.preventDefault();
          if (dragIndex === -1 || dragIndex === i) return;
          selected = move(selected, dragIndex, i);
          saveSel();
          renderAll();
        });

        // eventos: remover/mover
        d.querySelector(".cmp-colhead__remove").addEventListener("click", () => {
          selected.splice(i, 1);
          saveSel();
          renderAll();
        });
        const [btnL, btnR] = d.querySelectorAll(".cmp-colhead__actions .btn");
        btnL.addEventListener("click", () => {
          if (i > 0) {
            [selected[i - 1], selected[i]] = [selected[i], selected[i - 1]];
            saveSel();
            renderAll();
          }
        });
        btnR.addEventListener("click", () => {
          if (i < selected.length - 1) {
            [selected[i + 1], selected[i]] = [selected[i], selected[i + 1]];
            saveSel();
            renderAll();
          }
        });

        // teclado: ← → delete/backspace
        d.tabIndex = 0;
        d.addEventListener("keydown", (ev) => {
          if (ev.key === "ArrowLeft") {
            ev.preventDefault();
            btnL.click();
          }
          if (ev.key === "ArrowRight") {
            ev.preventDefault();
            btnR.click();
          }
          if (ev.key === "Delete" || ev.key === "Backspace") {
            ev.preventDefault();
            d.querySelector(".cmp-colhead__remove").click();
          }
        });

        headgrid.appendChild(d);
      } else {
        const form = document.createElement("form");
        form.className = "cmp-add-col";
        form.setAttribute("role", "columnheader");
        form.id = `col-${i + 1}`;
        form.innerHTML = `
        <input class="cmp-add-input input" list="breeds-datalist"
               placeholder="Adicionar raça..." aria-label="Adicionar raça">
        <button class="btn btn--sm" type="submit">Adicionar</button>`;

        // aceitar soltar aqui para mover a coluna arrastada para esta posição
        form.addEventListener("dragover", (e) => e.preventDefault());
        form.addEventListener("drop", (e) => {
          e.preventDefault();
          if (dragIndex === -1 || dragIndex === i) return;
          selected = move(selected, dragIndex, i);
          saveSel();
          renderAll();
        });

        form.addEventListener("submit", (e) => {
          e.preventDefault();
          const inp = form.querySelector(".cmp-add-input");
          const slug = resolveSlugByName(inp.value);
          if (!slug || selected.includes(slug) || selected.length >= MAX_COLS) return;
          selected.push(slug);
          saveSel();
          renderAll();
          requestAnimationFrame(() => headgrid.querySelector(".cmp-add-input")?.focus());
        });
        headgrid.appendChild(form);
      }
    }
  }

  function makeRowAppender(grid, groupId, breeds) {
    grid.dataset.group = groupId;

    grid.style.gridTemplateColumns = breeds && breeds.length ? colTemplate(MAX_COLS) : "1fr";

    return function row(label, fn) {
      const labelId = `${grid.dataset.group || "g"}-${slugify(label)}`;
      const lbl = cell(label, true);
      lbl.id = labelId;
      lbl.setAttribute("role", "rowheader");
      grid.appendChild(lbl);

      breeds.forEach((b, i) => {
        const c = cell(fn(b));
        c.setAttribute("role", "cell");
        c.setAttribute("aria-labelledby", `${labelId} col-${i + 1}`);
        grid.appendChild(c);
      });
    };
  }

  function renderG1(grid, breeds) {
    const row = makeRowAppender(grid, "g1", breeds);
    row("Grupo FCI", (b) => `Grupo ${b.fci.grupo ?? "—"} — ${b.fci.descricao ?? "—"}`);
    row("Porte", (b) => b.porte?.label ?? "—");
    row("Origem", (b) => b.origem ?? "—");
  }

  function renderG2(grid, breeds) {
    const row = makeRowAppender(grid, "g2", breeds);
    row("Altura", (b) => {
      const m = b.medidas.altura_cm || {};
      return `${m.macho || "—"} ♂ / ${m.femea || "—"} ♀ cm`;
    });
    row("Peso", (b) => {
      const m = b.medidas.peso_kg || {};
      return `${m.macho || "—"} ♂ / ${m.femea || "—"} ♀ kg`;
    });
    row("Expectativa de vida", (b) => `${b.medidas.expectativa_anos || "—"} anos`);
  }

  function renderG31(grid, breeds) {
    const row = makeRowAppender(grid, "g31", breeds);
    row("Nível de energia física", (b) => b.energia.nivel_fisico_txt || "—");
    row("Duração das atividades (≈ min/dia)", (b) => b.energia.minutos_dia ?? "—");
    row("Exigência cognitiva", (b) => b.energia.exigencia_cog_txt || "—");
  }

  function renderG32(grid, breeds) {
    const row = makeRowAppender(grid, "g32", breeds);
    row("Frequência de escovação", (b) => b.pelagem.escovacao_txt || "—");
    row("Queda de pelos", (b) => b.pelagem.queda_txt || "—");
    row("Frequência de tosa", (b) => b.pelagem.tosa_txt || "—");
  }

  function renderG33(grid, breeds) {
    const row = makeRowAppender(grid, "g33", breeds);
    row("Perfil climático", (b) => b.clima.perfil_txt || "—");
    row("Tolerância ao calor", (b) => b.clima.tolerancia_calor_txt || "—");
    row("Tolerância à umidade", (b) => b.clima.tolerancia_umidade_txt || "—");
    row("Adaptação ao espaço", (b) => b.clima.adaptacao_espaco_txt || "—");
  }

  function clearGrids() {
    Object.values(sections).forEach((sec) => {
      const g = sec.querySelector(".cmp-grid");
      if (g) g.innerHTML = "";
    });
  }

  function resolveSlugByName(name) {
    const norm = simplify(name);
    if (!norm) return null;
    const hit =
      data.find(
        (d) => simplify(d.nome) === norm || (d.aliases || []).some((a) => simplify(a) === norm)
      ) ||
      data.find(
        (d) =>
          simplify(d.nome).startsWith(norm) ||
          (d.aliases || []).some((a) => simplify(a).startsWith(norm))
      );
    return hit?.slug || null;
  }

  function renderAll() {
    renderChips();

    // ações rápidas (copiar/limpar)
    const hdr = root.querySelector(".page-header");
    let tools = hdr.querySelector(".js-tools");
    if (!tools) {
      tools = document.createElement("div");
      tools.className = "js-tools";
      tools.style.marginTop = "0.5rem";
      hdr.appendChild(tools);
    }
    tools.innerHTML = "";
    if (selected.length) {
      const share = document.createElement("button");
      share.type = "button";
      share.className = "btn btn--sm with-icon";
      share.textContent = "Copiar link da comparação";

      share.addEventListener("click", async () => {
        const p = new URLSearchParams();
        selected.forEach((s) => p.append("add", s));
        const url = `${location.origin}${location.pathname}?${p.toString()}`;
        const original = share.textContent;
        try {
          await navigator.clipboard.writeText(url);
          share.textContent = "Copiado!";
        } catch {
          share.textContent = "Não deu :(";
        } finally {
          setTimeout(() => (share.textContent = original), 1600);
        }
      });

      const clear = document.createElement("button");
      clear.type = "button";
      clear.className = "btn btn--sm";
      clear.textContent = "Limpar";
      clear.style.marginLeft = "0.5rem";
      clear.addEventListener("click", () => {
        selected = [];
        saveSel();
        renderAll();
      });

      tools.append(share, clear);
    }

    const breeds = selected.map((slug) => data.find((d) => d.slug === slug)).filter(Boolean);
    renderHeadgrid(breeds);

    clearGrids();
    renderG1(sections.g1.querySelector(".cmp-grid"), breeds);
    renderG2(sections.g2.querySelector(".cmp-grid"), breeds);
    renderG31(sections.g31.querySelector(".cmp-grid"), breeds);
    renderG32(sections.g32.querySelector(".cmp-grid"), breeds);
    renderG33(sections.g33.querySelector(".cmp-grid"), breeds);
  }

  async function init() {
    readURLAndMerge();

    const BASE = document.body?.dataset?.baseurl || "";
    try {
      const res = await fetch(`${BASE}/data/breeds-client.json`, { cache: "no-store" });
      data = await res.json();
    } catch (e) {
      console.error(e);
      data = [];
    }

    if (datalist && !datalist.children.length) {
      const opts = new Set();
      data.forEach((b) => {
        opts.add(b.nome);
        (b.aliases || []).forEach((a) => opts.add(a));
      });
      datalist.innerHTML = [...opts].map((n) => `<option value="${n}">`).join("");
    }

    renderAll();
  }

  init();
})();
