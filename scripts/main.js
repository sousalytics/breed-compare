document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".scale").forEach((el) => {
    const n = Number(el.getAttribute("data-value") || 0);
    el.innerHTML = "";
    for (let i = 0; i < n; i++) el.appendChild(document.createElement("i"));
  });
});
