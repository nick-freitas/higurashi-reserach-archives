import type { CorpusIndex } from "./indexer";
import type { ArcInfo, ArcEntry, ArcChapter, IndexedEntry } from "./types";

function getArcId(entry: IndexedEntry): string {
  switch (entry.source.type) {
    case "arc":
      return entry.source.arc ?? "unknown";
    case "tips":
      return "tips";
    case "common":
      return "common";
    case "miotsukushi":
      return `miotsukushi_${entry.source.variant ?? "omote"}`;
    case "fragment":
      return `fragment_${(entry.source.letter ?? "").toLowerCase()}`;
    default:
      return "unknown";
  }
}

function getArcName(arcId: string): string {
  if (arcId === "tips") return "Tips";
  if (arcId === "common") return "Common";
  if (arcId.startsWith("miotsukushi_")) {
    const variant = arcId.slice("miotsukushi_".length);
    return `Miotsukushi (${variant.charAt(0).toUpperCase() + variant.slice(1)})`;
  }
  if (arcId.startsWith("fragment_")) {
    const letter = arcId.slice("fragment_".length).toUpperCase();
    return `Fragments ${letter}`;
  }
  return arcId.charAt(0).toUpperCase() + arcId.slice(1);
}

/** For prologue/epilogue arcs, extract the book name from the first SAVEINFO entry */
function getPrologueEpilogueName(index: CorpusIndex, arcId: string): string | null {
  const match = arcId.match(/^book_\d+_(prologue|epilogue)$/);
  if (!match) return null;
  const suffix = match[1] === "prologue" ? "Prologue" : "Epilogue";
  // Find the first entry for this arc — its textENG is the book title
  for (const entry of index.entries) {
    if (getArcId(entry) === arcId && entry.entryIndex === 0) {
      const title = entry.textENG;
      if (title) return `${title} (${suffix})`;
      break;
    }
  }
  return suffix;
}

export function listArcs(index: CorpusIndex, significantOnly?: boolean, scores?: Set<number>): ArcInfo[] {
  const counts = new Map<string, number>();

  for (const entry of index.entries) {
    if (significantOnly && !entry.significantChanges) continue;
    if (scores && !scores.has(entry.significance ?? 0)) continue;
    const id = getArcId(entry);
    counts.set(id, (counts.get(id) ?? 0) + 1);
  }

  const arcs: ArcInfo[] = [];
  for (const [id, entryCount] of counts) {
    const name = getPrologueEpilogueName(index, id) ?? getArcName(id);
    arcs.push({ id, name, entryCount });
  }

  const categoryOrder: Record<string, number> = {
    common: 1,
    tips: 2,
  };

  arcs.sort((a, b) => {
    const aIsFragment = a.id.startsWith("fragment_");
    const bIsFragment = b.id.startsWith("fragment_");
    const aIsMio = a.id.startsWith("miotsukushi_");
    const bIsMio = b.id.startsWith("miotsukushi_");
    const aOrder = categoryOrder[a.id] ?? (aIsFragment ? 3 : aIsMio ? 4 : 0);
    const bOrder = categoryOrder[b.id] ?? (bIsFragment ? 3 : bIsMio ? 4 : 0);
    if (aOrder !== bOrder) return aOrder - bOrder;
    return a.id.localeCompare(b.id);
  });

  return arcs;
}

function getChapterName(filename: string, source: IndexedEntry["source"]): string {
  const name = filename.replace(/\.json$/, "");
  switch (source.type) {
    case "arc": {
      const ch = source.chapter ?? "";
      if (/^\d+$/.test(ch)) return `Chapter ${ch}`;
      if (ch === "end") return "Ending";
      if (ch === "badend") return "Bad End";
      if (ch.startsWith("badend")) return `Bad End ${ch.slice(6)}`;
      if (ch === "afterparty") return "After Party";
      if (ch) return ch.charAt(0).toUpperCase() + ch.slice(1);
      return name;
    }
    case "tips":
      return `Tip #${String(source.number ?? "").padStart(3, "0")}`;
    case "fragment":
      return `Fragment ${source.letter ?? ""}${source.number ?? ""}`;
    case "common":
      return (source.section ?? name).replace(/_/g, " ");
    case "miotsukushi": {
      const ch = source.chapter ?? "";
      if (/^\d+$/.test(ch)) return `Chapter ${ch}`;
      if (ch === "end") return "Ending";
      if (ch.startsWith("badend")) return `Bad End ${ch.slice(6)}`;
      if (ch) return ch.charAt(0).toUpperCase() + ch.slice(1);
      return name;
    }
    default:
      return name;
  }
}

/** Try to extract "#N / Title" from the first few entries of a file */
function extractChapterTitle(entries: IndexedEntry[], filename: string): string | null {
  const fileEntries = entries.filter((e) => e.filename === filename);
  for (let i = 0; i < Math.min(5, fileEntries.length); i++) {
    const match = fileEntries[i].textENG.match(/^#(\d+[A-Z]?)\s*\/\s*(.+)/);
    if (match) {
      return `#${match[1]} / ${match[2]}`;
    }
  }
  return null;
}

/** Extract title and day for common route files */
function extractCommonTitle(entries: IndexedEntry[], filename: string): string | null {
  // Special case for partnerselection
  if (filename === "common_partnerselection.json") return "Partner Selection";

  const fileEntries = entries.filter((e) => e.filename === filename);
  if (fileEntries.length < 2) return null;

  let day: string | null = null;
  let title: string | null = null;

  let label: string | null = null;

  for (let i = 0; i < Math.min(4, fileEntries.length); i++) {
    const text = fileEntries[i].textENG;
    // Match "Day N" or route names like "Mion Route 1", "Rena Route", "Watanagashi Route A"
    const labelMatch = text.match(/^(Day \d+|.+ Route\s*\w*)$/);
    if (labelMatch) {
      label = labelMatch[1];
      continue;
    }
    const titleMatch = text.match(/^(#\d+[A-Z]?\s*\/?\s*.+)/);
    if (titleMatch) {
      title = titleMatch[1];
      break;
    }
  }

  // If no label found from entries, try to extract from filename
  if (!label) {
    const dayMatch = filename.match(/common_day(\d+)/);
    if (dayMatch) {
      label = `Day ${dayMatch[1]}`;
    } else {
      // common_mion1_2.json → Mion Route 1, common_rena_2.json → Rena Route
      const routeMatch = filename.match(/common_(\w+?)(\d*)_\d/);
      if (routeMatch) {
        const name = routeMatch[1].charAt(0).toUpperCase() + routeMatch[1].slice(1);
        const num = routeMatch[2] || "";
        label = num ? `${name} Route ${num}` : `${name} Route`;
      }
    }
  }

  if (title && label) return `${label} - ${title}`;
  if (title) return title;
  return null;
}

/** Extract tip name from first entries */
function extractTipTitle(entries: IndexedEntry[], filename: string, tipNumber: number | string): string | null {
  const fileEntries = entries.filter((e) => e.filename === filename);
  for (let i = 0; i < Math.min(3, fileEntries.length); i++) {
    const text = fileEntries[i].textENG;
    // Skip generic "TIPS" label
    if (text === "TIPS") continue;
    // First non-"TIPS" SAVEINFO-like short text is the tip name
    if (text.length > 0 && text.length < 120 && !text.startsWith("``") && !text.startsWith("From ")) {
      return `#${Number(tipNumber)} ${text}`;
    }
  }
  return `#${Number(tipNumber)}`;
}

/** Arc types that should NOT use standard #N title extraction */
const SKIP_TITLE_EXTRACTION = new Set(["tips", "fragment", "common"]);

/** Arc ID patterns for prologues/epilogues */
function isPrologueOrEpilogue(arcId: string): boolean {
  return /^book_\d+_(prologue|epilogue)$/.test(arcId);
}

export function getArcChapters(index: CorpusIndex, arcId: string, significantOnly?: boolean, scores?: Set<number>): ArcChapter[] | null {
  const chapters = new Map<string, { source: IndexedEntry["source"]; count: number }>();

  for (const entry of index.entries) {
    if (getArcId(entry) !== arcId) continue;
    if (significantOnly && !entry.significantChanges) continue;
    if (scores && !scores.has(entry.significance ?? 0)) continue;
    const existing = chapters.get(entry.filename);
    if (existing) {
      existing.count++;
    } else {
      chapters.set(entry.filename, { source: entry.source, count: 1 });
    }
  }

  if (chapters.size === 0) return null;

  const sourceType = index.entries.find((e) => getArcId(e) === arcId)?.source.type ?? "";
  const isCommon = sourceType === "common";
  const shouldExtract = !SKIP_TITLE_EXTRACTION.has(sourceType) && !isPrologueOrEpilogue(arcId);

  const isTips = sourceType === "tips";

  const result: ArcChapter[] = [];
  for (const [file, { source, count }] of chapters) {
    let name = getChapterName(file, source);
    if (isTips) {
      const extracted = extractTipTitle(index.entries, file, source.number ?? 0);
      if (extracted) name = extracted;
    } else if (isCommon) {
      const extracted = extractCommonTitle(index.entries, file);
      if (extracted) name = extracted;
    } else if (shouldExtract) {
      const extracted = extractChapterTitle(index.entries, file);
      if (extracted) name = extracted;
    }
    result.push({ file, name, entryCount: count });
  }

  // Sort partnerselection to the bottom for common arc
  if (isCommon) {
    result.sort((a, b) => {
      const aIsPS = a.file.includes("partnerselection") ? 1 : 0;
      const bIsPS = b.file.includes("partnerselection") ? 1 : 0;
      return aIsPS - bIsPS;
    });
  }

  return result;
}

export interface ArcEntriesResult {
  arcId: string;
  arcName: string;
  totalEntries: number;
  offset: number;
  limit: number;
  entries: ArcEntry[];
}

export function getSignificantChanges(index: CorpusIndex): ArcEntry[] {
  return index.entries
    .filter((e) => e.significantChanges)
    .map((e) => ({
      file: e.filename,
      index: e.entryIndex,
      messageId: e.messageId,
      speakerJPN: e.speakerJPN,
      speakerENG: e.speakerENG,
      textJPN: e.textJPN,
      textENG: e.textENG,
      textENGNew: e.textENGNew,
      significantChanges: e.significantChanges,
      changeReason: e.changeReason,
      significance: e.significance,
    }));
}

/** Get entries with optional book/arc/file/speaker filters */
export function getFilteredEntries(
  index: CorpusIndex,
  options: { bookArcIds?: string[]; arcId?: string; file?: string; speaker?: string; significantOnly?: boolean; scores?: Set<number> },
  offset: number,
  limit: number,
): ArcEntriesResult {
  const filtered: IndexedEntry[] = [];

  for (const entry of index.entries) {
    if (options.significantOnly && !entry.significantChanges) continue;
    if (options.scores && !options.scores.has(entry.significance ?? 0)) continue;
    if (options.bookArcIds && !options.bookArcIds.includes(getArcId(entry))) continue;
    if (options.arcId && getArcId(entry) !== options.arcId) continue;
    if (options.file && entry.filename !== options.file) continue;
    if (options.speaker && (entry.speakerENG || entry.speakerJPN || "") !== options.speaker) continue;
    filtered.push(entry);
  }

  const paged = filtered.slice(offset, offset + limit);

  return {
    arcId: options.arcId ?? "__all__",
    arcName: options.arcId ? getArcName(options.arcId) : "All",
    totalEntries: filtered.length,
    offset,
    limit,
    entries: paged.map((e) => ({
      file: e.filename,
      index: e.entryIndex,
      messageId: e.messageId,
      speakerJPN: e.speakerJPN,
      speakerENG: e.speakerENG,
      textJPN: e.textJPN,
      textENG: e.textENG,
      textENGNew: e.textENGNew,
      significantChanges: e.significantChanges,
      changeReason: e.changeReason,
      significance: e.significance,
    })),
  };
}

export function getArcEntries(
  index: CorpusIndex,
  arcId: string,
  offset: number,
  limit: number,
  file?: string,
  speaker?: string
): ArcEntriesResult | null {
  const arcEntries: IndexedEntry[] = [];

  for (const entry of index.entries) {
    if (getArcId(entry) !== arcId) continue;
    if (file && entry.filename !== file) continue;
    if (speaker && (entry.speakerENG || entry.speakerJPN || "") !== speaker) continue;
    arcEntries.push(entry);
  }

  if (arcEntries.length === 0) return null;

  const paged = arcEntries.slice(offset, offset + limit);

  return {
    arcId,
    arcName: getArcName(arcId),
    totalEntries: arcEntries.length,
    offset,
    limit,
    entries: paged.map((e) => ({
      file: e.filename,
      index: e.entryIndex,
      messageId: e.messageId,
      speakerJPN: e.speakerJPN,
      speakerENG: e.speakerENG,
      textJPN: e.textJPN,
      textENG: e.textENG,
      textENGNew: e.textENGNew,
      significantChanges: e.significantChanges,
      changeReason: e.changeReason,
      significance: e.significance,
    })),
  };
}
