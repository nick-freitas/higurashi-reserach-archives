import * as fs from "fs";
import * as path from "path";
import type { IndexedEntry, Source } from "./types";
import { classifyFilename } from "./classifier";
import { stripTags } from "./strip-tags";

export interface CorpusIndex {
  entries: IndexedEntry[];
  filenames: string[];
  sourceMap: Map<string, Source>;
}

export function parseEntry(
  raw: Record<string, unknown>,
  index: number,
  filename: string
): IndexedEntry | null {
  const type = raw.type as string;
  const source = classifyFilename(filename);

  if (type === "SELECT") return null;
  if (source.type === "meta") return null;

  if (type === "MSGSET" || type === "LOGSET") {
    const rawNew = raw.TextENGNew as string | undefined;
    return {
      entryIndex: index,
      filename,
      source,
      messageId: type === "MSGSET" ? (raw.MessageID as number) : null,
      speakerJPN: (raw.NamesJPN as string) ?? null,
      speakerENG: (raw.NamesENG as string) ?? null,
      textJPN: stripTags((raw.TextJPN as string) ?? ""),
      textENG: stripTags((raw.TextENG as string) ?? ""),
      textENGNew: rawNew ? stripTags(rawNew) : null,
      significantChanges: (raw.significantChanges as boolean) === true,
      changeReason: (raw.changeReason as string) ?? null,
      significance: typeof raw.changeScore === "number" ? raw.changeScore : null,
    };
  }

  if (type === "SAVEINFO") {
    const rawNew = raw.ENGNew as string | undefined;
    return {
      entryIndex: index,
      filename,
      source,
      messageId: null,
      speakerJPN: null,
      speakerENG: null,
      textJPN: stripTags((raw.JPN as string) ?? ""),
      textENG: stripTags((raw.ENG as string) ?? ""),
      textENGNew: rawNew ? stripTags(rawNew) : null,
      significantChanges: (raw.significantChanges as boolean) === true,
      changeReason: (raw.changeReason as string) ?? null,
      significance: typeof raw.changeScore === "number" ? raw.changeScore : null,
    };
  }

  return null;
}

export function buildIndex(corpusDir: string): CorpusIndex {
  const entries: IndexedEntry[] = [];
  const filenames: string[] = [];
  const sourceMap = new Map<string, Source>();

  const absDir = path.resolve(corpusDir);
  const files = fs.readdirSync(absDir).filter((f) => f.endsWith(".json")).sort();

  for (const file of files) {
    const source = classifyFilename(file);
    if (source.type === "meta") continue;

    filenames.push(file);
    sourceMap.set(file, source);

    let raw: unknown;
    try {
      raw = JSON.parse(fs.readFileSync(path.join(absDir, file), "utf-8"));
    } catch (err) {
      console.warn(`Skipping ${file}: ${(err as Error).message}`);
      continue;
    }
    if (!Array.isArray(raw)) continue;

    for (let i = 0; i < raw.length; i++) {
      const entry = parseEntry(raw[i], i, file);
      if (entry) entries.push(entry);
    }
  }

  console.log(
    `Indexed ${entries.length} entries from ${filenames.length} files`
  );
  return { entries, filenames, sourceMap };
}
