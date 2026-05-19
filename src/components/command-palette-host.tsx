import { CommandPalette } from "@/components/command-palette";
import { getSearchIndex } from "@/lib/data";

export async function CommandPaletteHost() {
  const items = await getSearchIndex();
  return <CommandPalette items={items} />;
}
