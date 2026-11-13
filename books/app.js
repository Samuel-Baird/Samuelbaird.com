const list = document.getElementById("books");
const fmt = d => new Date(d + "T00:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
// The list is pre-rendered into the HTML by scripts/build.mjs; only build it here if that is missing.
if (!list.children.length) for (const b of window.BOOKS) {
  const li = document.createElement("li");
  li.className = "book";
  // Anything that isn't an Amazon (book) link is an article, unless data.js says otherwise.
  li.dataset.type = b.type || (/amazon\./.test(b.link) ? "book" : "article");
  li.innerHTML = `<a href="${b.link}" target="_blank" rel="noopener">${b.cover ? `<img src="${b.cover}" alt="Cover of ${b.title}" loading="lazy">` : `<div class="blank" role="img" aria-label="No cover"></div>`}<h3></h3><time datetime="${b.read}">${fmt(b.read)}</time></a>`;
  li.querySelector("h3").textContent = b.title;
  list.append(li);
}

const buttons = document.querySelectorAll(".filters button");
for (const btn of buttons) {
  btn.addEventListener("click", () => {
    for (const o of buttons) o.setAttribute("aria-pressed", String(o === btn));
    for (const li of list.children) li.hidden = btn.dataset.filter !== "all" && li.dataset.type !== btn.dataset.filter;
  });
}

const nb = [...list.children].filter(li => li.dataset.type === "book").length;
const na = list.children.length - nb;
if (!document.getElementById("count").textContent) document.getElementById("count").textContent = `${nb} book${nb === 1 ? "" : "s"} and ${na} article${na === 1 ? "" : "s"}, newest first, with the date I finished each one.`;
