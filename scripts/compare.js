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
    g34: mkSection("Clima & Espaço"),
  };
  Object.values(sections).forEach((s) => main.appendChild(s));

  let data = [];
  let selected = [];

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

  function colTemplate(nCols) {
    return `minmax(180px, 1fr)${" minmax(200px, 1fr)".repeat(nCols)}`;
  }

  function hThumb(img, alt = "") {
    if (!img) return "";
    return `<img src="${img}" alt="${alt}" loading="lazy" decoding="async" width="96" height="64" class="cmp-thumb">`;
  }

  function cell(text, isLabel = false) {
    const d = document.createElement("div");
    d.className = "cmp-cell" + (isLabel ? " cmp-cell--label" : "");
    d.innerHTML = text;
    return d;
  }

  function renderHeadgrid(breeds) {
    headgrid.innerHTML = "";
    headgrid.style.gridTemplateColumns = colTemplate(breeds.length);
    headgrid.appendChild(cell("&nbsp;", true));

    breeds.forEach((b) => {
      const d = document.createElement("div");
      d.className = "cmp-colhead";
      d.innerHTML = `<div class="cmp-colhead__box">${hThumb(
        b.foto,
        ""
      )}<div class="cmp-colhead__txt"><strong>${b.nome}</strong></div></div>`;
      headgrid.appendChild(d);
    });

    for (let i = breeds.length; i < MAX_COLS; i++) {
      const form = document.createElement("form");
      form.className = "cmp-add-col";
      form.innerHTML = `
        <input class="cmp-add-input" list="breeds-datalist" placeholder="Adicionar raça..." aria-label="Adicionar raça">
        <button class="btn btn--sm" type="submit">Adicionar</button>`;
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const inp = form.querySelector("input");
        const slug = resolveSlugByName(inp.value);
        if (!slug) return;
        if (selected.includes(slug)) return;
        if (selected.length >= MAX_COLS) return;
        selected.push(slug);
        saveSel();
        renderAll();
      });
      headgrid.appendChild(form);
    }
  }

  function renderG1(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    row("Grupo FCI", (b) => `Grupo ${b.fci.grupo ?? "—"} — ${b.fci.descricao ?? "—"}`);
    row("Porte", (b) => b.porte?.label ?? "—");
    row("Origem", (b) => b.origem ?? "—");

    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG2(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    row("Altura", (b) => {
      const m = b.medidas.altura_cm || {};
      return `${m.macho || "—"} ♂ / ${m.femea || "—"} ♀ cm`;
    });
    row("Peso", (b) => {
      const m = b.medidas.peso_kg || {};
      return `${m.macho || "—"} ♂ / ${m.femea || "—"} ♀ kg`;
    });
    row("Expectativa de vida", (b) => `${b.medidas.expectativa_anos || "—"} anos`);

    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG31(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    row("Nível de energia física", (b) => b.energia.nivel_fisico_txt || "—");
    row("Duração das atividades (≈ min/dia)", (b) => b.energia.minutos_dia ?? "—");
    row("Exigência cognitiva", (b) => b.energia.exigencia_cog_txt || "—");

    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG32(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    row("Frequência de escovação", (b) => b.pelagem.escovacao_txt || "—");
    row("Queda de pelos", (b) => b.pelagem.queda_txt || "—");
    row("Frequência de tosa", (b) => b.pelagem.tosa_txt || "—");

    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG34(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    row("Perfil climático", (b) => b.clima.perfil_txt || "—");
    row("Tolerância ao calor", (b) => b.clima.tolerancia_calor_txt || "—");
    row("Tolerância à umidade", (b) => b.clima.tolerancia_umidade_txt || "—");
    row("Adaptação ao espaço", (b) => b.clima.adaptacao_espaco_txt || "—");

    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
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
    const hit = data.find(
      (d) => simplify(d.nome) === norm || (d.aliases || []).some((a) => simplify(a) === norm)
    );
    return hit?.slug || null;
  }

  function renderAll() {
    renderChips();

    const breeds = selected.map((slug) => data.find((d) => d.slug === slug)).filter(Boolean);
    renderHeadgrid(breeds);

    clearGrids();
    renderG1(sections.g1.querySelector(".cmp-grid"), breeds);
    renderG2(sections.g2.querySelector(".cmp-grid"), breeds);
    renderG31(sections.g31.querySelector(".cmp-grid"), breeds);
    renderG32(sections.g32.querySelector(".cmp-grid"), breeds);
    renderG34(sections.g34.querySelector(".cmp-grid"), breeds);
  }

  async function init() {
    readURLAndMerge();
    try {
      const res = await fetch("/data/breeds-client.json", { cache: "no-store" });
      data = await res.json();
    } catch (e) {
      console.error(e);
      data = [];
    }

    if (datalist && !datalist.children.length) {
      datalist.innerHTML = data.map((b) => `<option value="${b.nome}">`).join("");
    }
    renderAll();
  }

  init();
})();
