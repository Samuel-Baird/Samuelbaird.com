import { CommandPalette } from "@/components/command-palette";
import { getSearchIndex, type SearchItem } from "@/lib/data";
import { getPremiumStatus } from "@/lib/permissions";

export async function CommandPaletteHost() {
  // This renders inside the nav on every page and there is no error boundary
  // above it, so a Supabase outage here would 500 even static content pages.
  // Degrade to an empty palette instead.
  let items: SearchItem[] = [];
  try {
    const status = await getPremiumStatus();
    items = await getSearchIndex({ includeCritical: status.premium });
  } catch (error) {
    console.error("command palette search index unavailable:", error);
  }
  return <CommandPalette items={items} />;
}
