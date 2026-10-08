// Easy puzzle: click the tiles in ascending order (1 → 6). Verified server-side.
(async function () {
  const box = document.getElementById("puzzle");
  const btn = document.getElementById("submit-btn");
  const msg = document.getElementById("puzzle-msg");
  let expected = 1, clicked = [];

  async function load() {
    expected = 1; clicked = []; btn.disabled = true;
    msg.textContent = "Clique les cases dans l'ordre : 1 → 6";
    const { tiles } = await (await fetch("/puzzle/new")).json();
    box.innerHTML = "";
    tiles.forEach(n => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "tile"; b.textContent = n;
      b.onclick = () => click(b, n);
      box.appendChild(b);
    });
  }

  async function click(el, n) {
    if (n !== expected) { msg.textContent = "Mauvais ordre, on recommence !"; return load(); }
    el.classList.add("ok"); el.disabled = true; clicked.push(n); expected++;
    if (clicked.length === 6) {
      const r = await fetch("/puzzle/check", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order: clicked })
      });
      if (r.ok) { msg.textContent = "✅ Bravo, tu n'es pas un robot !"; btn.disabled = false; }
      else { msg.textContent = "Trop rapide ou invalide, réessaie."; load(); }
    }
  }
  load();
})();
