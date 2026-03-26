import initSqlJs, { type Database } from "sql.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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

export interface Annotation {
  editedENG?: string;
  notes?: string;
}

export type AnnotationsMap = Record<string, Annotation>;

// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let db: Database | null = null;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ANNOTATIONS_KEY = "higurashi-annotations";

/** Run a read-only query and return all rows typed as T. */
function all<T>(sql: string, params: Record<string, unknown> = {}): T[] {
  if (!db) throw new Error("Database not initialised — call initDb() first");
  const stmt = db.prepare(sql);
  stmt.bind(
    Object.fromEntries(
      Object.entries(params).map(([k, v]) => {
        if (v instanceof Set) throw new Error("Cannot bind a Set directly");
        return [k, v as string | number | null];
      }),
    ),
  );
  const rows: T[] = [];
  while (stmt.step()) {
    rows.push(stmt.getAsObject() as T);
  }
  stmt.free();
  return rows;
}

/** Run a scalar query and return the single value. */
function scalar<T = number>(sql: string, params: Record<string, unknown> = {}): T {
  if (!db) throw new Error("Database not initialised — call initDb() first");
  const stmt = db.prepare(sql);
  stmt.bind(
    Object.fromEntries(
      Object.entries(params).map(([k, v]) => [k, v as string | number | null]),
    ),
  );
  stmt.step();
  const row = stmt.getAsObject();
  stmt.free();
  const keys = Object.keys(row);
  return row[keys[0]] as T;
}

// ---------------------------------------------------------------------------
// Build WHERE helpers for significance / score filtering
// ---------------------------------------------------------------------------

interface FilterClause {
  where: string;
  params: Record<string, unknown>;
}

function significanceFilter(
  significantOnly?: boolean,
  scores?: Set<number>,
  prefix = "",
): FilterClause {
  const clauses: string[] = [];
  const params: Record<string, unknown> = {};
  const col = prefix ? `${prefix}.significant_changes` : "significant_changes";
  const sigCol = prefix ? `${prefix}.significance` : "significance";

  if (significantOnly) {
    clauses.push(`${col} = 1`);
  }
  if (scores && scores.size > 0) {
    const placeholders = [...scores].map((s, i) => {
      const key = `:score${i}`;
      params[key] = s;
      return key;
    });
    clauses.push(`${sigCol} IN (${placeholders.join(", ")})`);
  }

  return {
    where: clauses.length > 0 ? clauses.join(" AND ") : "",
    params,
  };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Initialise sql.js, fetch the database file, and open it in memory.
 * Call once on app mount.
 */
export async function initDb(): Promise<void> {
  const SQL = await initSqlJs({
    locateFile: (file: string) => `${import.meta.env.BASE_URL}${file}`,
  });
  const response = await fetch(`${import.meta.env.BASE_URL}higurashi.db`);
  if (!response.ok) {
    throw new Error(`Failed to fetch database: ${response.status} ${response.statusText}`);
  }
  const buffer = await response.arrayBuffer();
  db = new SQL.Database(new Uint8Array(buffer));
}

/** Quick status summary. */
export function getStatus(): { entries: number; files: number } {
  const entries = scalar<number>("SELECT COUNT(*) AS c FROM entries");
  const files = scalar<number>("SELECT COUNT(DISTINCT filename) AS c FROM entries");
  return { entries, files };
}

/** List all arcs with entry counts, optionally filtered. */
export function listArcs(significantOnly?: boolean, scores?: Set<number>): ArcInfo[] {
  const f = significanceFilter(significantOnly, scores);
  const where = f.where ? `WHERE ${f.where}` : "";

  return all<ArcInfo>(
    `SELECT arc_id AS id, arc_name AS name, COUNT(*) AS entryCount
     FROM entries ${where}
     GROUP BY arc_id
     ORDER BY arc_name`,
    f.params,
  );
}

/** List chapters (files) within an arc. */
export function getArcChapters(
  arcId: string,
  significantOnly?: boolean,
  scores?: Set<number>,
): ChapterInfo[] {
  const f = significanceFilter(significantOnly, scores);
  const where = f.where ? `AND ${f.where}` : "";

  return all<ChapterInfo>(
    `SELECT filename AS file,
            COALESCE(chapter_name, filename) AS name,
            COUNT(*) AS entryCount
     FROM entries
     WHERE arc_id = :arcId ${where}
     GROUP BY filename
     ORDER BY filename`,
    { ":arcId": arcId, ...f.params },
  );
}

/** Fetch entries with flexible filtering and pagination. */
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
  const clauses: string[] = [];
  const params: Record<string, unknown> = {};

  if (options.arcId) {
    clauses.push("arc_id = :arcId");
    params[":arcId"] = options.arcId;
  }
  if (options.file) {
    clauses.push("filename = :file");
    params[":file"] = options.file;
  }
  if (options.speaker) {
    clauses.push("(speaker_eng = :speaker OR speaker_jpn = :speaker)");
    params[":speaker"] = options.speaker;
  }
  if (options.bookArcIds && options.bookArcIds.length > 0) {
    const placeholders = options.bookArcIds.map((id, i) => {
      const key = `:bookArc${i}`;
      params[key] = id;
      return key;
    });
    clauses.push(`arc_id IN (${placeholders.join(", ")})`);
  }

  const f = significanceFilter(options.significantOnly, options.scores);
  if (f.where) {
    clauses.push(f.where);
    Object.assign(params, f.params);
  }

  const where = clauses.length > 0 ? `WHERE ${clauses.join(" AND ")}` : "";
  const limit = options.limit ?? 100;
  const offset = options.offset ?? 0;

  const total = scalar<number>(`SELECT COUNT(*) AS c FROM entries ${where}`, params);
  const entries = all<EntryRow>(
    `SELECT * FROM entries ${where}
     ORDER BY filename, entry_index
     LIMIT :limit OFFSET :offset`,
    { ...params, ":limit": limit, ":offset": offset },
  );

  return { entries, total };
}

/**
 * Full-text search across entries.
 *
 * - Japanese: uses LIKE since FTS5 tokenises on whitespace (no spaces in JP)
 * - English: uses FTS5 MATCH for proper token matching
 * - "both": combines both approaches
 */
export function search(
  query: string,
  lang: "jp" | "en" | "both",
  offset = 0,
  limit = 100,
): { entries: EntryRow[]; total: number; query: string } {
  if (!query.trim()) return { entries: [], total: 0, query };

  const params: Record<string, unknown> = {};
  let countSql: string;
  let selectSql: string;

  if (lang === "jp") {
    params[":q"] = `%${query}%`;
    const where = "WHERE text_jpn LIKE :q";
    countSql = `SELECT COUNT(*) AS c FROM entries ${where}`;
    selectSql = `SELECT * FROM entries ${where} ORDER BY filename, entry_index LIMIT :limit OFFSET :offset`;
  } else if (lang === "en") {
    // FTS5 match — wrap in double quotes for phrase matching
    params[":fts"] = `"${query.replace(/"/g, '""')}"`;
    const from = `entries_fts(:fts) AS fts JOIN entries ON entries.id = fts.rowid`;
    countSql = `SELECT COUNT(*) AS c FROM ${from}`;
    selectSql = `SELECT entries.* FROM ${from} ORDER BY entries.filename, entries.entry_index LIMIT :limit OFFSET :offset`;
  } else {
    // "both" — UNION approach
    params[":q"] = `%${query}%`;
    params[":fts"] = `"${query.replace(/"/g, '""')}"`;

    const jpWhere = "text_jpn LIKE :q";
    const enFrom =
      "entries_fts(:fts) AS fts JOIN entries AS e2 ON e2.id = fts.rowid";

    countSql = `SELECT COUNT(*) AS c FROM (
      SELECT id FROM entries WHERE ${jpWhere}
      UNION
      SELECT e2.id FROM ${enFrom}
    )`;
    selectSql = `SELECT * FROM entries WHERE id IN (
      SELECT id FROM entries WHERE ${jpWhere}
      UNION
      SELECT e2.id FROM ${enFrom}
    ) ORDER BY filename, entry_index LIMIT :limit OFFSET :offset`;
  }

  params[":limit"] = limit;
  params[":offset"] = offset;

  const total = scalar<number>(countSql, params);
  const entries = all<EntryRow>(selectSql, params);

  return { entries, total, query };
}

/** Get entries surrounding a specific entry for context. */
export function getContext(filename: string, entryIndex: number, radius = 10): EntryRow[] {
  return all<EntryRow>(
    `SELECT * FROM entries
     WHERE filename = :filename
       AND entry_index BETWEEN :lo AND :hi
     ORDER BY entry_index`,
    {
      ":filename": filename,
      ":lo": entryIndex - radius,
      ":hi": entryIndex + radius,
    },
  );
}

/** Get all distinct speakers with entry counts. */
export function getSpeakers(): Speaker[] {
  return all<Speaker>(
    `SELECT speaker_eng AS name, COUNT(*) AS count
     FROM entries
     WHERE speaker_eng IS NOT NULL AND speaker_eng != ''
     GROUP BY speaker_eng
     ORDER BY count DESC`,
  );
}

// ---------------------------------------------------------------------------
// Annotations — localStorage
// ---------------------------------------------------------------------------

/** Load all annotations from localStorage. */
export function loadAnnotations(): AnnotationsMap {
  try {
    const raw = localStorage.getItem(ANNOTATIONS_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as AnnotationsMap;
  } catch {
    return {};
  }
}

/** Save / merge a single annotation and return the updated map. */
export function saveAnnotation(key: string, data: Partial<Annotation>): AnnotationsMap {
  const map = loadAnnotations();
  map[key] = { ...map[key], ...data };
  localStorage.setItem(ANNOTATIONS_KEY, JSON.stringify(map));
  return map;
}
