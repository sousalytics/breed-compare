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
});
