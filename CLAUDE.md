# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Higurashi Archives is a research and analysis tool for studying translation nuances between the original Japanese text of "Higurashi: When They Cry" (07th Expansion) and the community-created English translation from the HigurashiENX project.

## Architecture

Fully static React app — no server. Data is stored in a SQLite database queried client-side via sql.js (WASM).

**Build pipeline:**
1. Clone upstream [HigurashiENX-texts](https://github.com/masagrator/HigurashiENX-texts) repo
2. `scripts/merge-and-build.ts` merges upstream JSON with our `overlays/` data
3. Produces `public/higurashi.db` (SQLite with FTS5 full-text search)
4. Vite builds the React frontend
5. Deployed to GitHub Pages as static files

## Repository Structure

- **src/** — React frontend (components, types, db.ts query layer)
- **scripts/** — TypeScript build scripts (merge-and-build, extract-overlays, classifier, strip-tags)
- **overlays/** — Our analysis data: new translations, significance scores, change reasons (one JSON per source file)
- **py_scripts/** — Python translation and scoring scripts
- **tests/** — Test files
- **public/** — Static assets (generated DB and WASM at build time, gitignored)

## Data Model

**Upstream source** (not in this repo): 721 JSON files with bilingual dialogue entries (MSGSET, LOGSET, SAVEINFO types).

**Overlays** (in this repo): Per-file JSON arrays keyed by array index + MessageID, containing:
- `TextENGNew` / `ENGNew` — our revised English translations
- `significantChanges` — boolean flag for notable translation differences
- `changeReason` — explanation of why the change matters
- `changeScore` — 1-5 significance rating

**SQLite schema** (generated at build time):
- `entries` table — fully denormalized with arc_id, arc_name, chapter_name pre-computed
- `entries_fts` — FTS5 virtual table for full-text search over Japanese and English text

## Higurashi Narrative Structure

The story consists of multiple **arcs** (episodes). The same core cast appears across arcs, but arcs do not necessarily share continuity:

- **Connected arcs** — same timeline with events carrying over
- **"What if" arcs** — alternative scenarios with different outcomes
- **Answer arcs** — reveal truths about earlier "question" arcs

A character may behave very differently between arcs. When analyzing content, always consider which arc it comes from.

## Key Commands

```bash
npm run dev           # Start Vite dev server
npm run build:db      # Build SQLite from upstream + overlays (needs SOURCE_DIR)
npm run build         # Full build (WASM + DB + frontend)
npm test              # Run vitest
```
