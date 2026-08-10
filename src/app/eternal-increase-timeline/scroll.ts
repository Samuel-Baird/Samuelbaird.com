/**
 * Jumping to an entry or an era section is an animation, so it honours
 * `prefers-reduced-motion` like every other motion on the site: the
 * destination is the same either way, only the travel is skipped.
 */
function behavior(): ScrollBehavior {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ? "auto"
    : "smooth";
}

export function scrollToId(id: string) {
  document
    .getElementById(id)
    ?.scrollIntoView({ behavior: behavior(), block: "start" });
}

export function scrollToTop() {
  window.scrollTo({ top: 0, behavior: behavior() });
}
