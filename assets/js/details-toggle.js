document.addEventListener("click", (e) => {
  const btn = e.target.closest(".indicator__toggle");
  if (!btn) return;
  const id = btn.getAttribute("aria-controls");
  const panel = document.getElementById(id);
  if (!panel) return;
  const open = btn.getAttribute("aria-expanded") === "true";
  btn.setAttribute("aria-expanded", String(!open));
  panel.hidden = open;
});
