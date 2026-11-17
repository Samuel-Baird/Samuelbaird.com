/**
 * Folder-level view over the Data Explorer's contents, for the index page
 * at /data-explorer. A "folder" is one linked card: a single dataset, a
 * category collection of datasets (see Dataset["category"]'s doc comment
 * in data-explorer.ts), or a study that has its own graphics. Studies
 * without graphics of their own never produce a folder here - see
 * study-graphics.ts's getStudyFolderSlugs().
 *
 * Datasets are known statically at import time; studies live in the
 * database, so the caller (the page component) fetches them and passes the
 * rows in here rather than this module reaching for the database itself.
 */
import { categorySlug, deriveTraditions, type Dataset, type Graphic } from "@/lib/data-explorer";
import type { Study } from "@/lib/types";

export type DatasetFolder = {
  kind: "dataset";
  key: string;
  dataset: Dataset;
  category: string | null;
  traditions: string[];
};

export type CategoryFolder = {
  kind: "category";
  key: string;
  category: string;
  slug: string;
  items: Dataset[];
  traditions: string[];
};

export type StudyFolder = {
  kind: "study";
  key: string;
  study: Study;
  graphics: Graphic[];
  category: string | null;
  traditions: string[];
};

export type Folder = DatasetFolder | CategoryFolder | StudyFolder;

function datasetTraditions(dataset: Dataset): string[] {
  const set = new Set<string>();
  for (const g of dataset.graphics) for (const t of deriveTraditions(g)) set.add(t);
  return [...set];
}

/** Groups datasets by consecutive runs of the same `category` into
 * CategoryFolder cards, same rule as the Data Explorer index has always
 * used - a category split across two places in DATASETS renders as two
 * separate collections, not one. */
export function buildDatasetFolders(datasets: Dataset[]): Folder[] {
  const folders: Folder[] = [];
  for (const dataset of datasets) {
    const category = dataset.category ?? null;
    const last = folders[folders.length - 1];
    if (category && last?.kind === "category" && last.category === category) {
      last.items.push(dataset);
      for (const t of datasetTraditions(dataset)) {
        if (!last.traditions.includes(t)) last.traditions.push(t);
      }
      continue;
    }
    if (category) {
      folders.push({
        kind: "category",
        key: `category:${categorySlug(category)}`,
        category,
        slug: categorySlug(category),
        items: [dataset],
        traditions: datasetTraditions(dataset),
      });
    } else {
      folders.push({
        kind: "dataset",
        key: `dataset:${dataset.slug}`,
        dataset,
        category: null,
        traditions: datasetTraditions(dataset),
      });
    }
  }
  return folders;
}

export function buildStudyFolders(
  studies: Study[],
  graphicsBySlug: Map<string, Graphic[]>,
): StudyFolder[] {
  const folders: StudyFolder[] = [];
  for (const study of studies) {
    const graphics = graphicsBySlug.get(study.slug) ?? [];
    if (graphics.length === 0) continue;
    folders.push({
      kind: "study",
      key: `study:${study.slug}`,
      study,
      graphics,
      category: study.category ?? null,
      traditions: [...new Set(graphics.flatMap((g) => deriveTraditions(g)))],
    });
  }
  return folders.sort((a, b) => a.study.title.localeCompare(b.study.title, "en", { sensitivity: "base" }));
}
