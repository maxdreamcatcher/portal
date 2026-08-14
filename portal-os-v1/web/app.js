const output = document.getElementById("output");
const btnPing = document.getElementById("btnPing");

btnPing.addEventListener("click", () => {
  output.textContent = "Runtime pinged. Portal‑OS v1 responding.";
});
