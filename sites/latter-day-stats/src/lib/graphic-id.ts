// A graphic's id is its PNG's file name without the extension. Kept apart from
// src/lib/data-explorer.ts (which imports every dataset JSON) so client
// components can use it without pulling all that data into their bundles and
// the Worker's SSR chunks.
export function graphicId(graphic: { imageSrc: string }): string {
  return graphic.imageSrc.split("/").pop()!.replace(/\.png$/, "");
}
