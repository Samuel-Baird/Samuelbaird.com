/**
 * Entries for the Exegesis Hall of Shame (/exegesis-hall-of-shame).
 *
 * Add new entries to the TOP of the array (newest first). Keep `heard` to the
 * exegesis as it was said, and keep `source` anonymous unless the speaker said it
 * publicly and we can link it.
 */
export type ShameEntry = {
  id: string;
  reference: string;
  /** The words under examination, quoted from the text. */
  text: string;
  /** The exegesis, as it was said. */
  heard: string;
  /** Who said it and where, kept anonymous unless public. */
  source: string;
  /** Where to read the passage for yourself. */
  readUrl: string;
};

export const SHAME_ENTRIES: ShameEntry[] = [
  {
    id: "dc-132-17-enlarged",
    reference: "D&C 132:17",
    text: "…these angels did not abide my law; therefore, they cannot be enlarged, but remain separately and singly, without exaltation, in their saved condition, to all eternity…",
    heard:
      "“They cannot be enlarged” means they cannot get pregnant. “Enlarged” refers to pregnancy.",
    source:
      "Heard in class. Anonymous instructor, Institute at Utah Valley.",
    readUrl:
      "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/132?lang=eng&id=p17#p17",
  },
];
