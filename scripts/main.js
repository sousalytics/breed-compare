document.addEventListener("DOMContentLoaded", () => {
  // 1) Escala segmentada (5 pills)
  document.querySelectorAll(".scale").forEach((el) => {
    const n = Number(el.getAttribute("data-value") || 0);
    el.innerHTML = "";
    for (let i = 1; i <= 5; i++) {
      const seg = document.createElement("i");
      if (i <= n) seg.className = "is-on";
      el.appendChild(seg);
    }
  });

  // 2) Botão controla o <details> correspondente
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

(function () {
  const root = document.querySelector(".page-breeds");
  if (!root) return;

  const form = root.querySelector("#breed-filters");
  const list = root.querySelector(".breed-list");
  const items = Array.from(list.querySelectorAll(".breed-card"));
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
  }

  function writeURL(q, porte, grupo) {
    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (porte) p.set("porte", porte);
    if (grupo) p.set("grupo", grupo);
    const url = p.toString() ? `?${p.toString()}` : location.pathname;
    history.replaceState(null, "", url);
  }

  function applyFilter() {
    const q = inputQ.value.trim().toLowerCase();
    const porte = selPorte.value;
    const grupo = selGrupo.value;

    let visible = 0;
    items.forEach((li) => {
      const name = li.dataset.name || "";
      const p = li.dataset.porte || "";
      const g = li.dataset.grupo || "";
      const okQ = !q || name.includes(q);
      const okP = !porte || p === porte;
      const okG = !grupo || g === grupo;
      li.hidden = !(okQ && okP && okG);
      if (!li.hidden) visible++;
    });

    if (status) status.textContent = `${visible} raça(s) encontrada(s)`;
    writeURL(q, porte, grupo);
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    applyFilter();
  });
  inputQ.addEventListener("input", applyFilter);
  selPorte.addEventListener("change", applyFilter);
  selGrupo.addEventListener("change", applyFilter);
  btnClear.addEventListener("click", () => {
    inputQ.value = "";
    selPorte.value = "";
    selGrupo.value = "";
    applyFilter();
  });

  readURL();
  applyFilter();
})();
