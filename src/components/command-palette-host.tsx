import { CommandPalette } from "@/components/command-palette";
import { getSearchIndex } from "@/lib/data";
import { getPremiumStatus } from "@/lib/permissions";

export async function CommandPaletteHost() {
  const status = await getPremiumStatus();
  const items = await getSearchIndex({ includeCritical: status.premium });
  return <CommandPalette items={items} />;
}
