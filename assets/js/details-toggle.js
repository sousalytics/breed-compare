// Toggle unificado para os indicadores (“+ / –”)
// Suporta dois padrões:
// 1) <button class="indicator__togglebtn" data-target="ID_DO_DETAILS">…</button>
//    <details id="ID_DO_DETAILS" class="indicator__details">…</details>
// 2) <button class="indicator__toggle" aria-controls="PAINEL_ID" aria-expanded="false">…</button>
//    <div id="PAINEL_ID" hidden>…</div>

(function () {
  function toggleDetails(btn) {
    const id = btn.getAttribute("data-target");
    if (!id) return false;
    const det = document.getElementById(id);
    if (!det) return false;

    const isOpen = det.hasAttribute("open");
    if (isOpen) det.removeAttribute("open");
    else det.setAttribute("open", "");
    btn.setAttribute("aria-expanded", String(!isOpen));
    return true;
  }

  function togglePanel(btn) {
    const id = btn.getAttribute("aria-controls");
    if (!id) return false;
    const panel = document.getElementById(id);
    if (!panel) return false;

    const open = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!open));
    panel.hidden = open;
    return true;
  }

  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".indicator__togglebtn") || e.target.closest(".indicator__toggle");
    if (!btn) return;

    // tenta <details>…; se não rolar, tenta painel com hidden
    if (!toggleDetails(btn)) togglePanel(btn);
  });
})();
