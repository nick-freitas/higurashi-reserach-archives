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

function getChapterName(filename: string, source: Source): string | null {
  switch (source.type) {
    case "arc":
    case "miotsukushi": {
      const ch = source.chapter ?? "";
      if (ch === "") return null;
      if (ch === "end") return "Ending";
      if (ch === "badend") return "Bad End";
      // Numeric chapter
      const num = parseInt(ch, 10);
      if (!isNaN(num)) return `Chapter ${num}`;
      // Fallback: return as-is with first letter capitalized
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

// ── Main build ────────────────────────────────────────────────────

const GAME_TEXT_DIR = path.resolve(import.meta.dirname ?? __dirname, "..", "game_text");
const DB_PATH = path.resolve(import.meta.dirname ?? __dirname, "..", "public", "higurashi.db");

function main() {
  const startTime = Date.now();

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

  // Read all JSON files
  const files = fs.readdirSync(GAME_TEXT_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  console.log(`Found ${files.length} JSON files in game_text/`);

  let totalEntries = 0;
  let skippedFiles = 0;

  // Wrap everything in a single transaction for performance
  const transaction = db.transaction(() => {
    for (const file of files) {
      const source = classifyFilename(file);

      // Skip meta files (e.g., chapternames.json)
      if (source.type === "meta") {
        skippedFiles++;
        continue;
      }

      const arcId = getArcId(source, file);
      const arcName = getArcName(arcId);
      const chapterName = getChapterName(file, source);
      const filenameNoExt = file.replace(/\.json$/, "");

      const filePath = path.join(GAME_TEXT_DIR, file);
      const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as any[];

      let entryIndex = 0;

      for (const entry of raw) {
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
  console.log(`Entries: ${totalEntries} (skipped ${skippedFiles} meta files)`);
  console.log(`Database: ${DB_PATH} (${sizeMB} MB)`);
}

main();
