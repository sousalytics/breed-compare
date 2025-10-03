(function () {
  const root = document.querySelector(".page-compare");
  if (!root) return;

  const MAX_COLS = 3;

  const form = root.querySelector("#compare-form");
  const inputQ = root.querySelector("#q-compare");
  const btnAdd = root.querySelector("#add-breed");
  const chips = root.querySelector(".selected-chips");
  const datalist = root.querySelector("#breeds-datalist");

  const main = root.querySelector(".compare-main");

  function mkSection(title) {
    const sec = document.createElement("section");
    sec.className = "cmp-card card";
    sec.innerHTML = `
      <h2 class="cmp-card__title">${title}</h2>
      <div class="cmp-grid"></div>`;
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

  const simplify = (s) =>
    (s || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();

  let data = [];
  let selected = [];

  function readURL() {
    const p = new URLSearchParams(location.search);
    selected = p.getAll("add").slice(0, MAX_COLS);
    selected = [...new Set(selected)];
  }
  function writeURL() {
    const p = new URLSearchParams();
    selected.forEach((s) => p.append("add", s));
    history.replaceState(null, "", p.toString() ? `?${p.toString()}` : location.pathname);
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
        writeURL();
        renderAll();
      });
      chips.appendChild(chip);
    });
  }

  function clearGrids() {
    Object.values(sections).forEach((sec) => {
      const g = sec.querySelector(".cmp-grid");
      if (g) g.innerHTML = "";
    });
  }

  function colTemplate(nCols) {
    return `minmax(180px, 1fr)${" minmax(180px, 1fr)".repeat(nCols)}`;
  }

  function h(img, alt = "") {
    if (!img) return "";
    return `<img src="${img}" alt="${alt}" loading="lazy" decoding="async" width="96" height="64" class="cmp-thumb">`;
  }

  function cell(text, isLabel = false) {
    const d = document.createElement("div");
    d.className = "cmp-cell" + (isLabel ? " cmp-cell--label" : "");
    d.innerHTML = text;
    return d;
  }
  function cellHead(b) {
    const d = document.createElement("div");
    d.className = "cmp-cell cmp-cell--head";
    d.innerHTML = `<div class="cmp-colhead">${h(b.foto, "")}<div class="cmp-colhead__txt"><strong>${
      b.nome
    }</strong></div></div>`;
    return d;
  }

  function renderG1(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    grid.appendChild(cell("Rótulo", true));
    breeds.forEach((b) => grid.appendChild(cellHead(b)));
    row("Grupo FCI", (b) => `Grupo ${b.fci.grupo} — ${b.fci.descricao}`);
    row("Porte", (b) => b.porte.label);
    row("Origem", (b) => b.origem);
    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG2(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    grid.appendChild(cell("Rótulo", true));
    breeds.forEach((b) => grid.appendChild(cellHead(b)));
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
    grid.appendChild(cell("Rótulo", true));
    breeds.forEach((b) => grid.appendChild(cellHead(b)));
    row("Nível de energia física", (b) => b.energia.nivel_fisico_txt);
    row("Duração das atividades (≈ min/dia)", (b) => `${b.energia.minutos_dia}`);
    row("Exigência cognitiva", (b) => b.energia.exigencia_cog_txt);
    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG32(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    grid.appendChild(cell("Rótulo", true));
    breeds.forEach((b) => grid.appendChild(cellHead(b)));
    row("Frequência de escovação", (b) => b.pelagem.escovacao_txt);
    row("Queda de pelos", (b) => b.pelagem.queda_txt);
    row("Frequência de tosa", (b) => b.pelagem.tosa_txt);
    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderG34(grid, breeds) {
    grid.style.gridTemplateColumns = colTemplate(breeds.length);
    grid.appendChild(cell("Rótulo", true));
    breeds.forEach((b) => grid.appendChild(cellHead(b)));
    row("Perfil climático", (b) => b.clima.perfil_txt);
    row("Tolerância ao calor", (b) => b.clima.tolerancia_calor_txt);
    row("Tolerância à umidade", (b) => b.clima.tolerancia_umidade_txt);
    row("Adaptação ao espaço", (b) => b.clima.adaptacao_espaco_txt);
    function row(label, fn) {
      grid.appendChild(cell(label, true));
      breeds.forEach((b) => grid.appendChild(cell(fn(b))));
    }
  }

  function renderAll() {
    renderChips();
    clearGrids();
    const breeds = selected.map((slug) => data.find((d) => d.slug === slug)).filter(Boolean);
    renderG1(sections.g1.querySelector(".cmp-grid"), breeds);
    renderG2(sections.g2.querySelector(".cmp-grid"), breeds);
    renderG31(sections.g31.querySelector(".cmp-grid"), breeds);
    renderG32(sections.g32.querySelector(".cmp-grid"), breeds);
    renderG34(sections.g34.querySelector(".cmp-grid"), breeds);
  }

  function resolveSlugByName(name) {
    const norm = simplify(name);
    if (!norm) return null;
    const hit = data.find(
      (d) => simplify(d.nome) === norm || (d.aliases || []).some((a) => simplify(a) === norm)
    );
    return hit?.slug || null;
  }

  function populateDatalist() {
    const dl = document.getElementById("breeds-datalist");
    if (!dl) return;
    dl.innerHTML = data.map((d) => `<option value="${d.nome}">`).join("");
  }

  async function init() {
    readURL();
    const DATA_URL = root.dataset.dataUrl || "/data/breeds-client.json";
    try {
      const res = await fetch(DATA_URL, { cache: "no-store" });
      data = await res.json();
    } catch (e) {
      console.error("Falha ao carregar dados", e);
      data = [];
    }

    if (datalist && !datalist.options.length) {
      datalist.innerHTML = data.map((b) => `<option value="${b.nome}">`).join("");
    }

    populateDatalist();
    renderAll();
  }

  btnAdd.addEventListener("click", () => {
    const slug = resolveSlugByName(inputQ.value);
    if (!slug) return;
    if (selected.includes(slug)) return;
    if (selected.length >= MAX_COLS) return;
    selected.push(slug);
    writeURL();
    renderAll();
    inputQ.value = "";
    inputQ.focus();
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    btnAdd.click();
  });

  init();
})();
