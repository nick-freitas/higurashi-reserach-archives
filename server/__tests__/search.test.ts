import { describe, it, expect, beforeAll } from "vitest";
import { search } from "../search";
import { buildIndex, type CorpusIndex } from "../indexer";

let index: CorpusIndex;

beforeAll(() => {
  index = buildIndex("..");
});

describe("search", () => {
  it("finds Japanese text matches", () => {
    const result = search(index, "嘘", "jp", 0, 10);
    expect(result.totalHits).toBeGreaterThan(0);
    expect(result.groups.length).toBeGreaterThan(0);
    for (const group of result.groups) {
      for (const hit of group.hits) {
        expect(hit.textJPN.includes("嘘")).toBe(true);
      }
    }
  });

  it("finds English text matches", () => {
    const result = search(index, "lying", "en", 0, 10);
    expect(result.totalHits).toBeGreaterThan(0);
    for (const group of result.groups) {
      for (const hit of group.hits) {
        expect(hit.textENG.toLowerCase().includes("lying")).toBe(true);
      }
    }
  });

  it("searches both languages", () => {
    const result = search(index, "Rena", "both", 0, 10);
    expect(result.totalHits).toBeGreaterThan(0);
  });

  it("returns correct matchOffset and matchLength", () => {
    const result = search(index, "嘘", "jp", 0, 5);
    const hit = result.groups[0]?.hits[0];
    expect(hit).toBeDefined();
    expect(hit.textJPN.substring(hit.matchOffset, hit.matchOffset + hit.matchLength)).toBe("嘘");
  });

  it("respects offset and limit", () => {
    const all = search(index, "の", "jp", 0, 1000);
    const page1 = search(index, "の", "jp", 0, 10);
    const page2 = search(index, "の", "jp", 10, 10);
    expect(page1.totalHits).toBe(all.totalHits);
    expect(page1.groups.flatMap((g) => g.hits).length).toBeLessThanOrEqual(10);
    const toKey = (g: { filename: string; hits: { entryIndex: number }[] }) =>
      g.hits.map((h) => `${g.filename}:${h.entryIndex}`);
    const keys1 = page1.groups.flatMap(toKey);
    const keys2 = page2.groups.flatMap(toKey);
    expect(keys1).not.toEqual(keys2);
  });

  it("returns empty results for no match", () => {
    const result = search(index, "xyzzy_no_match_ever", "both", 0, 100);
    expect(result.totalHits).toBe(0);
    expect(result.groups).toEqual([]);
  });

  it("groups results by filename", () => {
    const result = search(index, "嘘", "jp", 0, 1000);
    const filenames = result.groups.map((g) => g.filename);
    expect(new Set(filenames).size).toBe(filenames.length);
  });
});
