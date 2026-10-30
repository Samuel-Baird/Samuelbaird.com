const list = document.getElementById("books");
const fmt = d => new Date(d + "T00:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
for (const b of window.BOOKS) {
  const li = document.createElement("li");
  li.className = "book";
  li.innerHTML = `<a href="${b.link}" target="_blank" rel="noopener">${b.cover ? `<img src="${b.cover}" alt="Cover of ${b.title}" loading="lazy">` : `<div class="blank" role="img" aria-label="No cover"></div>`}<h3></h3><time datetime="${b.read}">${fmt(b.read)}</time></a>`;
  li.querySelector("h3").textContent = b.title;
  list.append(li);
}
