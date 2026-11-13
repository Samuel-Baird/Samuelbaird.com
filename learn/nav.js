/* Course switcher for /learn pages. Reads /learn/courses.json and puts a slim bar at the top
   of the page: "Learn" (home) plus one link per course, the current one marked. Include with
   <script src="/learn/nav.js" defer></script>. */
(function () {
  var css =
    ".learn-nav{border-bottom:1px solid var(--border);background:var(--background)}" +
    ".learn-nav .in{max-width:56rem;margin:0 auto;padding:0 16px;display:flex;gap:4px;align-items:center;overflow-x:auto;scrollbar-width:none}" +
    ".learn-nav .in::-webkit-scrollbar{display:none}" +
    ".learn-nav a{flex:0 0 auto;display:inline-flex;align-items:center;min-height:44px;padding:0 10px;color:var(--muted);" +
    "text-decoration:none;font:500 .82rem var(--font-sans);font-variant-caps:all-small-caps;letter-spacing:.08em;" +
    "border-bottom:2px solid transparent}" +
    ".learn-nav a:hover{color:var(--foreground)}" +
    ".learn-nav a[aria-current=page]{color:var(--foreground);border-bottom-color:var(--honey)}" +
    ".learn-nav .home{color:var(--accent);padding-left:0}" +
    ".learn-nav .sep{width:1px;height:18px;background:var(--border);flex:0 0 auto;margin:0 4px}";
  function here(href) {
    var p = location.pathname.replace(/\/index\.html$/, "").replace(/\/$/, "");
    return p === href || p.indexOf(href + "/") === 0;
  }
  function render(courses) {
    var st = document.createElement("style");
    st.textContent = css;
    document.head.appendChild(st);
    var nav = document.createElement("nav");
    nav.className = "learn-nav";
    nav.setAttribute("aria-label", "Courses");
    var inner = document.createElement("div");
    inner.className = "in";
    var home = document.createElement("a");
    home.href = "/learn";
    home.className = "home";
    home.textContent = "← Learn";
    if (here("/learn") && !courses.some(function (c) { return here(c.href); })) home.setAttribute("aria-current", "page");
    inner.appendChild(home);
    var sep = document.createElement("span");
    sep.className = "sep";
    inner.appendChild(sep);
    courses.forEach(function (c) {
      var a = document.createElement("a");
      a.href = c.href;
      a.textContent = c.code;
      a.title = c.code + " · " + c.title;
      if (here(c.href)) a.setAttribute("aria-current", "page");
      inner.appendChild(a);
    });
    nav.appendChild(inner);
    document.body.insertBefore(nav, document.body.firstChild);
  }
  fetch("/learn/courses.json")
    .then(function (r) { return r.json(); })
    .then(render)
    .catch(function () {});
})();
