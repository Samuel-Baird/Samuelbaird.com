/**
 * Seed script: King Follett Discourse — four contemporary accounts
 *
 * Creates one changelog_document ("King Follett Discourse") with four
 * changelog_versions (one per reporter), each with a single section
 * containing the full versified transcript markdown.
 *
 * Verses [v. 1]–[v. 38] are shared across all four accounts; the base
 * text is Thomas Bullock's (the longest and most detailed). Each account
 * records what its reporter captured; missing passages are noted inline.
 *
 * Usage:
 *   node scripts/seed-king-follett.mjs
 *
 * Requires SUPABASE_SERVICE_ROLE_KEY and NEXT_PUBLIC_SUPABASE_URL in env.
 */

import { readFileSync } from "fs";
import { createClient } from "@supabase/supabase-js";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local" });

const __dirname = dirname(fileURLToPath(import.meta.url));
const contentDir = join(__dirname, "../content/versions/king-follett-discourse");

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY,
);

const DOCUMENT = {
  slug: "king-follett-discourse",
  title: "King Follett Discourse",
  category: "Discourse",
  summary:
    "Joseph Smith's final major public discourse, delivered at the April 1844 general conference in Nauvoo, Illinois, during the funeral of Elder King Follett. Four contemporaneous manuscript accounts survive, each capturing the sermon in the reporter's own shorthand. All four accounts share a common versification (vv. 1–38) based on the longest account (Thomas Bullock), making it easy to compare how each reporter recorded the same passage. Topics include the nature of God, the eternal existence of intelligence, the potential of human souls, and the salvation of the dead.",
};

const VERSIONS = [
  {
    label: "Willard Richards account",
    published_on: "1844-04-07",
    ordinal: 0,
    source_type: "markdown",
    source_url:
      "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-willard-richards/1#full-transcript",
    confidence: "official-digital",
    file: "willard-richards.md",
    sectionHeading: "Willard Richards — JS Journal, 1842–1844, bk. 4, pp. [67]–[71]",
  },
  {
    label: "Wilford Woodruff account",
    published_on: "1844-04-07",
    ordinal: 1,
    source_type: "markdown",
    source_url:
      "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-wilford-woodruff/1#full-transcript",
    confidence: "official-digital",
    file: "wilford-woodruff.md",
    sectionHeading: "Wilford Woodruff — Journal, vol. 5, pp. [133]–[140]",
  },
  {
    label: "Thomas Bullock account",
    published_on: "1844-04-07",
    ordinal: 2,
    source_type: "markdown",
    source_url:
      "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-thomas-bullock/1#full-transcript",
    confidence: "official-digital",
    file: "thomas-bullock.md",
    sectionHeading: "Thomas Bullock — Minutes, 6–9 Apr. 1844, pp. 14–22",
  },
  {
    label: "William Clayton account",
    published_on: "1844-04-07",
    ordinal: 3,
    source_type: "markdown",
    source_url:
      "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-william-clayton/1#full-transcript",
    confidence: "official-digital",
    file: "william-clayton.md",
    sectionHeading: "William Clayton — Minutes, 6–8 Apr. 1844, pp. 11–18",
  },
];

async function main() {
  console.log("Seeding King Follett Discourse…");

  // Upsert document
  const { data: existingDoc } = await supabase
    .from("changelog_documents")
    .select("id")
    .eq("slug", DOCUMENT.slug)
    .maybeSingle();

  let docId;
  if (existingDoc) {
    console.log(`  Document already exists (id: ${existingDoc.id}), updating…`);
    const { error } = await supabase
      .from("changelog_documents")
      .update({ title: DOCUMENT.title, summary: DOCUMENT.summary, category: DOCUMENT.category })
      .eq("id", existingDoc.id);
    if (error) throw error;
    docId = existingDoc.id;
  } else {
    const { data, error } = await supabase
      .from("changelog_documents")
      .insert(DOCUMENT)
      .select("id")
      .single();
    if (error) throw error;
    docId = data.id;
    console.log(`  Created document (id: ${docId})`);
  }

  for (const version of VERSIONS) {
    const markdown = readFileSync(join(contentDir, version.file), "utf-8");

    // Check for existing version by label
    const { data: existingVersion } = await supabase
      .from("changelog_versions")
      .select("id")
      .eq("document_id", docId)
      .eq("label", version.label)
      .maybeSingle();

    let versionId;
    if (existingVersion) {
      console.log(`  Version "${version.label}" already exists, updating…`);
      const { error } = await supabase
        .from("changelog_versions")
        .update({
          published_on: version.published_on,
          ordinal: version.ordinal,
          source_type: version.source_type,
          source_url: version.source_url,
          confidence: version.confidence,
        })
        .eq("id", existingVersion.id);
      if (error) throw error;
      versionId = existingVersion.id;
    } else {
      const { data, error } = await supabase
        .from("changelog_versions")
        .insert({
          document_id: docId,
          label: version.label,
          published_on: version.published_on,
          ordinal: version.ordinal,
          source_type: version.source_type,
          source_url: version.source_url,
          confidence: version.confidence,
        })
        .select("id")
        .single();
      if (error) throw error;
      versionId = data.id;
      console.log(`  Created version "${version.label}" (id: ${versionId})`);
    }

    // Delete existing sections and replace
    await supabase.from("changelog_sections").delete().eq("version_id", versionId);

    const { error: sectionError } = await supabase.from("changelog_sections").insert({
      version_id: versionId,
      ordinal: 0,
      heading: version.sectionHeading,
      body_markdown: markdown,
    });
    if (sectionError) throw sectionError;
    console.log(`    Wrote section for "${version.label}"`);
  }

  console.log("Done.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
