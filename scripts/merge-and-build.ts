import fs from "node:fs";
import path from "node:path";
import Database from "better-sqlite3";
import { classifyFilename } from "./classifier";
import { stripTags } from "./strip-tags";
import type { Source } from "./types";

// ── Helper functions ──────────────────────────────────────────────

function getArcId(source: Source, _filename: string): string {
  switch (source.type) {
    case "arc":
      return source.arc ?? "unknown";
    case "tips":
      return "tips";
    case "common":
      return "common";
    case "miotsukushi":
      return `miotsukushi_${source.variant ?? "omote"}`;
    case "fragment":
      return `fragment_${(source.letter ?? "").toLowerCase()}`;
    case "meta":
      return "meta";
  }
}

function getArcName(arcId: string): string {
  if (arcId === "tips") return "Tips";
  if (arcId === "common") return "Common";

  const mioMatch = arcId.match(/^miotsukushi_(omote|ura)$/);
  if (mioMatch) {
    const variant = mioMatch[1];
    return `Miotsukushi (${variant.charAt(0).toUpperCase() + variant.slice(1)})`;
  }

  const fragMatch = arcId.match(/^fragment_([a-z])$/);
  if (fragMatch) {
    return `Fragments ${fragMatch[1].toUpperCase()}`;
  }

  // Default: capitalize first letter
  return arcId.charAt(0).toUpperCase() + arcId.slice(1);
}

function getBasicChapterName(filename: string, source: Source): string | null {
  switch (source.type) {
    case "arc":
    case "miotsukushi": {
      const ch = source.chapter ?? "";
      if (ch === "") return null;
      if (ch === "end") return "Ending";
      if (ch === "badend") return "Bad End";
      if (ch.startsWith("badend")) return `Bad End ${ch.slice(6)}`;
      if (ch === "afterparty") return "After Party";
      const num = parseInt(ch, 10);
      if (!isNaN(num)) return `Chapter ${num}`;
      return ch.charAt(0).toUpperCase() + ch.slice(1);
    }
    case "tips": {
      const n = source.number;
      if (n == null) return null;
      return `Tip #${String(n).padStart(3, "0")}`;
    }
    case "fragment": {
      const letter = source.letter ?? "";
      const num = source.number ?? "";
      return `Fragment ${letter}${num}`;
    }
    case "common": {
      const section = source.section ?? "";
      if (!section) return null;
      return section.replace(/_/g, " ");
    }
    case "meta":
      return null;
  }
}

/** Extract "#N / Title" from the first few entries of a file */
function extractChapterTitle(entries: any[]): string | null {
  for (let i = 0; i < Math.min(5, entries.length); i++) {
    const text = stripTags(entries[i].TextENG ?? entries[i].ENG ?? "");
    const match = text.match(/^#(\d+[A-Z]?)\s*\/\s*(.+)/);
    if (match) return `#${match[1]} / ${match[2]}`;
  }
  return null;
}

/** Extract title and day for common route files */
function extractCommonTitle(entries: any[], filename: string): string | null {
  if (filename === "common_partnerselection.json") return "Partner Selection";

  let label: string | null = null;
  let title: string | null = null;

  for (let i = 0; i < Math.min(4, entries.length); i++) {
    const text = stripTags(entries[i].TextENG ?? entries[i].ENG ?? "");
    const labelMatch = text.match(/^(Day \d+|.+ Route\s*\w*)$/);
    if (labelMatch) { label = labelMatch[1]; continue; }
    const titleMatch = text.match(/^(#\d+[A-Z]?\s*\/?\s*.+)/);
    if (titleMatch) { title = titleMatch[1]; break; }
  }

  if (!label) {
    const dayMatch = filename.match(/common_day(\d+)/);
    if (dayMatch) {
      label = `Day ${dayMatch[1]}`;
    } else {
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
function extractTipTitle(entries: any[], tipNumber: number | string): string | null {
  for (let i = 0; i < Math.min(3, entries.length); i++) {
    const text = stripTags(entries[i].TextENG ?? entries[i].ENG ?? entries[i].JPN ?? "");
    if (text === "TIPS") continue;
    if (text.length > 0 && text.length < 120 && !text.startsWith("``") && !text.startsWith("From ")) {
      return `#${Number(tipNumber)} ${text}`;
    }
  }
  return `#${Number(tipNumber)}`;
}

/** Get prologue/epilogue display name from first SAVEINFO entry */
function extractPrologueEpilogueName(entries: any[], arcId: string): string | null {
  const match = arcId.match(/^book_\d+_(prologue|epilogue)$/);
  if (!match) return null;
  const suffix = match[1] === "prologue" ? "Prologue" : "Epilogue";
  for (const entry of entries) {
    if (entry.type === "SAVEINFO") {
      const title = stripTags(entry.ENG ?? "");
      if (title) return `${title} (${suffix})`;
      break;
    }
  }
  return suffix;
}

/** Arc types that should NOT use standard #N title extraction */
const SKIP_TITLE_EXTRACTION = new Set(["tips", "fragment", "common"]);

function getChapterName(filename: string, source: Source, entries: any[]): string | null {
  const basic = getBasicChapterName(filename, source);

  if (source.type === "tips") {
    return extractTipTitle(entries, source.number ?? 0);
  }
  if (source.type === "common") {
    return extractCommonTitle(entries, filename) ?? basic;
  }
  if (!SKIP_TITLE_EXTRACTION.has(source.type)) {
    const arcId = getArcId(source, filename);
    if (/^book_\d+_(prologue|epilogue)$/.test(arcId)) {
      return basic; // prologues/epilogues use basic name
    }
    return extractChapterTitle(entries) ?? basic;
  }
  return basic;
}

function getArcNameWithEntries(arcId: string, entries: any[]): string {
  const prologueName = extractPrologueEpilogueName(entries, arcId);
  if (prologueName) return prologueName;
  return getArcName(arcId);
}

// ── Overlay types ─────────────────────────────────────────────────

interface OverlayEntry {
  index: number;
  MessageID?: number;
  TextENGNew?: string;
  ENGNew?: string;
  significantChanges?: boolean;
  changeReason?: string;
  changeScore?: number;
}

// ── Merge logic ───────────────────────────────────────────────────

function mergeOverlays(sourceEntries: any[], overlayEntries: OverlayEntry[], filename: string): any[] {
  // Clone so we don't mutate the originals
  const merged = sourceEntries.map((e) => ({ ...e }));

  for (const overlay of overlayEntries) {
    const idx = overlay.index;

    if (idx < 0 || idx >= merged.length) {
      console.warn(`[${filename}] overlay index ${idx} out of bounds (source has ${merged.length} entries), skipping`);
      continue;
    }

    const target = merged[idx];

    // For MSGSET entries, verify MessageID matches if present in overlay
    if (overlay.MessageID != null && target.type === "MSGSET") {
      if (target.MessageID !== overlay.MessageID) {
        console.warn(
          `[${filename}] MessageID mismatch at index ${idx}: source=${target.MessageID}, overlay=${overlay.MessageID}, skipping`
        );
        continue;
      }
    }

    // Merge overlay fields into the source entry
    if (overlay.TextENGNew !== undefined) target.TextENGNew = overlay.TextENGNew;
    if (overlay.ENGNew !== undefined) target.ENGNew = overlay.ENGNew;
    if (overlay.significantChanges !== undefined) target.significantChanges = overlay.significantChanges;
    if (overlay.changeReason !== undefined) target.changeReason = overlay.changeReason;
    if (overlay.changeScore !== undefined) target.changeScore = overlay.changeScore;
  }

  return merged;
}

// ── Main build ────────────────────────────────────────────────────

const scriptDir = import.meta.dirname ?? __dirname;
const SOURCE_DIR = path.resolve(process.env.SOURCE_DIR ?? path.join(scriptDir, "..", "upstream"));
const OVERLAYS_DIR = path.resolve(scriptDir, "..", "overlays");
const DB_PATH = path.resolve(scriptDir, "..", "public", "higurashi.db");

function main() {
  const startTime = Date.now();

  console.log(`Source dir:   ${SOURCE_DIR}`);
  console.log(`Overlays dir: ${OVERLAYS_DIR}`);
  console.log(`Output:       ${DB_PATH}`);

  if (!fs.existsSync(SOURCE_DIR)) {
    console.error(`Source directory not found: ${SOURCE_DIR}`);
    console.error(`Set SOURCE_DIR env var or clone upstream repo to ./upstream`);
    process.exit(1);
  }

  const overlaysExist = fs.existsSync(OVERLAYS_DIR);
  if (!overlaysExist) {
    console.log(`No overlays directory found — building from source only`);
  }

  // Build a set of overlay filenames for quick lookup
  const overlayFiles = new Set<string>();
  if (overlaysExist) {
    for (const f of fs.readdirSync(OVERLAYS_DIR)) {
      if (f.endsWith(".json")) overlayFiles.add(f);
    }
    console.log(`Found ${overlayFiles.size} overlay files`);
  }

  // Ensure output directory exists
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

  // Remove existing DB if present
  if (fs.existsSync(DB_PATH)) {
    fs.unlinkSync(DB_PATH);
  }

  // Open database
  const db = new Database(DB_PATH);
  db.pragma("journal_mode = OFF");
  db.pragma("synchronous = OFF");

  // Create tables
  db.exec(`
    CREATE TABLE entries (
      id INTEGER PRIMARY KEY,
      filename TEXT NOT NULL,
      entry_index INTEGER NOT NULL,
      message_id INTEGER,
      source_type TEXT NOT NULL,
      arc_id TEXT NOT NULL,
      arc_name TEXT NOT NULL,
      chapter_name TEXT,
      speaker_jpn TEXT,
      speaker_eng TEXT,
      text_jpn TEXT NOT NULL,
      text_eng TEXT NOT NULL,
      text_eng_new TEXT,
      significant_changes INTEGER NOT NULL DEFAULT 0,
      change_reason TEXT,
      significance INTEGER
    );
  `);

  db.exec(`
    CREATE VIRTUAL TABLE entries_fts USING fts5(
      text_jpn, text_eng, speaker_jpn, speaker_eng,
      content=entries, content_rowid=id
    );
  `);

  // Prepare insert statements
  const insertEntry = db.prepare(`
    INSERT INTO entries (
      filename, entry_index, message_id, source_type, arc_id, arc_name,
      chapter_name, speaker_jpn, speaker_eng, text_jpn, text_eng,
      text_eng_new, significant_changes, change_reason, significance
    ) VALUES (
      @filename, @entryIndex, @messageId, @sourceType, @arcId, @arcName,
      @chapterName, @speakerJpn, @speakerEng, @textJpn, @textEng,
      @textEngNew, @significantChanges, @changeReason, @significance
    )
  `);

  const insertFts = db.prepare(`
    INSERT INTO entries_fts (rowid, text_jpn, text_eng, speaker_jpn, speaker_eng)
    VALUES (@id, @textJpn, @textEng, @speakerJpn, @speakerEng)
  `);

  // Read all JSON files from source
  const files = fs.readdirSync(SOURCE_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  console.log(`Found ${files.length} source JSON files`);

  let totalEntries = 0;
  let skippedFiles = 0;
  let mergedFiles = 0;

  // Wrap everything in a single transaction for performance
  const transaction = db.transaction(() => {
    for (const file of files) {
      const source = classifyFilename(file);

      // Skip meta files (e.g., chapternames.json)
      if (source.type === "meta") {
        skippedFiles++;
        continue;
      }

      const filenameNoExt = file.replace(/\.json$/, "");

      // Read source entries
      const sourcePath = path.join(SOURCE_DIR, file);
      let entries = JSON.parse(fs.readFileSync(sourcePath, "utf-8")) as any[];

      // Check for overlay and merge if present
      if (overlayFiles.has(file)) {
        const overlayPath = path.join(OVERLAYS_DIR, file);
        const overlayData = JSON.parse(fs.readFileSync(overlayPath, "utf-8")) as OverlayEntry[];
        entries = mergeOverlays(entries, overlayData, file);
        mergedFiles++;
      }

      const arcId = getArcId(source, file);
      const arcName = getArcNameWithEntries(arcId, entries);
      const chapterName = getChapterName(file, source, entries);

      let entryIndex = 0;

      for (const entry of entries) {
        const type = entry.type as string;

        let speakerJpn: string | null = null;
        let speakerEng: string | null = null;
        let textJpn: string;
        let textEng: string;
        let textEngNew: string | null = null;
        let messageId: number | null = null;

        if (type === "MSGSET" || type === "LOGSET") {
          speakerJpn = entry.NamesJPN ?? null;
          speakerEng = entry.NamesENG ?? null;
          textJpn = stripTags(entry.TextJPN ?? "");
          textEng = stripTags(entry.TextENG ?? "");
          textEngNew = entry.TextENGNew ? stripTags(entry.TextENGNew) : null;
          messageId = type === "MSGSET" ? entry.MessageID : null;
        } else if (type === "SAVEINFO") {
          textJpn = stripTags(entry.JPN ?? "");
          textEng = stripTags(entry.ENG ?? "");
          textEngNew = entry.ENGNew ? stripTags(entry.ENGNew) : null;
        } else {
          // Skip SELECT and any other types
          continue;
        }

        const significantChanges = entry.significantChanges === true ? 1 : 0;
        const changeReason = entry.changeReason ?? null;
        const significance = typeof entry.changeScore === "number" ? entry.changeScore : null;

        const result = insertEntry.run({
          filename: filenameNoExt,
          entryIndex,
          messageId,
          sourceType: source.type,
          arcId,
          arcName,
          chapterName,
          speakerJpn,
          speakerEng,
          textJpn,
          textEng,
          textEngNew,
          significantChanges,
          changeReason,
          significance,
        });

        insertFts.run({
          id: result.lastInsertRowid,
          textJpn,
          textEng,
          speakerJpn: speakerJpn ?? "",
          speakerEng: speakerEng ?? "",
        });

        entryIndex++;
        totalEntries++;
      }
    }
  });

  transaction();

  // Create indexes after all inserts
  console.log("Creating indexes...");
  db.exec(`CREATE INDEX idx_entries_arc_id ON entries(arc_id);`);
  db.exec(`CREATE INDEX idx_entries_filename ON entries(filename);`);
  db.exec(`CREATE INDEX idx_entries_source_type ON entries(source_type);`);
  db.exec(`CREATE INDEX idx_entries_significant ON entries(significant_changes) WHERE significant_changes = 1;`);
  db.exec(`CREATE INDEX idx_entries_speaker_eng ON entries(speaker_eng) WHERE speaker_eng IS NOT NULL;`);

  db.close();

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  const fileSize = fs.statSync(DB_PATH).size;
  const sizeMB = (fileSize / (1024 * 1024)).toFixed(1);

  console.log(`Done in ${elapsed}s`);
  console.log(`Entries: ${totalEntries} (skipped ${skippedFiles} meta files, merged ${mergedFiles} overlay files)`);
  console.log(`Database: ${DB_PATH} (${sizeMB} MB)`);
}

main();
