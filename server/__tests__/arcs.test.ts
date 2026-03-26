import { describe, it, expect, beforeAll } from "vitest";
import { buildIndex, type CorpusIndex } from "../indexer";
import { listArcs, getArcEntries } from "../arcs";

let index: CorpusIndex;

beforeAll(() => {
  index = buildIndex("..");
});

describe("listArcs", () => {
  it("returns a non-empty array of arcs", () => {
    const arcs = listArcs(index);
    expect(arcs.length).toBeGreaterThan(0);
  });

  it("each arc has id, name, and entryCount > 0", () => {
    const arcs = listArcs(index);
    for (const arc of arcs) {
      expect(arc.id).toBeTruthy();
      expect(arc.name).toBeTruthy();
      expect(arc.entryCount).toBeGreaterThan(0);
    }
  });

  it("includes known arc types", () => {
    const arcs = listArcs(index);
    const ids = arcs.map((a) => a.id);
    expect(ids).toContain("onikakushi");
    expect(ids).toContain("tips");
    expect(ids).toContain("common");
  });

  it("splits miotsukushi into omote and ura", () => {
    const arcs = listArcs(index);
    const ids = arcs.map((a) => a.id);
    expect(ids).toContain("miotsukushi_omote");
    expect(ids).toContain("miotsukushi_ura");
  });

  it("groups fragments by letter prefix", () => {
    const arcs = listArcs(index);
    const fragmentArcs = arcs.filter((a) => a.id.startsWith("fragment_"));
    expect(fragmentArcs.length).toBeGreaterThan(0);
    for (const f of fragmentArcs) {
      expect(f.id).toMatch(/^fragment_[a-z]$/);
    }
  });

  it("total entryCount across all arcs equals index.entries.length", () => {
    const arcs = listArcs(index);
    const totalEntries = arcs.reduce((sum, a) => sum + a.entryCount, 0);
    expect(totalEntries).toBe(index.entries.length);
  });
});

describe("getArcEntries", () => {
  it("returns paginated entries for a known arc", () => {
    const result = getArcEntries(index, "onikakushi", 0, 50);
    expect(result).not.toBeNull();
    expect(result!.entries.length).toBeLessThanOrEqual(50);
    expect(result!.entries.length).toBeGreaterThan(0);
    expect(result!.totalEntries).toBeGreaterThan(0);
  });

  it("returns null for unknown arc", () => {
    const result = getArcEntries(index, "nonexistent_arc", 0, 50);
    expect(result).toBeNull();
  });

  it("respects offset and limit", () => {
    const page1 = getArcEntries(index, "onikakushi", 0, 10);
    const page2 = getArcEntries(index, "onikakushi", 10, 10);
    expect(page1).not.toBeNull();
    expect(page2).not.toBeNull();
    const keys1 = page1!.entries.map((e) => `${e.file}:${e.index}`);
    const keys2 = page2!.entries.map((e) => `${e.file}:${e.index}`);
    expect(keys1).not.toEqual(keys2);
  });

  it("entries are in file order", () => {
    const result = getArcEntries(index, "onikakushi", 0, 500);
    expect(result).not.toBeNull();
    const files = result!.entries.map((e) => e.file);
    const uniqueFiles = [...new Set(files)];
    let lastFileIdx = -1;
    for (const file of files) {
      const idx = uniqueFiles.indexOf(file);
      expect(idx).toBeGreaterThanOrEqual(lastFileIdx);
      lastFileIdx = idx;
    }
  });

  it("returns correct arc metadata", () => {
    const result = getArcEntries(index, "tips", 0, 5);
    expect(result).not.toBeNull();
    expect(result!.arcId).toBe("tips");
    expect(result!.arcName).toBe("Tips");
  });
});
