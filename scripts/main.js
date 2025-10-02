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
