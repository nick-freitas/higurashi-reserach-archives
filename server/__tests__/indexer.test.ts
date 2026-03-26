import { describe, it, expect } from "vitest";
import { parseEntry, buildIndex } from "../indexer";

describe("parseEntry", () => {
  it("parses a MSGSET entry", () => {
    const entry = {
      type: "MSGSET",
      MessageID: 31784,
      NamesJPN: "レナ",
      NamesENG: "Rena",
      PreTextTags: "@vS01/01/120100001.",
      TextJPN: "だから、@k嘘は言ってないよ。",
      TextENG: "``That's why, I wasn't lying.``",
    };
    const result = parseEntry(entry, 5, "onikakushi_05.json");
    expect(result).toEqual({
      entryIndex: 5,
      filename: "onikakushi_05.json",
      source: { type: "arc", arc: "onikakushi", chapter: "05" },
      messageId: 31784,
      speakerJPN: "レナ",
      speakerENG: "Rena",
      textJPN: "だから、嘘は言ってないよ。",
      textENG: "That's why, I wasn't lying.",
      textENGNew: null,
      significantChanges: false,
      changeReason: null,
      significance: null,
    });
  });

  it("parses a LOGSET entry (no MessageID)", () => {
    const entry = {
      type: "LOGSET",
      NamesJPN: "圭一",
      NamesENG: "Keiichi",
      TextJPN: "テスト",
      TextENG: "Test",
    };
    const result = parseEntry(entry, 10, "matsuribayashi_13.json");
    expect(result?.messageId).toBeNull();
    expect(result?.speakerENG).toBe("Keiichi");
  });

  it("parses a SAVEINFO entry", () => {
    const entry = {
      type: "SAVEINFO",
      category: 0,
      JPN: "鬼隠し編",
      ENG: "Onikakushi",
    };
    const result = parseEntry(entry, 0, "onikakushi_01.json");
    expect(result?.textJPN).toBe("鬼隠し編");
    expect(result?.textENG).toBe("Onikakushi");
    expect(result?.speakerJPN).toBeNull();
  });

  it("skips SELECT entries", () => {
    const entry = {
      type: "SELECT",
      metadata: "64s",
      count: 2,
      titleJPN: "選択",
      titleENG: "Choose",
    };
    const result = parseEntry(entry, 3, "onikakushi_01.json");
    expect(result).toBeNull();
  });

  it("parses narration (no speaker)", () => {
    const entry = {
      type: "MSGSET",
      MessageID: 100,
      TextJPN: "静かだった。",
      TextENG: "It was quiet.",
    };
    const result = parseEntry(entry, 1, "onikakushi_01.json");
    expect(result?.speakerJPN).toBeNull();
    expect(result?.speakerENG).toBeNull();
  });
});

describe("buildIndex", () => {
  it("loads and indexes JSON files from a directory", () => {
    // This test uses the real corpus — it's an integration test
    const index = buildIndex("../game_text");
    expect(index.entries.length).toBeGreaterThan(100000);
    expect(index.filenames.length).toBeGreaterThan(700);
  });
});
