document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".scale").forEach((el) => {
    const n = Number(el.getAttribute("data-value") || 0);
    el.innerHTML = "";
    for (let i = 1; i <= 5; i++) {
      const seg = document.createElement("i");
      if (i <= n) seg.className = "is-on";
      el.appendChild(seg);
    }
  });

  document.querySelectorAll(".indicator__togglebtn").forEach((btn) => {
    const id = btn.getAttribute("data-target");
    const det = document.getElementById(id);
    if (!det) return;

    // inicial
    btn.setAttribute("aria-expanded", det.hasAttribute("open") ? "true" : "false");

    btn.addEventListener("click", () => {
      const isOpen = det.hasAttribute("open");
      if (isOpen) det.removeAttribute("open");
      else det.setAttribute("open", "");
      btn.setAttribute("aria-expanded", String(!isOpen));
    });
  });
});

const DEBOUNCE_MS = 250; // ↑ (até ~300 ms) se engasgar; ↓ (150–200 ms) se parecer “lento” de resposta
const USE_DEBOUNCE = true; // true = espera ~250ms após digitar; false = aplica a cada tecla

function debounce(fn, wait = 250) {
  let t;
  return function debounced(...args) {
    const ctx = this;
    clearTimeout(t);
    t = setTimeout(() => fn.apply(ctx, args), wait);
  };
}

function simplify(str) {
  return (str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[’'´`-]+/g, " ")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

(function () {
  const root = document.querySelector(".page-breeds");
  if (!root) return;

  const form = root.querySelector("#breed-filters");
  const list = root.querySelector(".breed-list");
  if (!list) return;

  const items = Array.from(list.querySelectorAll(".breed-card"));

  const normTextCache = new Map();
  items.forEach((li) => {
    const nameNorm = simplify(li.dataset.name || "");
    const aliasNorm = simplify(li.dataset.alias || "");
    normTextCache.set(li, (nameNorm + " " + aliasNorm).trim());
  });

  const status = root.querySelector("#results-status");
  const inputQ = form.querySelector("#q");
  const selPorte = form.querySelector("#porte");
  const selGrupo = form.querySelector("#grupo");
  const btnClear = form.querySelector("#limpar");

  function readURL() {
    const p = new URLSearchParams(location.search);
    inputQ.value = p.get("q") || "";
    selPorte.value = p.get("porte") || "";
    selGrupo.value = p.get("grupo") || "";

    lastState = {
      q: inputQ.value.trim().toLowerCase(),
      porte: selPorte.value,
      grupo: selGrupo.value,
    };
  }

  let lastState = { q: "", porte: "", grupo: "" };

  function writeURL(q, porte, grupo) {
    if (lastState.q === q && lastState.porte === porte && lastState.grupo === grupo) return;
    lastState = { q, porte, grupo };

    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (porte) p.set("porte", porte);
    if (grupo) p.set("grupo", grupo);
    const url = p.toString() ? `?${p.toString()}` : location.pathname;
    history.replaceState(null, "", url);
  }

  function applyFilter() {
    const qRaw = inputQ.value;
    const qNorm = simplify(qRaw);
    const qTokens = qNorm ? qNorm.split(" ") : [];

    const porte = selPorte.value;
    const grupo = selGrupo.value;

    let visible = 0;
    items.forEach((li) => {
      const searchable = normTextCache.get(li) || "";
      const p = li.dataset.porte || "";
      const g = li.dataset.grupo || "";

      const okQ = !qTokens.length || qTokens.every((t) => searchable.includes(t));
      const okP = !porte || p === porte;
      const okG = !grupo || g === grupo;

      li.hidden = !(okQ && okP && okG);
      if (!li.hidden) visible++;
    });

    if (status) status.textContent = `${visible} raça(s) encontrada(s)`;
    writeURL(qRaw.trim().toLowerCase(), porte, grupo);
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    applyFilter();
  });
  selPorte.addEventListener("change", applyFilter);
  selGrupo.addEventListener("change", applyFilter);
  btnClear?.addEventListener("click", () => {
    inputQ.value = "";
    selPorte.value = "";
    selGrupo.value = "";
    applyFilter();
  });

  const debouncedApply = USE_DEBOUNCE ? debounce(applyFilter, DEBOUNCE_MS) : applyFilter;

  let composing = false;
  inputQ.addEventListener("compositionstart", () => {
    composing = true;
  });
  inputQ.addEventListener("compositionend", () => {
    composing = false;
    applyFilter();
  });

  inputQ.addEventListener("input", () => {
    if (composing) return;
    debouncedApply();
  });

  inputQ.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      applyFilter();
    }
  });
  inputQ.addEventListener("blur", applyFilter);

  readURL();
  applyFilter();
})();
