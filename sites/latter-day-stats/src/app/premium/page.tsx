import { redirect } from "next/navigation";

// Premium is gone: everything that lived here is free. Old links and bookmarks
// land on the channel list.
export default function PremiumPage() {
  redirect("/channels");
}
