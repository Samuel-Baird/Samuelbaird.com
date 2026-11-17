/** Citations in the form the Joseph Smith Papers site itself uses. */

export function accessedDate(d = new Date()): string {
  return d.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "America/Denver",
  });
}

/**
 * e.g. "Journal, 1835–1836, p. 10, The Joseph Smith Papers, accessed
 * November 8, 2026, https://www.josephsmithpapers.org/paper-summary/journal-1835-1836/11"
 */
export function citation(p: { title: string; page?: string; url: string; accessed?: Date }): string {
  const parts = [p.title.replace(/[.,\s]+$/, "")];
  if (p.page) parts.push(`p. ${p.page}`);
  parts.push("The Joseph Smith Papers", `accessed ${accessedDate(p.accessed)}`, p.url);
  return parts.join(", ");
}
