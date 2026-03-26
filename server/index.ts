import express from "express";
import * as fs from "fs";
import * as path from "path";
import { buildIndex } from "./indexer";
import { search } from "./search";
import type { CorpusIndex } from "./indexer";
import { listArcs, getArcEntries, getArcChapters, getSignificantChanges, getFilteredEntries } from "./arcs";

const app = express();
app.use(express.json());

const CORPUS_DIR = path.resolve(import.meta.dirname, "../game_text");
const ANNOTATIONS_PATH = path.resolve(import.meta.dirname, "../data/annotations.json");

// Build index at startup
console.log(`Loading corpus from ${CORPUS_DIR}...`);
const startTime = Date.now();
const index: CorpusIndex = buildIndex(CORPUS_DIR);
console.log(`Index built in ${Date.now() - startTime}ms`);

// Annotations helpers
function readAnnotations(): Record<string, unknown> {
  if (!fs.existsSync(ANNOTATIONS_PATH)) return {};
  return JSON.parse(fs.readFileSync(ANNOTATIONS_PATH, "utf-8"));
}

function writeAnnotations(data: Record<string, unknown>): void {
  fs.writeFileSync(ANNOTATIONS_PATH, JSON.stringify(data, null, 2));
}

// Search endpoint
app.get("/api/search", (req, res) => {
  const q = (req.query.q as string) ?? "";
  const lang = (req.query.lang as "jp" | "en" | "both") ?? "both";
  const offset = parseInt((req.query.offset as string) ?? "0", 10);
  const limit = parseInt((req.query.limit as string) ?? "100", 10);

  const result = search(index, q, lang, offset, Math.min(limit, 500));
  res.json(result);
});

// Arc browser endpoints
app.get("/api/arcs", (req, res) => {
  const significantOnly = req.query.significantOnly === "true";
  const scoresParam = req.query.scores as string | undefined;
  const scores = scoresParam ? new Set(scoresParam.split(",").map(Number)) : undefined;
  res.json({ arcs: listArcs(index, significantOnly || undefined, scores) });
});

app.get("/api/arc/:arcId/chapters", (req, res) => {
  const significantOnly = req.query.significantOnly === "true";
  const scoresParam = req.query.scores as string | undefined;
  const scores = scoresParam ? new Set(scoresParam.split(",").map(Number)) : undefined;
  const chapters = getArcChapters(index, req.params.arcId, significantOnly || undefined, scores);
  res.json({ arcId: req.params.arcId, chapters: chapters ?? [] });
});

app.get("/api/arc/:arcId", (req, res) => {
  const arcId = req.params.arcId;
  const offset = parseInt((req.query.offset as string) ?? "0", 10);
  const limit = parseInt((req.query.limit as string) ?? "50", 10);
  const file = (req.query.file as string) || undefined;
  const speaker = (req.query.speaker as string) || undefined;

  const result = getArcEntries(index, arcId, offset, Math.min(limit, 500), file, speaker);
  if (!result) {
    res.status(404).json({ error: `Arc "${arcId}" not found` });
    return;
  }
  res.json(result);
});

// Speakers endpoint — list all unique speakers with counts
app.get("/api/speakers", (_req, res) => {
  const counts = new Map<string, number>();
  for (const entry of index.entries) {
    const speaker = entry.speakerENG || entry.speakerJPN;
    if (speaker) {
      counts.set(speaker, (counts.get(speaker) ?? 0) + 1);
    }
  }
  const speakers = Array.from(counts.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
  res.json({ speakers });
});

// General entries endpoint with optional filters
app.get("/api/entries", (req, res) => {
  const offset = parseInt((req.query.offset as string) ?? "0", 10);
  const limit = parseInt((req.query.limit as string) ?? "50", 10);
  const speaker = (req.query.speaker as string) || undefined;
  const arcId = (req.query.arc as string) || undefined;
  const file = (req.query.file as string) || undefined;
  const bookArcs = req.query.bookArcs as string | undefined;
  const bookArcIds = bookArcs ? bookArcs.split(",") : undefined;

  const significantOnly = req.query.significantOnly === "true";
  const scoresParam = req.query.scores as string | undefined;
  const scores = scoresParam ? new Set(scoresParam.split(",").map(Number)) : undefined;
  const result = getFilteredEntries(
    index,
    { bookArcIds, arcId, file, speaker, significantOnly: significantOnly || undefined, scores },
    offset,
    Math.min(limit, 500),
  );
  res.json(result);
});

// Context entries endpoint — returns entries around a given entry
app.get("/api/context", (req, res) => {
  const file = req.query.file as string;
  const idx = parseInt(req.query.index as string, 10);
  const radius = parseInt((req.query.radius as string) ?? "2", 10);
  if (!file || isNaN(idx)) {
    res.status(400).json({ error: "file and index are required" });
    return;
  }

  const fileEntries = index.entries.filter((e) => e.filename === file);
  // Find position of the target entry in the file
  const pos = fileEntries.findIndex((e) => e.entryIndex === idx);
  if (pos === -1) {
    res.json({ entries: [], targetIndex: idx });
    return;
  }

  const start = Math.max(0, pos - radius);
  const end = Math.min(fileEntries.length, pos + radius + 1);
  const context = fileEntries.slice(start, end).map((e) => ({
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

  res.json({ entries: context, targetIndex: idx });
});

// Significant changes endpoint
app.get("/api/significant-changes", (_req, res) => {
  res.json({ entries: getSignificantChanges(index) });
});

// Furigana endpoint
app.post("/api/furigana", async (req, res) => {
  const { text, key } = req.body as { text: string; key?: string };
  if (!text) {
    res.status(400).json({ error: "text is required" });
    return;
  }

  try {
    const { query } = await import("@anthropic-ai/claude-agent-sdk");
    let result = "";
    for await (const message of query({
      prompt: `Add furigana readings to this Japanese text using [漢字]{かんじ} bracket notation. Only annotate kanji compounds — do not annotate hiragana, katakana, or punctuation. Return ONLY the annotated text, nothing else.\n\n${text}`,
      options: {
        maxTurns: 1,
        permissionMode: "acceptEdits",
        systemPrompt:
          "You are a Japanese language specialist. Add furigana readings using [漢字]{かんじ} bracket notation. Only annotate kanji — not hiragana, katakana, or punctuation. Return only the annotated text.",
      },
    })) {
      if (message.type === "result" && "result" in message) {
        result = (message as { result: string }).result;
      }
    }

    const annotated = result || text;

    // Cache in annotations if key provided
    if (key) {
      const annotations = readAnnotations();
      const existing = (annotations[key] as Record<string, string>) ?? {};
      existing.furiganaJPN = annotated;
      annotations[key] = existing;
      writeAnnotations(annotations);
    }

    res.json({ annotated });
  } catch (err) {
    console.error("Furigana API error:", err);
    res.status(500).json({ error: "Failed to generate furigana" });
  }
});

// Annotations CRUD
app.get("/api/annotations", (_req, res) => {
  res.json(readAnnotations());
});

app.patch("/api/annotations/:key", (req, res) => {
  const annotations = readAnnotations();
  const existing = (annotations[req.params.key] as Record<string, string>) ?? {};
  Object.assign(existing, req.body);
  annotations[req.params.key] = existing;
  writeAnnotations(annotations);
  res.json(existing);
});

// Status endpoint (for checking if index is ready)
app.get("/api/status", (_req, res) => {
  res.json({
    ready: true,
    entries: index.entries.length,
    files: index.filenames.length,
    hasFurigana: true,
  });
});

const PORT = parseInt(process.env.PORT ?? "4738", 10);
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
