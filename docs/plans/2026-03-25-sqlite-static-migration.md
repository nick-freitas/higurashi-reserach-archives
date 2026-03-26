# SQLite Static Site Migration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Express server with a pre-built SQLite database queried client-side via sql.js, enabling GitHub Pages hosting as a fully static site.

**Architecture:** A build-time Node script reads all JSON files from `game_text/`, processes entries (classify, strip tags, extract names), and writes a single `public/higurashi.db` SQLite file with FTS5 indexes. The React frontend loads this DB via sql.js (WASM) at startup and runs all queries locally. Annotations use localStorage.

**Tech Stack:** better-sqlite3 (build-time), sql.js (client-side WASM), Vite, React, vitest

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `scripts/build-db.ts` | Build-time: reads game_text/, writes public/higurashi.db |
| Create | `src/db.ts` | Client-side DB wrapper: load sql.js, fetch DB, expose query helpers |
| Create | `src/__tests__/db.test.ts` | Tests for db query helpers |
| Modify | `src/App.tsx` | Replace all /api fetches with db.ts calls, remove furigana/server state |
| Modify | `src/types.ts` | Remove FuriganaRequest/Response, add Annotation localStorage types |
| Modify | `src/components/DetailPanel.tsx` | Remove furigana props, annotations via localStorage |
| Modify | `src/components/KWICResults.tsx` | Remove furigana props |
| Modify | `package.json` | Add better-sqlite3, sql.js; remove express/tsx/concurrently/claude-agent-sdk; add build:db script |
| Modify | `vite.config.ts` | Remove proxy config |
| Modify | `index.html` | Add sql.js WASM loading hint |
| Modify | `.gitignore` | Add game_text/, public/higurashi.db |
| Modify | `tsconfig.node.json` | Include scripts/ |
| Delete | `server/` | Entire directory |
| Delete | `data/` | No longer needed |
| Delete | `Caddyfile` | No longer needed |
| Delete | `tsconfig.server.json` | No longer needed |
| Keep   | `server/classifier.ts` → `scripts/classifier.ts` | Reuse classification logic in build script |
| Keep   | `server/strip-tags.ts` → `scripts/strip-tags.ts` | Reuse tag stripping in build script |

---

### Task 1: Project setup — dependencies, gitignore, cleanup

**Files:**
- Modify: `package.json`
- Modify: `.gitignore`
- Modify: `vite.config.ts`
- Modify: `tsconfig.node.json`
- Delete: `server/`, `data/`, `Caddyfile`, `tsconfig.server.json`
- Create: `scripts/classifier.ts` (copy from server/)
- Create: `scripts/strip-tags.ts` (copy from server/)

- [ ] **Step 1: Copy reusable server modules to scripts/**

```bash
cp server/classifier.ts scripts/classifier.ts
cp server/strip-tags.ts scripts/strip-tags.ts
```

Update imports in both files: they're self-contained, but `classifier.ts` imports `Source` from `./types`. Create a minimal `scripts/types.ts`:

```ts
export interface Source {
  type: "arc" | "tips" | "fragment" | "common" | "miotsukushi" | "meta";
  arc?: string;
  chapter?: string;
  number?: number | string;
  letter?: string;
  section?: string;
  variant?: "omote" | "ura";
}
```

- [ ] **Step 2: Delete server code and unused files**

```bash
rm -rf server/ data/ Caddyfile tsconfig.server.json
```

- [ ] **Step 3: Update package.json**

Remove dependencies: `express`, `@anthropic-ai/claude-agent-sdk`
Remove devDependencies: `@types/express`, `concurrently`, `tsx`
Add dependencies: `sql.js`
Add devDependencies: `better-sqlite3`, `@types/better-sqlite3`

Update scripts:
```json
{
  "scripts": {
    "dev": "vite",
    "build:db": "tsx scripts/build-db.ts",
    "build": "npm run build:db && tsc -b && vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

Note: keep `tsx` as a devDependency (needed to run build-db.ts).

- [ ] **Step 4: Update .gitignore**

Add:
```
game_text/
public/higurashi.db
```

- [ ] **Step 5: Update vite.config.ts**

Remove the `server.proxy` block (no more API proxy). Remove `server.port`, `server.strictPort`, and `server.allowedHosts` if only used for local dev with Caddy:

```ts
/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

- [ ] **Step 6: Update tsconfig.node.json**

Add `scripts/` to the include array so `tsx` can run the build script with proper type checking.

- [ ] **Step 7: Run npm install**

```bash
npm install
```

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "chore: remove server, set up for static SQLite migration"
```

---

### Task 2: Build script — generate SQLite database from game_text/

**Files:**
- Create: `scripts/build-db.ts`
- Test: manually verify output

This is the core preprocessing step. It reads all JSON files, processes every entry using the same logic the server indexer used, and writes a SQLite database with FTS5 indexes.

- [ ] **Step 1: Create scripts/build-db.ts**

```ts
import Database from "better-sqlite3";
import * as fs from "fs";
import * as path from "path";
import { classifyFilename } from "./classifier";
import { stripTags } from "./strip-tags";
import type { Source } from "./types";

const GAME_TEXT_DIR = path.resolve(import.meta.dirname, "../game_text");
const OUTPUT_PATH = path.resolve(import.meta.dirname, "../public/higurashi.db");

function getArcId(source: Source, filename: string): string {
  switch (source.type) {
    case "arc": return source.arc ?? "unknown";
    case "tips": return "tips";
    case "common": return "common";
    case "miotsukushi": return `miotsukushi_${source.variant ?? "omote"}`;
    case "fragment": return `fragment_${(source.letter ?? "").toLowerCase()}`;
    default: return "unknown";
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

function getChapterName(filename: string, source: Source): string {
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
    case "tips": return `Tip #${String(source.number ?? "").padStart(3, "0")}`;
    case "fragment": return `Fragment ${source.letter ?? ""}${source.number ?? ""}`;
    case "common": return (source.section ?? name).replace(/_/g, " ");
    case "miotsukushi": {
      const ch = source.chapter ?? "";
      if (/^\d+$/.test(ch)) return `Chapter ${ch}`;
      if (ch === "end") return "Ending";
      if (ch.startsWith("badend")) return `Bad End ${ch.slice(6)}`;
      if (ch) return ch.charAt(0).toUpperCase() + ch.slice(1);
      return name;
    }
    default: return name;
  }
}

// --- Main ---

console.log(`Reading JSON files from ${GAME_TEXT_DIR}...`);

const files = fs.readdirSync(GAME_TEXT_DIR).filter(f => f.endsWith(".json")).sort();
console.log(`Found ${files.length} JSON files`);

fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
if (fs.existsSync(OUTPUT_PATH)) fs.unlinkSync(OUTPUT_PATH);

const db = new Database(OUTPUT_PATH);
db.pragma("journal_mode = OFF");
db.pragma("synchronous = OFF");

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

  CREATE VIRTUAL TABLE entries_fts USING fts5(
    text_jpn, text_eng, speaker_jpn, speaker_eng,
    content=entries, content_rowid=id
  );
`);

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

let totalEntries = 0;

const insertAll = db.transaction(() => {
  for (const file of files) {
    const source = classifyFilename(file);
    if (source.type === "meta") continue;

    let raw: unknown;
    try {
      raw = JSON.parse(fs.readFileSync(path.join(GAME_TEXT_DIR, file), "utf-8"));
    } catch (err) {
      console.warn(`Skipping ${file}: ${(err as Error).message}`);
      continue;
    }
    if (!Array.isArray(raw)) continue;

    const arcId = getArcId(source, file);
    const arcName = getArcName(arcId);
    const chapterName = getChapterName(file, source);

    for (let i = 0; i < raw.length; i++) {
      const r = raw[i] as Record<string, unknown>;
      const type = r.type as string;

      if (type === "SELECT" || source.type === "meta") continue;

      let speakerJpn: string | null = null;
      let speakerEng: string | null = null;
      let textJpn = "";
      let textEng = "";
      let textEngNew: string | null = null;
      let messageId: number | null = null;

      if (type === "MSGSET" || type === "LOGSET") {
        speakerJpn = (r.NamesJPN as string) ?? null;
        speakerEng = (r.NamesENG as string) ?? null;
        textJpn = stripTags((r.TextJPN as string) ?? "");
        textEng = stripTags((r.TextENG as string) ?? "");
        const rawNew = r.TextENGNew as string | undefined;
        textEngNew = rawNew ? stripTags(rawNew) : null;
        messageId = type === "MSGSET" ? (r.MessageID as number) : null;
      } else if (type === "SAVEINFO") {
        textJpn = stripTags((r.JPN as string) ?? "");
        textEng = stripTags((r.ENG as string) ?? "");
        const rawNew = r.ENGNew as string | undefined;
        textEngNew = rawNew ? stripTags(rawNew) : null;
      } else {
        continue;
      }

      const result = insertEntry.run({
        filename: file,
        entryIndex: i,
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
        significantChanges: (r.significantChanges === true) ? 1 : 0,
        changeReason: (r.changeReason as string) ?? null,
        significance: typeof r.changeScore === "number" ? r.changeScore : null,
      });

      insertFts.run({
        id: result.lastInsertRowid,
        textJpn,
        textEng,
        speakerJpn: speakerJpn ?? "",
        speakerEng: speakerEng ?? "",
      });

      totalEntries++;
    }
  }
});

insertAll();

// Create indexes for common queries
db.exec(`
  CREATE INDEX idx_entries_arc_id ON entries(arc_id);
  CREATE INDEX idx_entries_filename ON entries(filename);
  CREATE INDEX idx_entries_source_type ON entries(source_type);
  CREATE INDEX idx_entries_significant ON entries(significant_changes) WHERE significant_changes = 1;
  CREATE INDEX idx_entries_speaker_eng ON entries(speaker_eng) WHERE speaker_eng IS NOT NULL;
`);

db.close();

const stats = fs.statSync(OUTPUT_PATH);
console.log(`Done. ${totalEntries} entries from ${files.length} files.`);
console.log(`Database: ${OUTPUT_PATH} (${(stats.size / 1024 / 1024).toFixed(1)} MB)`);
```

- [ ] **Step 2: Ensure public/ directory exists and run build:db**

```bash
mkdir -p public
npx tsx scripts/build-db.ts
```

Expected: prints entry count and file size. Should produce ~20-30MB file.

- [ ] **Step 3: Verify DB contents**

```bash
sqlite3 public/higurashi.db "SELECT COUNT(*) FROM entries;"
sqlite3 public/higurashi.db "SELECT DISTINCT arc_id FROM entries ORDER BY arc_id LIMIT 10;"
sqlite3 public/higurashi.db "SELECT * FROM entries_fts WHERE entries_fts MATCH 'Rena' LIMIT 3;"
```

- [ ] **Step 4: Commit**

```bash
git add scripts/ public/.gitkeep
git commit -m "feat: add build-db script to generate SQLite from game_text"
```

Note: `public/higurashi.db` is gitignored — only the script is committed.

---

### Task 3: Client-side DB wrapper — sql.js query layer

**Files:**
- Create: `src/db.ts`
- Create: `src/__tests__/db.test.ts`

This module loads the SQLite database via sql.js and exposes typed query functions that replace all the former API endpoints.

- [ ] **Step 1: Write src/db.ts**

```ts
import initSqlJs, { type Database } from "sql.js";

let db: Database | null = null;

export async function initDb(): Promise<void> {
  const SQL = await initSqlJs({
    locateFile: (file: string) => `https://sql.js.org/dist/${file}`,
  });
  const response = await fetch("/higurashi.db");
  const buffer = await response.arrayBuffer();
  db = new SQL.Database(new Uint8Array(buffer));
}

function getDb(): Database {
  if (!db) throw new Error("Database not initialized. Call initDb() first.");
  return db;
}

// --- Query helpers ---

export interface EntryRow {
  id: number;
  filename: string;
  entry_index: number;
  message_id: number | null;
  source_type: string;
  arc_id: string;
  arc_name: string;
  chapter_name: string | null;
  speaker_jpn: string | null;
  speaker_eng: string | null;
  text_jpn: string;
  text_eng: string;
  text_eng_new: string | null;
  significant_changes: number;
  change_reason: string | null;
  significance: number | null;
}

export interface ArcInfo {
  id: string;
  name: string;
  entryCount: number;
}

export interface ChapterInfo {
  file: string;
  name: string;
  entryCount: number;
}

export interface Speaker {
  name: string;
  count: number;
}

export interface SearchMatch {
  entry: EntryRow;
  matchField: "text_jpn" | "text_eng";
  snippet: string;
}

export function getStatus(): { entries: number; files: number } {
  const d = getDb();
  const entries = (d.exec("SELECT COUNT(*) as c FROM entries")[0].values[0][0] as number);
  const files = (d.exec("SELECT COUNT(DISTINCT filename) as c FROM entries")[0].values[0][0] as number);
  return { entries, files };
}

export function listArcs(significantOnly?: boolean, scores?: Set<number>): ArcInfo[] {
  const d = getDb();
  let sql = "SELECT arc_id, arc_name, COUNT(*) as cnt FROM entries";
  const conditions: string[] = [];
  if (significantOnly) conditions.push("significant_changes = 1");
  if (scores && scores.size > 0 && scores.size < 5) {
    conditions.push(`significance IN (${Array.from(scores).join(",")})`);
  }
  if (conditions.length) sql += " WHERE " + conditions.join(" AND ");
  sql += " GROUP BY arc_id, arc_name ORDER BY arc_id";

  const results = d.exec(sql);
  if (!results.length) return [];
  return results[0].values.map(row => ({
    id: row[0] as string,
    name: row[1] as string,
    entryCount: row[2] as number,
  }));
}

export function getArcChapters(
  arcId: string,
  significantOnly?: boolean,
  scores?: Set<number>
): ChapterInfo[] {
  const d = getDb();
  let sql = "SELECT filename, chapter_name, COUNT(*) as cnt FROM entries WHERE arc_id = ?";
  const params: (string | number)[] = [arcId];
  if (significantOnly) sql += " AND significant_changes = 1";
  if (scores && scores.size > 0 && scores.size < 5) {
    sql += ` AND significance IN (${Array.from(scores).join(",")})`;
  }
  sql += " GROUP BY filename, chapter_name ORDER BY filename";

  const stmt = d.prepare(sql);
  stmt.bind(params);
  const rows: ChapterInfo[] = [];
  while (stmt.step()) {
    const r = stmt.getAsObject();
    rows.push({
      file: r.filename as string,
      name: r.chapter_name as string,
      entryCount: r.cnt as number,
    });
  }
  stmt.free();
  return rows;
}

export function getEntries(options: {
  arcId?: string;
  file?: string;
  speaker?: string;
  bookArcIds?: string[];
  significantOnly?: boolean;
  scores?: Set<number>;
  offset?: number;
  limit?: number;
}): { entries: EntryRow[]; total: number } {
  const d = getDb();
  const conditions: string[] = [];
  const params: (string | number)[] = [];

  if (options.arcId) {
    conditions.push("arc_id = ?");
    params.push(options.arcId);
  }
  if (options.file) {
    conditions.push("filename = ?");
    params.push(options.file);
  }
  if (options.speaker) {
    conditions.push("(speaker_eng = ? OR speaker_jpn = ?)");
    params.push(options.speaker, options.speaker);
  }
  if (options.bookArcIds && options.bookArcIds.length > 0) {
    conditions.push(`arc_id IN (${options.bookArcIds.map(() => "?").join(",")})`);
    params.push(...options.bookArcIds);
  }
  if (options.significantOnly) {
    conditions.push("significant_changes = 1");
  }
  if (options.scores && options.scores.size > 0 && options.scores.size < 5) {
    conditions.push(`significance IN (${Array.from(options.scores).join(",")})`);
  }

  const where = conditions.length ? " WHERE " + conditions.join(" AND ") : "";
  const countResult = d.exec(`SELECT COUNT(*) FROM entries${where}`, params);
  const total = countResult.length ? (countResult[0].values[0][0] as number) : 0;

  const offset = options.offset ?? 0;
  const limit = Math.min(options.limit ?? 50, 500);

  const stmt = d.prepare(
    `SELECT * FROM entries${where} ORDER BY id LIMIT ? OFFSET ?`
  );
  stmt.bind([...params, limit, offset]);
  const entries: EntryRow[] = [];
  while (stmt.step()) {
    entries.push(stmt.getAsObject() as unknown as EntryRow);
  }
  stmt.free();
  return { entries, total };
}

export function search(
  query: string,
  lang: "jp" | "en" | "both",
  offset: number = 0,
  limit: number = 100
): { entries: EntryRow[]; total: number; query: string } {
  if (!query) return { entries: [], total: 0, query };
  const d = getDb();

  // Build FTS match expression based on language
  let ftsMatch: string;
  if (lang === "jp") {
    ftsMatch = `{text_jpn speaker_jpn} : ${JSON.stringify(query)}`;
  } else if (lang === "en") {
    ftsMatch = `{text_eng speaker_eng} : ${JSON.stringify(query)}`;
  } else {
    ftsMatch = JSON.stringify(query);
  }

  const countSql = `SELECT COUNT(*) FROM entries_fts WHERE entries_fts MATCH ?`;
  const countResult = d.exec(countSql, [ftsMatch]);
  const total = countResult.length ? (countResult[0].values[0][0] as number) : 0;

  const sql = `
    SELECT e.* FROM entries e
    JOIN entries_fts fts ON e.id = fts.rowid
    WHERE entries_fts MATCH ?
    ORDER BY e.id
    LIMIT ? OFFSET ?
  `;
  const stmt = d.prepare(sql);
  stmt.bind([ftsMatch, Math.min(limit, 500), offset]);
  const entries: EntryRow[] = [];
  while (stmt.step()) {
    entries.push(stmt.getAsObject() as unknown as EntryRow);
  }
  stmt.free();
  return { entries, total, query };
}

export function getContext(
  filename: string,
  entryIndex: number,
  radius: number = 2
): EntryRow[] {
  const d = getDb();
  // Get entries around the target in the same file
  const sql = `
    SELECT * FROM entries
    WHERE filename = ? AND entry_index BETWEEN ? AND ?
    ORDER BY entry_index
  `;
  const stmt = d.prepare(sql);
  stmt.bind([filename, entryIndex - radius, entryIndex + radius]);
  const entries: EntryRow[] = [];
  while (stmt.step()) {
    entries.push(stmt.getAsObject() as unknown as EntryRow);
  }
  stmt.free();
  return entries;
}

export function getSpeakers(): Speaker[] {
  const d = getDb();
  const sql = `
    SELECT COALESCE(speaker_eng, speaker_jpn) as name, COUNT(*) as cnt
    FROM entries
    WHERE speaker_eng IS NOT NULL OR speaker_jpn IS NOT NULL
    GROUP BY name
    ORDER BY cnt DESC
  `;
  const results = d.exec(sql);
  if (!results.length) return [];
  return results[0].values.map(row => ({
    name: row[0] as string,
    count: row[1] as number,
  }));
}

// --- Annotations (localStorage) ---

const ANNOTATIONS_KEY = "higurashi-annotations";

export interface Annotation {
  editedENG?: string;
  notes?: string;
}

export type AnnotationsMap = Record<string, Annotation>;

export function loadAnnotations(): AnnotationsMap {
  try {
    const raw = localStorage.getItem(ANNOTATIONS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function saveAnnotation(key: string, data: Partial<Annotation>): AnnotationsMap {
  const annotations = loadAnnotations();
  annotations[key] = { ...annotations[key], ...data };
  localStorage.setItem(ANNOTATIONS_KEY, JSON.stringify(annotations));
  return annotations;
}
```

- [ ] **Step 2: Write src/__tests__/db.test.ts**

Testing the annotations helpers (localStorage). The SQL query functions are integration-level and will be validated by running the app against the built DB.

```ts
import { describe, it, expect, beforeEach } from "vitest";
import { loadAnnotations, saveAnnotation } from "../db";

describe("annotations (localStorage)", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns empty object when no annotations exist", () => {
    expect(loadAnnotations()).toEqual({});
  });

  it("saves and loads an annotation", () => {
    saveAnnotation("file.json:123", { notes: "test note" });
    const loaded = loadAnnotations();
    expect(loaded["file.json:123"]).toEqual({ notes: "test note" });
  });

  it("merges annotation fields", () => {
    saveAnnotation("key", { notes: "a" });
    saveAnnotation("key", { editedENG: "b" });
    const loaded = loadAnnotations();
    expect(loaded["key"]).toEqual({ notes: "a", editedENG: "b" });
  });
});
```

- [ ] **Step 3: Run tests**

```bash
npm test
```

Expected: annotation tests pass. Existing tests that import from `server/` will fail — delete those:

```bash
rm -rf src/__tests__/parseRuby.test.tsx
```

(parseRuby was for furigana rendering — no longer needed.)

Also delete `src/utils/` if it only contains parseRuby:

```bash
rm -rf src/utils/
```

- [ ] **Step 4: Commit**

```bash
git add src/db.ts src/__tests__/db.test.ts
git commit -m "feat: add client-side SQLite query layer and annotation helpers"
```

---

### Task 4: Refactor frontend — replace API calls with db.ts

**Files:**
- Modify: `src/App.tsx`
- Modify: `src/types.ts`
- Modify: `src/components/DetailPanel.tsx`
- Modify: `src/components/KWICResults.tsx`
- Delete: `src/utils/` (parseRuby — furigana)
- Delete: `src/__tests__/parseRuby.test.tsx`

This is the largest task. The core change: every `fetch("/api/...")` call becomes a synchronous or async call to a function in `db.ts`.

- [ ] **Step 1: Clean up src/types.ts**

Remove `FuriganaRequest`, `FuriganaResponse`. Remove `furiganaJPN` from `Annotation` type. The canonical Annotation type now lives in `db.ts` — update imports throughout.

```ts
// Remove these interfaces:
// - FuriganaRequest
// - FuriganaResponse
// - Annotation (moved to db.ts)
// - AnnotationsMap (moved to db.ts)
```

Keep: `Source`, `SearchHit`, `SearchGroup`, `SearchResponse`, `ArcInfo`, `ArcEntry`, `ArcChapter`, `ArcChaptersResponse`, `ArcEntriesResponse`, `SelectedEntry`

- [ ] **Step 2: Refactor App.tsx**

Key changes:
1. Replace `serverReady` polling with `initDb()` call on mount
2. Replace all `fetch("/api/...")` calls with `db.ts` function calls
3. Remove `hasFurigana`, `furiganaLoading`, `handleRequestFurigana`
4. Annotations: use `loadAnnotations()` / `saveAnnotation()` from db.ts instead of fetch
5. Convert async fetches to synchronous db calls where possible (db queries are fast since it's in-memory)

The loading screen changes from "Connecting to server…" to "Loading database…"

Replace the `useEffect` for server status:
```ts
useEffect(() => {
  initDb().then(() => setDbReady(true));
}, []);
```

Replace search handler:
```ts
const handleSearch = useCallback((query: string, lang: "jp" | "en" | "both") => {
  setLoading(true);
  const result = search(query, lang, 0, 100);
  // Map result.entries to SearchResponse format for existing components
  setSearchResult(mapToSearchResponse(result));
  setLoading(false);
}, []);
```

Replace arc/chapter/entries fetches with direct calls to `listArcs()`, `getArcChapters()`, `getEntries()`.

Replace annotation save:
```ts
const handleSaveAnnotation = useCallback((data: Partial<Annotation>) => {
  if (!selectedEntry) return;
  const key = getAnnotationKey(selectedEntry);
  const updated = saveAnnotation(key, data);
  setAnnotations(updated);
}, [selectedEntry]);
```

- [ ] **Step 3: Update DetailPanel.tsx**

Remove props: `hasFurigana`, `furiganaLoading`, `onRequestFurigana`
Remove furigana rendering logic.
Keep: entry display, annotation notes/edit.

- [ ] **Step 4: Update KWICResults.tsx**

Remove props: `hasFurigana`, `onRequestFurigana`

- [ ] **Step 5: Add mapping helpers in App.tsx**

The db.ts returns `EntryRow` objects. Existing components expect `SearchHit`, `ArcEntry`, etc. Add thin mappers:

```ts
function entryRowToArcEntry(row: EntryRow): ArcEntry {
  return {
    file: row.filename,
    index: row.entry_index,
    messageId: row.message_id,
    speakerJPN: row.speaker_jpn,
    speakerENG: row.speaker_eng,
    textJPN: row.text_jpn,
    textENG: row.text_eng,
    textENGNew: row.text_eng_new,
    significantChanges: row.significant_changes === 1,
    changeReason: row.change_reason,
    significance: row.significance,
  };
}
```

- [ ] **Step 6: Run tests and verify**

```bash
npm test
npm run build:db
npm run dev
```

Manually verify: search works, arc browser works, annotations persist in localStorage.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: replace server API with client-side SQLite queries"
```

---

### Task 5: GitHub Pages setup

**Files:**
- Modify: `vite.config.ts` (if base path needed)
- Modify: `package.json` (add deploy script)

- [ ] **Step 1: Decide on base path**

If deploying to `https://nick-freitas.github.io/higurashi-reserach-archives/`, set `base` in vite config:

```ts
export default defineConfig({
  base: "/higurashi-reserach-archives/",
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

Update the DB fetch URL in `src/db.ts` to use `import.meta.env.BASE_URL`:

```ts
const response = await fetch(`${import.meta.env.BASE_URL}higurashi.db`);
```

- [ ] **Step 2: Update sql.js WASM locator**

The WASM file should be served locally rather than from a CDN for reliability. Copy it during build or reference from node_modules:

```ts
const SQL = await initSqlJs({
  locateFile: (file: string) => `${import.meta.env.BASE_URL}${file}`,
});
```

Add a copy step to `package.json`:
```json
"build": "npm run build:db && cp node_modules/sql.js/dist/sql-wasm.wasm public/ && tsc -b && vite build"
```

- [ ] **Step 3: Add GitHub Actions workflow**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build:db
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Note: The GitHub Actions build needs `game_text/` data. Options:
- Store it in a separate private repo/artifact and pull during CI
- Or check it in (undo the gitignore) — it's 80MB which is within GitHub's limits
- Or build locally and push the `dist/` folder

This decision is up to you — we can adjust the workflow accordingly.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add GitHub Pages deployment config"
```

---

### Task 6: Final cleanup and README update

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `package.json` (name field)

- [ ] **Step 1: Update package.json name**

```json
"name": "higurashi-archives"
```

- [ ] **Step 2: Update README**

Update Getting Started to reflect new workflow:
```
npm install
npm run build:db    # Pre-process game text into SQLite (requires game_text/ directory)
npm run dev
```

Remove server references. Update project structure to remove `server/`, `data/`.

- [ ] **Step 3: Update CLAUDE.md**

Remove server references. Update structure to reflect static architecture.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: update README and CLAUDE.md for static SQLite architecture"
```
