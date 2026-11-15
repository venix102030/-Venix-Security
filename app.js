const countEl = document.getElementById("count");
const sideCount = document.getElementById("sideCount");
const events = document.getElementById("events");
const button = document.getElementById("simulate");
let count = 0;

const now = new Date();
document.getElementById("today").textContent = now.toLocaleDateString("pt-BR", {
  weekday: "short", day: "2-digit", month: "short", year: "numeric"
});

button.addEventListener("click", () => {
  count += 1;
  countEl.textContent = String(count).padStart(2, "0");
  sideCount.textContent = String(count);

  const empty = events.querySelector(".empty-state");
  if (empty) empty.remove();

  const item = document.createElement("div");
  item.className = "event";

  const mark = document.createElement("div");
  mark.className = "event-mark";
  mark.textContent = "!";
  const copy = document.createElement("div");
  copy.className = "event-copy";
  const title = document.createElement("b");
  title.textContent = "Alerta demonstrativo — conferência necessária";
  const description = document.createElement("small");
  description.textContent = "Exemplo fictício de ocorrência na entrada escolar. A equipe deve realizar conferência humana.";
  copy.append(title, description);
  const time = document.createElement("span");
  time.className = "event-time";
  time.textContent = new Date().toLocaleTimeString("pt-BR", {hour:"2-digit", minute:"2-digit"});
  item.append(mark, copy, time);
  events.prepend(item);
});
